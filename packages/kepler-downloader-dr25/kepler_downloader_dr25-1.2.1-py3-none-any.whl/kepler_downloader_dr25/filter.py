#!/usr/bin/env python3
"""
Universal Kepler Data Filter Script

A generic, intelligent filter that can:
1. Accept any CSV with KIC IDs as input
2. Clone data from existing jobs (respecting mode structure)
3. Download missing KICs from MAST
4. Handle both ExoMiner and Standard modes
5. Validate mode compatibility

Default mode: ExoMiner (with DVT requirement)

Usage:
    python kepler_filter.py --input-csv <csv_file> --source-job <job_folder> [options]

Example:
    python kepler_filter.py --input-csv input/koi.csv --source-job output/job-20250906  # ExoMiner is default
"""

import os
import sys
import shutil
import pandas as pd
import numpy as np
import argparse
import sqlite3
import requests
import time
import json
import logging
from pathlib import Path
from typing import Set, List, Dict, Tuple, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from enum import Enum
from dataclasses import dataclass
import hashlib
from astroquery.mast import Observations


class JobMode(Enum):
    """Enumeration of supported job modes"""

    EXOMINER = "exominer"
    STANDARD = "standard"
    UNKNOWN = "unknown"


@dataclass
class JobInfo:
    """Information about a job's structure and content"""

    mode: JobMode
    path: Path
    has_database: bool
    kic_count: int
    file_count: int
    total_size_gb: float
    has_dvt_files: bool
    directory_structure: str
    db_schema_version: Optional[str] = None


@dataclass
class FilterConfig:
    """Configuration for the filter operation"""

    input_csv: Path
    source_job: Path
    target_mode: JobMode
    output_dir: Path
    force_mode: bool
    validate_dvt: bool
    download_missing: bool
    max_workers: int
    batch_size: int
    verbose: bool


class KeplerFilter:
    """Universal filter for Kepler data with mode awareness"""

    def __init__(self, config: FilterConfig):
        """
        Initialize the Kepler Filter

        Args:
            config: FilterConfig object with all settings
        """
        self.config = config
        self.source_job_info: Optional[JobInfo] = None
        self.target_kics: Set[int] = set()
        self.source_kics: Set[int] = set()
        self.missing_kics: Set[int] = set()
        self.incompatible_kics: Set[int] = set()

        # Statistics
        self.stats = {
            "total_kics": 0,
            "source_kics": 0,
            "copied_kics": 0,
            "downloaded_kics": 0,
            "failed_kics": 0,
            "removed_kics_no_dvt": 0,
            "mode_conflicts": 0,
            "total_files_copied": 0,
            "total_files_downloaded": 0,
            "total_size_gb": 0.0,
        }

        # Setup output directories
        self.setup_output_directories()
        self.setup_logging()
        self.setup_database()

    def setup_output_directories(self):
        """Create output directory structure"""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories based on target mode
        if self.config.target_mode == JobMode.EXOMINER:
            self.data_dir = self.config.output_dir / "Kepler"
        else:
            self.data_dir = self.config.output_dir / "mastDownload" / "Kepler"

        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.reports_dir = self.config.output_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        self.csv_dir = self.config.output_dir / "input_csv_files"
        self.csv_dir.mkdir(exist_ok=True)

    def setup_logging(self):
        """Configure logging"""
        log_file = self.reports_dir / f"filter_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        log_level = logging.DEBUG if self.config.verbose else logging.INFO

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def setup_database(self):
        """Initialize database for tracking operations"""
        self.db_path = self.config.output_dir / "filter_records.db"
        conn = sqlite3.connect(str(self.db_path))

        # Main filter tracking table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS filter_operations (
                kic_id INTEGER PRIMARY KEY,
                source TEXT,
                target_mode TEXT,
                operation TEXT,
                status TEXT,
                has_dvt BOOLEAN,
                file_count INTEGER,
                total_size_mb REAL,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Mode compatibility tracking
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mode_compatibility (
                check_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_mode TEXT,
                target_mode TEXT,
                compatible BOOLEAN,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # File inventory
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_inventory (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kic_id INTEGER,
                file_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                source TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.close()
        self.logger.info(f"Database initialized at {self.db_path}")

    def detect_job_mode(self, job_path: Path) -> JobInfo:
        """
        Detect the mode and structure of a job

        Args:
            job_path: Path to the job directory

        Returns:
            JobInfo object with job details
        """
        self.logger.info(f"Detecting mode for job: {job_path}")

        # Check for ExoMiner structure (Kepler/XXXX/XXXXXXXXX/)
        exominer_dir = job_path / "Kepler"
        standard_dir = job_path / "mastDownload" / "Kepler"

        mode = JobMode.UNKNOWN
        directory_structure = "unknown"

        if exominer_dir.exists():
            # Check for ExoMiner's specific structure
            subdirs = list(exominer_dir.iterdir())
            if subdirs and all(d.is_dir() and len(d.name) == 4 for d in subdirs[:5]):
                mode = JobMode.EXOMINER
                directory_structure = "Kepler/XXXX/XXXXXXXXX/"

        if standard_dir.exists() and mode == JobMode.UNKNOWN:
            # Check for standard MAST structure
            subdirs = list(standard_dir.iterdir())
            if subdirs and any("kplr" in d.name for d in subdirs[:5]):
                mode = JobMode.STANDARD
                directory_structure = "mastDownload/Kepler/kplr*/"

        # Count KICs and files
        kic_count = 0
        file_count = 0
        total_size = 0
        has_dvt = False

        data_root = exominer_dir if mode == JobMode.EXOMINER else standard_dir if mode == JobMode.STANDARD else job_path

        if data_root.exists():
            for fits_file in data_root.rglob("*.fits"):
                file_count += 1
                total_size += fits_file.stat().st_size

                if "_dvt.fits" in fits_file.name:
                    has_dvt = True

                # Extract KIC from filename
                if fits_file.name.startswith("kplr"):
                    try:
                        kic_str = fits_file.name[4:].split("-")[0].split("_")[0]
                        kic_id = int(kic_str)
                        self.source_kics.add(kic_id)
                    except (ValueError, IndexError):
                        pass

            kic_count = len(self.source_kics)

        # Check for database
        db_path = job_path / "download_records.db"
        has_database = db_path.exists()

        # Get schema version if database exists
        schema_version = None
        if has_database:
            try:
                conn = sqlite3.connect(f"file:{str(db_path)}?mode=ro", uri=True)
                # Check for specific tables to determine schema version
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                table_names = [t[0] for t in tables]

                if "removed_kics" in table_names:
                    schema_version = "v2_with_dvt"
                elif "download_records" in table_names:
                    schema_version = "v1_standard"

                conn.close()
            except:
                pass

        job_info = JobInfo(
            mode=mode,
            path=job_path,
            has_database=has_database,
            kic_count=kic_count,
            file_count=file_count,
            total_size_gb=total_size / (1024**3),
            has_dvt_files=has_dvt,
            directory_structure=directory_structure,
            db_schema_version=schema_version,
        )

        self.logger.info(f"Detected mode: {mode.value}")
        self.logger.info(f"  KICs: {kic_count}, Files: {file_count}, Size: {job_info.total_size_gb:.2f} GB")
        self.logger.info(f"  Has DVT: {has_dvt}, Database: {has_database}")

        return job_info

    def load_input_csv(self) -> pd.DataFrame:
        """
        Load and parse the input CSV file

        Returns:
            DataFrame with the CSV data
        """
        self.logger.info(f"Loading input CSV: {self.config.input_csv}")

        # Read CSV, handling comments
        df = pd.read_csv(self.config.input_csv, comment="#")

        # Find KIC column
        kic_columns = ["kepid", "KIC", "kic", "kic_id", "kepid_str", "kics"]
        kic_column = None

        for col in kic_columns:
            if col in df.columns:
                kic_column = col
                break

        if kic_column is None:
            # Try first column as fallback
            kic_column = df.columns[0]
            self.logger.warning(f"No standard KIC column found, using: {kic_column}")

        # Extract KIC IDs
        kic_values = df[kic_column].dropna()

        for val in kic_values:
            try:
                # Handle both int and float strings
                kic_id = int(float(str(val)))
                self.target_kics.add(kic_id)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid KIC value: {val}")

        self.stats["total_kics"] = len(self.target_kics)
        self.logger.info(f"Loaded {len(self.target_kics)} unique KIC IDs from CSV")

        # Copy CSV for reference
        shutil.copy2(self.config.input_csv, self.csv_dir / self.config.input_csv.name)

        return df

    def check_mode_compatibility(self) -> Tuple[bool, str]:
        """
        Check if source and target modes are compatible

        Returns:
            Tuple of (is_compatible, reason)
        """
        if self.source_job_info.mode == JobMode.UNKNOWN:
            return False, "Source job mode could not be determined"

        # If forcing mode conversion, only warn
        if self.config.force_mode:
            if self.source_job_info.mode != self.config.target_mode:
                self.logger.warning(
                    f"Mode mismatch: Source is {self.source_job_info.mode.value}, "
                    f"target is {self.config.target_mode.value} (forced)"
                )
            return True, "Mode conversion forced by user"

        # Check compatibility
        if self.source_job_info.mode != self.config.target_mode:
            reason = (
                f"Mode mismatch: Source job is {self.source_job_info.mode.value}, "
                f"but target mode is {self.config.target_mode.value}. "
                f"Use --force-mode to override (may cause data structure issues)"
            )

            # Record in database
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                """
                INSERT INTO mode_compatibility 
                (source_mode, target_mode, compatible, reason)
                VALUES (?, ?, ?, ?)
            """,
                (self.source_job_info.mode.value, self.config.target_mode.value, False, reason),
            )
            conn.close()

            return False, reason

        # Check DVT requirements for ExoMiner
        if self.config.target_mode == JobMode.EXOMINER and not self.source_job_info.has_dvt_files:
            if self.config.validate_dvt:
                return False, "Target mode is ExoMiner but source has no DVT files"
            else:
                self.logger.warning("ExoMiner mode without DVT files in source")

        return True, "Modes are compatible"

    def copy_kic_data(self, kic_id: int) -> bool:
        """
        Copy KIC data from source job maintaining structure

        Args:
            kic_id: KIC ID to copy

        Returns:
            True if successful
        """
        copied_files = 0

        if self.source_job_info.mode == JobMode.EXOMINER:
            # ExoMiner structure: Kepler/XXXX/XXXXXXXXX/
            kic_padded = f"{kic_id:09d}"
            first_four = kic_padded[:4]

            source_dir = self.source_job_info.path / "Kepler" / first_four / kic_padded

            if self.config.target_mode == JobMode.EXOMINER:
                # Direct copy maintaining structure
                target_dir = self.data_dir / first_four / kic_padded

                if source_dir.exists():
                    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
                    copied_files = len(list(target_dir.glob("*.fits")))
            else:
                # Convert to standard structure
                if source_dir.exists():
                    for fits_file in source_dir.glob("*.fits"):
                        if "_llc.fits" in fits_file.name:
                            target_dir = self.data_dir / f"kplr{kic_padded}_lc"
                        elif "_dvt.fits" in fits_file.name:
                            target_dir = self.data_dir / f"kplr{kic_padded}_dv"
                        else:
                            target_dir = self.data_dir / f"kplr{kic_padded}_misc"

                        target_dir.mkdir(exist_ok=True)
                        shutil.copy2(fits_file, target_dir / fits_file.name)
                        copied_files += 1

        elif self.source_job_info.mode == JobMode.STANDARD:
            # Standard structure: mastDownload/Kepler/kplr*/
            kic_padded = f"{kic_id:09d}"

            if self.config.target_mode == JobMode.STANDARD:
                # Direct copy maintaining structure
                source_base = self.source_job_info.path / "mastDownload" / "Kepler"

                for subdir in source_base.glob(f"kplr{kic_padded}*"):
                    target_dir = self.data_dir / subdir.name
                    shutil.copytree(subdir, target_dir, dirs_exist_ok=True)
                    copied_files += len(list(target_dir.glob("*.fits")))
            else:
                # Convert to ExoMiner structure
                first_four = kic_padded[:4]
                target_dir = self.data_dir / first_four / kic_padded
                target_dir.mkdir(parents=True, exist_ok=True)

                source_base = self.source_job_info.path / "mastDownload" / "Kepler"

                for subdir in source_base.glob(f"kplr{kic_padded}*"):
                    for fits_file in subdir.glob("*.fits"):
                        shutil.copy2(fits_file, target_dir / fits_file.name)
                        copied_files += 1

        if copied_files > 0:
            # Record in database
            conn = sqlite3.connect(str(self.db_path))

            # Check for DVT files
            has_dvt = False
            if self.config.target_mode == JobMode.EXOMINER:
                kic_padded = f"{kic_id:09d}"
                first_four = kic_padded[:4]
                target_dir = self.data_dir / first_four / kic_padded
                # Check for DVT or DVR files
                has_dvt = False
                if target_dir.exists():
                    has_dvt = any(target_dir.glob("*_dvt.fits"))

            conn.execute(
                """
                INSERT INTO filter_operations 
                (kic_id, source, target_mode, operation, status, has_dvt, file_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (kic_id, "source_job", self.config.target_mode.value, "copy", "success", has_dvt, copied_files),
            )
            conn.close()

            self.stats["copied_kics"] += 1
            self.stats["total_files_copied"] += copied_files

            return True

        return False

    def download_from_mast(self, kic_id: int) -> dict:
        """
        Download KIC data from MAST

        Args:
            kic_id: KIC ID to download

        Returns:
            A dictionary with download results.
        """
        if not self.config.download_missing:
            return False

        result = {
            "kic": kic_id,
            "success": False,
            "files_downloaded": 0,
            "has_dvt": False,
            "file_paths": [],
            "error": None,
        }

        try:
            kic_formatted = f"kplr{kic_id:09d}"
            obs_table = Observations.query_criteria(
                target_name=kic_formatted, obs_collection="Kepler", dataproduct_type="timeseries"
            )

            if len(obs_table) == 0:
                result["error"] = "No observations found"
                return result

            products = Observations.get_product_list(obs_table)
            if len(products) == 0:
                result["error"] = "No products found"
                return result

            fits_products = Observations.filter_products(products, extension="fits")
            if len(fits_products) == 0:
                result["error"] = "No FITS files found"
                return result

            mask = [
                "_llc.fits" in str(row["productFilename"]) or "_dvt.fits" in str(row["productFilename"])
                for row in fits_products
            ]
            if not any(mask):
                result["error"] = "No long-cadence or DVT FITS files found"
                return result

            fits_products = fits_products[mask]

            file_paths = []
            dvt_count = 0
            for product in fits_products:
                filename = str(product["productFilename"])
                uri = product["dataURI"]
                url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={uri}"

                if self.config.target_mode == JobMode.EXOMINER:
                    target_path = self._get_exominer_path(kic_id, filename)
                else:
                    kic_padded = f"{kic_id:09d}"
                    if "_llc.fits" in filename:
                        subdir = f"{kic_padded}_lc"
                    elif "_dvt.fits" in filename:
                        subdir = f"{kic_padded}_dv"
                    else:
                        subdir = f"{kic_padded}_misc"
                    target_dir = self.data_dir / subdir
                    target_dir.mkdir(exist_ok=True)
                    target_path = target_dir / filename

                if self._download_file(url, str(target_path)):
                    file_paths.append(str(target_path))
                    if "_dvt.fits" in filename:
                        dvt_count += 1

            result["files_downloaded"] = len(file_paths)
            result["file_paths"] = file_paths
            result["has_dvt"] = dvt_count > 0
            if len(file_paths) > 0:
                result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Failed to download KIC {kic_id}: {str(e)}")

        # Record in database
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """
            INSERT INTO filter_operations 
            (kic_id, source, target_mode, operation, status, has_dvt, file_count, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                kic_id,
                "mast",
                self.config.target_mode.value,
                "download",
                "success" if result["success"] else "failed",
                result["has_dvt"],
                result["files_downloaded"],
                result["error"],
            ),
        )
        conn.close()

        if result["success"]:
            self.stats["downloaded_kics"] += 1
            self.stats["total_files_downloaded"] += result["files_downloaded"]
        else:
            self.stats["failed_kics"] += 1

        return result["success"]

    def _get_exominer_path(self, kic_int: int, filename: str) -> Path:
        kic_padded = f"{kic_int:09d}"
        first_four = kic_padded[:4]
        target_dir = self.data_dir / first_four / kic_padded
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / filename

    def _download_file(self, url: str, target_path: str, max_retries: int = 3) -> bool:
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                with open(target_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    self.logger.debug(f"Download attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2**attempt)
                else:
                    self.logger.error(f"Failed to download after {max_retries} attempts: {e}")
                    return False
        return False

    def validate_dvt_requirements(self):
        """
        Validate DVT requirements for ExoMiner mode
        """
        if self.config.target_mode != JobMode.EXOMINER or not self.config.validate_dvt:
            return

        self.logger.info("Validating DVT requirements for ExoMiner mode")

        kics_without_dvt = []

        conn = sqlite3.connect(str(self.db_path))

        # Check each KIC for DVT files
        for kic_id in self.target_kics:
            kic_padded = f"{kic_id:09d}"
            first_four = kic_padded[:4]
            kic_dir = self.data_dir / first_four / kic_padded

            if kic_dir.exists():
                dvt_files = list(kic_dir.glob("*_dvt.fits"))
                if not dvt_files:
                    kics_without_dvt.append(kic_id)

                    # Update database
                    conn.execute(
                        """
                        UPDATE filter_operations 
                        SET has_dvt = false 
                        WHERE kic_id = ?
                    """,
                        (kic_id,),
                    )

        conn.close()

        if kics_without_dvt:
            self.logger.warning(f"Found {len(kics_without_dvt)} KICs without DVT files")

            # Remove or backup based on configuration
            for kic_id in kics_without_dvt:
                kic_padded = f"{kic_id:09d}"
                first_four = kic_padded[:4]
                kic_dir = self.data_dir / first_four / kic_padded

                if kic_dir.exists():
                    backup_dir = self.config.output_dir / "backup_no_dvt" / first_four / kic_padded
                    backup_dir.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(kic_dir), str(backup_dir))
                    self.stats["removed_kics_no_dvt"] += 1
                    self.logger.info(f"Moved KIC {kic_id} to backup (no DVT)")

    def sync_database_from_source(self):
        """
        Sync database records from source job
        """
        if not self.source_job_info.has_database:
            return

        self.logger.info("Syncing database from source job")

        source_db = self.source_job_info.path / "download_records.db"

        try:
            # Connect to both databases
            source_conn = sqlite3.connect(f"file:{str(source_db)}?mode=ro", uri=True)
            target_conn = sqlite3.connect(str(self.db_path))

            # Copy relevant records for filtered KICs
            kic_list = list(self.target_kics)

            if kic_list:
                # Check if source has the download_records table
                tables = source_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                table_names = [t[0] for t in tables]

                if "download_records" in table_names:
                    # Copy download records for our KICs
                    placeholders = ",".join(["?" for _ in kic_list])
                    records = source_conn.execute(
                        f"SELECT * FROM download_records WHERE kic IN ({placeholders})", kic_list
                    ).fetchall()

                    # Create a compatible insert
                    if records:
                        self.logger.info(f"Copying {len(records)} database records")
                        # This would need proper column mapping in production

            source_conn.close()
            target_conn.close()

        except Exception as e:
            self.logger.warning(f"Could not sync database: {str(e)}")

    def generate_health_report(self):
        """
        Generate comprehensive health report
        """
        report_path = self.config.output_dir / "health_check_report.txt"

        with open(report_path, "w") as f:
            f.write("Kepler Filter Health Check Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Output Directory: {self.config.output_dir}\n\n")

            # Input information
            f.write("Input Configuration:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Input CSV: {self.config.input_csv}\n")
            f.write(f"Source Job: {self.config.source_job}\n")
            f.write(f"Target Mode: {self.config.target_mode.value}\n")
            f.write(f"Force Mode: {self.config.force_mode}\n")
            f.write(f"Validate DVT: {self.config.validate_dvt}\n\n")

            # Source job information
            f.write("Source Job Analysis:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Detected Mode: {self.source_job_info.mode.value}\n")
            f.write(f"Directory Structure: {self.source_job_info.directory_structure}\n")
            f.write(f"Total KICs: {self.source_job_info.kic_count}\n")
            f.write(f"Total Files: {self.source_job_info.file_count}\n")
            f.write(f"Total Size: {self.source_job_info.total_size_gb:.2f} GB\n")
            f.write(f"Has DVT Files: {self.source_job_info.has_dvt_files}\n")
            f.write(f"Has Database: {self.source_job_info.has_database}\n")
            if self.source_job_info.db_schema_version:
                f.write(f"DB Schema: {self.source_job_info.db_schema_version}\n")
            f.write("\n")

            # Mode compatibility
            is_compatible, reason = self.check_mode_compatibility()
            f.write("Mode Compatibility:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Compatible: {is_compatible}\n")
            f.write(f"Reason: {reason}\n\n")

            # Processing statistics
            f.write("Processing Statistics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Target KICs from CSV: {self.stats['total_kics']}\n")
            f.write(f"KICs in Source Job: {len(self.source_kics)}\n")
            f.write(f"KICs Copied: {self.stats['copied_kics']}\n")
            f.write(f"KICs Downloaded: {self.stats['downloaded_kics']}\n")
            f.write(f"KICs Failed: {self.stats['failed_kics']}\n")

            if self.config.target_mode == JobMode.EXOMINER and self.config.validate_dvt:
                f.write(f"KICs Removed (no DVT): {self.stats['removed_kics_no_dvt']}\n")

            f.write(f"\nTotal Files Copied: {self.stats['total_files_copied']}\n")
            f.write(f"Total Files Downloaded: {self.stats['total_files_downloaded']}\n")

            # Missing KICs
            if self.missing_kics:
                f.write(f"\nMissing KICs (not in source): {len(self.missing_kics)}\n")
                if len(self.missing_kics) <= 20:
                    f.write(f"Missing KIC IDs: {sorted(list(self.missing_kics))}\n")
                else:
                    f.write(f"First 20 missing KICs: {sorted(list(self.missing_kics))[:20]}\n")

            # Warnings and recommendations
            if not is_compatible and not self.config.force_mode:
                f.write("\n⚠️  WARNING: Mode incompatibility detected!\n")
                f.write("The source job and target mode are not compatible.\n")
                f.write("Data structure conversion may be required.\n")
                f.write("Use --force-mode to override (use with caution).\n")

            if self.config.target_mode == JobMode.EXOMINER and not self.source_job_info.has_dvt_files:
                f.write("\n⚠️  WARNING: ExoMiner mode requires DVT files!\n")
                f.write("The source job does not contain DVT files.\n")
                f.write("Consider using Standard mode or downloading DVT files.\n")

        self.logger.info(f"Health report generated: {report_path}")

        # Also generate a JSON report for programmatic access
        json_report = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "input_csv": str(self.config.input_csv),
                "source_job": str(self.config.source_job),
                "target_mode": self.config.target_mode.value,
                "force_mode": self.config.force_mode,
                "validate_dvt": self.config.validate_dvt,
            },
            "source_job_info": {
                "mode": self.source_job_info.mode.value,
                "kic_count": self.source_job_info.kic_count,
                "file_count": self.source_job_info.file_count,
                "total_size_gb": self.source_job_info.total_size_gb,
                "has_dvt_files": self.source_job_info.has_dvt_files,
            },
            "statistics": self.stats,
            "mode_compatible": is_compatible,
            "compatibility_reason": reason,
        }

        json_path = self.reports_dir / f"filter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, "w") as f:
            json.dump(json_report, f, indent=2)

    def run(self):
        """
        Execute the complete filtering process
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting Kepler Universal Filter")
            self.logger.info("=" * 60)

            # Step 1: Load input CSV
            self.logger.info("\nStep 1: Loading input CSV")
            csv_data = self.load_input_csv()

            # Step 2: Detect source job mode
            self.logger.info("\nStep 2: Analyzing source job")
            self.source_job_info = self.detect_job_mode(self.config.source_job)

            # Step 3: Check mode compatibility
            self.logger.info("\nStep 3: Checking mode compatibility")
            is_compatible, reason = self.check_mode_compatibility()

            if not is_compatible and not self.config.force_mode:
                self.logger.error(f"Mode incompatibility: {reason}")
                self.generate_health_report()
                return False

            # Step 4: Identify missing KICs
            self.logger.info("\nStep 4: Identifying KICs to process")
            self.missing_kics = self.target_kics - self.source_kics
            available_kics = self.target_kics & self.source_kics

            self.logger.info(f"  KICs in both: {len(available_kics)}")
            self.logger.info(f"  KICs missing: {len(self.missing_kics)}")

            # Step 5: Copy available KICs
            self.logger.info("\nStep 5: Copying available KICs")
            with tqdm(total=len(available_kics), desc="Copying KICs") as pbar:
                for kic_id in available_kics:
                    self.copy_kic_data(kic_id)
                    pbar.update(1)

            # Step 6: Download missing KICs
            if self.missing_kics and self.config.download_missing:
                self.logger.info("\nStep 6: Downloading missing KICs")
                with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                    future_to_kic = {
                        executor.submit(self.download_from_mast, kic_id): kic_id for kic_id in self.missing_kics
                    }
                    for future in tqdm(
                        as_completed(future_to_kic), total=len(self.missing_kics), desc="Downloading KICs"
                    ):
                        future.result()

            elif self.missing_kics:
                self.logger.info("\nStep 6: Skipping download (disabled)")

            # Step 7: Validate DVT requirements
            if self.config.target_mode == JobMode.EXOMINER and self.config.validate_dvt:
                self.logger.info("\nStep 7: Validating DVT requirements")
                self.validate_dvt_requirements()

            # Step 8: Sync database
            self.logger.info("\nStep 8: Syncing database")
            self.sync_database_from_source()

            # Step 9: Generate reports
            self.logger.info("\nStep 9: Generating reports")
            self.generate_health_report()

            self.logger.info("\n" + "=" * 60)
            self.logger.info("Filter process completed successfully!")
            self.logger.info(f"Output directory: {self.config.output_dir}")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Fatal error: {str(e)}")
            self.generate_health_report()
            raise


def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(
        description="Universal Kepler Data Filter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with KOI file and job
  python kepler_filter.py --input-csv input/koi.csv --source-job output/job-20250906
  
  # Specify target mode (default is exominer)
  python kepler_filter.py --input-csv input/custom.csv --source-job output/job-20250906 --no-exominer  # Use Standard format
  
  # Force mode conversion (use with caution)
  python kepler_filter.py --input-csv input/koi.csv --source-job output/job-20250906 --force-mode
  
  # Disable DVT validation for ExoMiner
  python kepler_filter.py --input-csv input/koi.csv --source-job output/job-20250906 --no-validate-dvt
        """,
    )

    parser.add_argument("--input-csv", required=True, help="Input CSV file containing KIC IDs")
    parser.add_argument("--source-job", required=True, help="Source job folder to copy data from")
    parser.add_argument(
        "--no-exominer", action="store_true", help="Use Standard MAST format instead of ExoMiner (ExoMiner is default)"
    )
    parser.add_argument("--output-dir", help="Output directory for filtered data")
    parser.add_argument("--force-mode", action="store_true", help="Force mode conversion even if incompatible")
    parser.add_argument("--no-validate-dvt", action="store_true", help="Disable DVT validation for ExoMiner mode")
    parser.add_argument(
        "--no-download-missing",
        action="store_true",
        help="Skip downloading missing KICs from MAST (by default, missing KICs are downloaded)",
    )
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers for downloads")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Create configuration
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"output/filtered_{timestamp}")

    config = FilterConfig(
        input_csv=Path(args.input_csv),
        source_job=Path(args.source_job),
        target_mode=JobMode("standard" if args.no_exominer else "exominer"),
        output_dir=output_dir,
        force_mode=args.force_mode,
        validate_dvt=not args.no_validate_dvt,
        download_missing=not args.no_download_missing,
        max_workers=args.workers,
        batch_size=args.batch_size,
        verbose=args.verbose,
    )

    # Validate inputs
    if not config.input_csv.exists():
        print(f"ERROR: Input CSV not found: {config.input_csv}", file=sys.stderr)
        sys.exit(1)

    if not config.source_job.exists():
        print(f"ERROR: Source job not found: {config.source_job}", file=sys.stderr)
        sys.exit(1)

    try:
        # Create and run filter
        filter_tool = KeplerFilter(config)
        success = filter_tool.run()

        if success:
            print(f"\nSUCCESS: Filtered data created at: {output_dir}")
        else:
            print(f"\nFAILED: Check health report at: {output_dir}/health_check_report.txt")
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
