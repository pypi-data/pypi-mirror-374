import os
import glob
import pandas as pd
from astroquery.mast import Observations
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Timer
import json
import sys
import sqlite3
import shutil
import redis
from typing import Dict, List, Any, Tuple, Optional
import pickle  # Note: Only used with trusted internal data, never with user input
import argparse
import requests
from urllib.parse import urlparse
from pathlib import Path
import csv

class FastKeplerDownloader:
    def __init__(self, download_dir: str, job_id: str, max_workers: int = 4, batch_size: int = 50, 
                 redis_host: str = 'localhost', redis_port: int = 6379, redis_db: int = 0, 
                 exominer_format: bool = False, strict_dvt: bool = False, backup_no_dvt: bool = False):
        """
        Enhanced Fast Kepler FITS downloader with DVT filtering for ExoMiner mode.
        
        Args:
            download_dir: Directory to download files to
            job_id: Unique job identifier for this download session
            max_workers: Number of parallel download threads  
            batch_size: Number of KICs to process in each batch
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            exominer_format: If True, organize files in ExoMiner directory structure
            strict_dvt: If True in ExoMiner mode, immediately skip KICs without DVT
            backup_no_dvt: If True, backup KICs without DVT instead of deleting
        """
        # Validate inputs
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        if not job_id:
            raise ValueError("job_id cannot be empty")
        
        self.job_id = job_id
        self.job_dir = os.path.join(download_dir, job_id)
        self.download_dir = os.path.join(self.job_dir, 'mastDownload')
        self.kepler_dir = os.path.join(self.job_dir, 'Kepler') if exominer_format else None
        self.exominer_format = exominer_format
        self.strict_dvt = strict_dvt and exominer_format  # Only apply strict DVT in ExoMiner mode
        self.backup_no_dvt = backup_no_dvt
        self.db_path = os.path.join(self.job_dir, 'download_records.db')
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.lock = Lock()
        
        # Enhanced stats for DVT tracking
        self.stats = {
            'processed': 0,
            'downloaded': 0,
            'errors': 0,
            'start_time': time.time(),
            'kics_with_data': 0,
            'kics_with_dvt': 0,
            'kics_without_dvt': 0,
            'kics_removed_no_dvt': 0,
            'kics_backed_up_no_dvt': 0,
            'total_llc_files': 0,
            'total_dvt_files': 0
        }
        
        # DVT tracking
        self.dvt_status: Dict[int, bool] = {}  # KIC -> has_dvt
        self.removed_kics: List[Dict[str, Any]] = []  # Track removed KICs
        
        # Redis configuration
        self.redis_client = None
        self.redis_config = {'host': redis_host, 'port': redis_port, 'db': redis_db}
        self.redis_keys = {
            'csv_data': f'{job_id}:csv_data',
            'download_records': f'{job_id}:download_records',
            'file_inventory': f'{job_id}:file_inventory',
            'dvt_status': f'{job_id}:dvt_status'  # New key for DVT status
        }
        self.sync_timer = None
        self.sync_interval = 10  # seconds
        self.is_syncing = False
        
        # Create job directory and subdirectories
        os.makedirs(self.job_dir, exist_ok=True)
        if self.exominer_format:
            os.makedirs(self.kepler_dir, exist_ok=True)
            if self.backup_no_dvt:
                self.backup_dir = os.path.join(self.job_dir, 'backup_no_dvt')
                os.makedirs(self.backup_dir, exist_ok=True)
        
        # Reports directory
        self.reports_dir = os.path.join(self.job_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Initialize Redis connection and database
        self._init_redis()
        self._init_database()
        self._start_sync_timer()
    
    def _init_redis(self):
        """Initialize Redis connection with retry logic and clear any existing data for this job."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Security: Configure Redis with connection limits and timeouts
                self.redis_client = redis.Redis(
                    **self.redis_config, 
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    max_connections=50
                )
                # Test connection
                self.redis_client.ping()
                
                # Clear any existing data for this job
                for key in self.redis_keys.values():
                    self.redis_client.delete(key)
                
                logging.info(f"Redis connection established for job {self.job_id}")
                return
                
            except (redis.ConnectionError, redis.TimeoutError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Redis connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logging.warning(f"Could not connect to Redis after {max_retries} attempts. Falling back to direct database writes.")
                    self.redis_client = None
    
    def _init_database(self):
        """Initialize DuckDB database with enhanced schema for DVT tracking."""
        conn = sqlite3.connect(self.db_path)
        
        # Enhanced download_records table with DVT status
        conn.execute("""
            CREATE TABLE IF NOT EXISTS download_records (
                kic INTEGER PRIMARY KEY,
                success BOOLEAN,
                files_downloaded INTEGER,
                llc_files INTEGER,
                dvt_files INTEGER,
                has_dvt BOOLEAN,
                error_message TEXT,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                job_id TEXT,
                file_paths TEXT,
                removal_reason TEXT  -- New field for tracking why KIC was removed
            )
        """)
        
        # File inventory table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_inventory (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kic INTEGER,
                file_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                job_id TEXT
            )
        """)
        
        # CSV import tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS csv_import_records (
                file_name TEXT PRIMARY KEY,
                import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_rows INTEGER,
                unique_kics INTEGER,
                job_id TEXT
            )
        """)
        
        # New table for removed KICs tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS removed_kics (
                kic INTEGER PRIMARY KEY,
                kepoi_name TEXT,
                removal_reason TEXT,
                llc_files_removed INTEGER,
                dvt_files_removed INTEGER,
                total_size_mb_removed REAL,
                removal_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                job_id TEXT
            )
        """)
        
        conn.close()
        logging.info(f"Database initialized with enhanced DVT tracking at {self.db_path}")
    
    def _start_sync_timer(self):
        """Start periodic sync timer for Redis to database."""
        if self.redis_client is not None:
            self.sync_timer = Timer(self.sync_interval, self._periodic_sync)
            self.sync_timer.daemon = True
            self.sync_timer.start()
    
    def _stop_sync_timer(self):
        """Stop the periodic sync timer."""
        if self.sync_timer is not None:
            self.sync_timer.cancel()
    
    def _periodic_sync(self):
        """Periodically sync Redis buffer to database."""
        if not self.is_syncing and self.redis_client is not None:
            self.is_syncing = True
            try:
                self._sync_redis_to_db()
            except Exception as e:
                logging.error(f"Error during periodic sync: {e}")
            finally:
                self.is_syncing = False
                self._start_sync_timer()  # Restart timer for next sync
    
    def _sync_redis_to_db(self):
        """Sync data from Redis buffers to DuckDB database."""
        if self.redis_client is None:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Sync download records
            records_key = self.redis_keys['download_records']
            batch_size = 100
            
            while True:
                # Pop batch of records from Redis list
                records = self.redis_client.lrange(records_key, 0, batch_size - 1)
                if not records:
                    break
                
                # Process records
                for record_data in records:
                    record = json.loads(record_data.decode())
                    
                    # Insert or update with DVT status
                    conn.execute("""
                        INSERT INTO download_records 
                        (kic, success, files_downloaded, llc_files, dvt_files, has_dvt, error_message, job_id, file_paths)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(kic) DO UPDATE SET
                            success = EXCLUDED.success,
                            files_downloaded = EXCLUDED.files_downloaded,
                            llc_files = EXCLUDED.llc_files,
                            dvt_files = EXCLUDED.dvt_files,
                            has_dvt = EXCLUDED.has_dvt,
                            error_message = EXCLUDED.error_message,
                            file_paths = EXCLUDED.file_paths
                    """, (
                        record['kic'],
                        record['success'],
                        record['files_downloaded'],
                        record.get('llc_files', 0),
                        record.get('dvt_files', 0),
                        record.get('has_dvt', record.get('dvt_files', 0) > 0),
                        record.get('error'),
                        self.job_id,
                        json.dumps(record.get('file_paths', []))
                    ))
                
                # Remove processed records from Redis
                self.redis_client.ltrim(records_key, batch_size, -1)
            
            # Sync file inventory
            files_key = self.redis_keys['file_inventory']
            
            while True:
                file_records = self.redis_client.lrange(files_key, 0, batch_size - 1)
                if not file_records:
                    break
                
                for file_data in file_records:
                    file_record = json.loads(file_data.decode())
                    
                    conn.execute("""
                        INSERT INTO file_inventory 
                        (kic, file_type, file_path, file_size, job_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        file_record['kic'],
                        file_record['file_type'],
                        file_record['file_path'],
                        file_record['file_size'],
                        self.job_id
                    ))
                
                self.redis_client.ltrim(files_key, batch_size, -1)
            
            # Sync DVT status
            dvt_key = self.redis_keys['dvt_status']
            dvt_data = self.redis_client.hgetall(dvt_key)
            
            for kic_bytes, has_dvt_bytes in dvt_data.items():
                kic = int(kic_bytes.decode())
                has_dvt = has_dvt_bytes.decode() == 'true'
                self.dvt_status[kic] = has_dvt
            
            # Log sync success before committing
            records_count = conn.execute("SELECT COUNT(*) FROM download_records").fetchone()[0]
            files_count = conn.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0]
            
            # CRITICAL: Commit the transaction before closing
            conn.commit()
            conn.close()
            
            if records_count > 0 or files_count > 0:
                logging.debug(f"Synced to DB: {records_count} download records, {files_count} file inventory items")
            
        except Exception as e:
            logging.error(f"Error syncing Redis to database: {e}")
    
    def download_kic(self, kic: str) -> dict:
        """
        Download FITS files for a single KIC with DVT tracking.
        """
        result = {
            'kic': kic,
            'success': False,
            'files_downloaded': 0,
            'llc_files': 0,
            'dvt_files': 0,
            'has_dvt': False,
            'file_paths': [],
            'error': None
        }
        
        try:
            kic_int = int(kic)
            
            # Query MAST
            kic_formatted = f"kplr{kic_int:09d}"
            logging.debug(f"Querying MAST for KIC {kic} (formatted as {kic_formatted})")
            obs_table = Observations.query_criteria(
                target_name=kic_formatted,
                obs_collection="Kepler",
                dataproduct_type="timeseries"
            )
            
            if len(obs_table) == 0:
                result['error'] = 'No observations found'
                return result
            
            # Get products
            products = Observations.get_product_list(obs_table)
            
            if len(products) == 0:
                result['error'] = 'No products found'
                return result
            
            # Filter for FITS files
            fits_products = Observations.filter_products(products, extension="fits")
            
            if len(fits_products) == 0:
                result['error'] = 'No FITS files found'
                return result
            
            # Filter for long-cadence and DVT files
            mask = []
            has_dvt_files = False
            for row in fits_products:
                filename = str(row['productFilename'])
                is_lc = '_llc.fits' in filename
                is_dvt = '_dvt.fits' in filename
                if is_dvt:
                    has_dvt_files = True
                mask.append(is_lc or is_dvt)
            
            if not any(mask):
                result['error'] = 'No long-cadence or DVT FITS files found'
                return result
            
            # In strict DVT mode for ExoMiner, skip KICs without DVT files early
            if self.strict_dvt and not has_dvt_files:
                result['error'] = 'No DVT files available (required for ExoMiner)'
                logging.info(f"Skipping KIC {kic} - no DVT files available (strict mode)")
                return result
            
            fits_products = fits_products[mask]
            
            logging.debug(f"Found {len(fits_products)} LLC/DVT files for KIC {kic}")
            
            # Download files
            file_paths = []
            llc_count = 0
            dvt_count = 0
            
            for product in fits_products:
                filename = str(product['productFilename'])
                
                # Skip non-LLC/DVT files in ExoMiner mode
                if self.exominer_format and not ('_llc.fits' in filename or '_dvt.fits' in filename):
                    continue
                
                uri = product['dataURI']
                url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri={uri}"
                
                # Determine target path
                if self.exominer_format:
                    target_path = self._get_exominer_path(kic_int, filename)
                else:
                    # Standard MAST directory structure
                    kic_formatted = f"kplr{kic_int:09d}"
                    if '_llc.fits' in filename:
                        subdir = f"{kic_formatted}_lc"
                    elif '_dvt.fits' in filename:
                        subdir = f"{kic_formatted}_dv"
                    else:
                        subdir = f"{kic_formatted}_misc"
                    
                    target_dir = os.path.join(self.download_dir, 'Kepler', subdir)
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(target_dir, filename)
                
                # Check if file already exists
                if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    logging.debug(f"File already exists: {filename}")
                    file_paths.append(target_path)
                    
                    if '_llc.fits' in filename:
                        llc_count += 1
                    elif '_dvt.fits' in filename:
                        dvt_count += 1
                    
                    continue
                
                # Download file
                if self._download_file(url, target_path):
                    file_paths.append(target_path)
                    
                    if '_llc.fits' in filename:
                        llc_count += 1
                    elif '_dvt.fits' in filename:
                        dvt_count += 1
                else:
                    logging.warning(f"Failed to download: {filename}")
            
            result['files_downloaded'] = len(file_paths)
            result['file_paths'] = file_paths
            result['llc_files'] = llc_count
            result['dvt_files'] = dvt_count
            result['has_dvt'] = dvt_count > 0
            
            if len(file_paths) > 0:
                result['success'] = True
                
                # Track DVT status
                self.dvt_status[kic_int] = result['has_dvt']
                
                # Update stats
                with self.lock:
                    self.stats['total_llc_files'] += llc_count
                    self.stats['total_dvt_files'] += dvt_count
                    if result['has_dvt']:
                        self.stats['kics_with_dvt'] += 1
                    else:
                        self.stats['kics_without_dvt'] += 1
                
                # Store DVT status in Redis
                if self.redis_client:
                    self.redis_client.hset(
                        self.redis_keys['dvt_status'], 
                        str(kic_int), 
                        'true' if result['has_dvt'] else 'false'
                    )
            else:
                result['error'] = 'No files downloaded'
                
        except Exception as e:
            result['error'] = str(e)
            logging.error(f"Error downloading KIC {kic}: {e}")
        
        return result
    
    def _get_exominer_path(self, kic_int: int, filename: str) -> str:
        """
        Get the ExoMiner directory path for a given KIC and filename.
        
        ExoMiner format:
        Kepler/
        └── XXXX/           (first 4 digits of 9-digit KIC)
            └── XXXXXXXXX/  (full 9-digit KIC)
                └── *.fits
        """
        # Format KIC to 9 digits with leading zeros
        kic_padded = f"{kic_int:09d}"
        
        # Get first 4 digits for parent directory
        first_four = kic_padded[:4]
        
        # Create target directory structure
        target_dir = os.path.join(self.kepler_dir, first_four, kic_padded)
        os.makedirs(target_dir, exist_ok=True)
        
        # Return full path
        return os.path.join(target_dir, filename)
    
    def _download_file(self, url: str, target_path: str, max_retries: int = 3) -> bool:
        """
        Download a file from a URL to a target path with retry logic.
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(target_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return True
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logging.debug(f"Download attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Failed to download after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def _process_batch(self, kic_batch: list) -> list:
        """Process a batch of KICs in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_kic = {executor.submit(self.download_kic, kic): kic for kic in kic_batch}
            
            for future in as_completed(future_to_kic):
                kic = future_to_kic[future]
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per KIC
                    results.append(result)
                    
                    # Record result
                    self._record_download_result(result)
                    
                    # Update stats
                    with self.lock:
                        self.stats['processed'] += 1
                        if result['success']:
                            self.stats['downloaded'] += result['files_downloaded']
                            if result['files_downloaded'] > 0:
                                self.stats['kics_with_data'] += 1
                        else:
                            self.stats['errors'] += 1
                    
                    # Log progress
                    elapsed = time.time() - self.stats['start_time']
                    rate = self.stats['processed'] / elapsed * 60 if elapsed > 0 else 0
                    status = '✓' if result['success'] else '✗'
                    dvt_status = '+DVT' if result['has_dvt'] else '-DVT'
                    logging.info(f"KIC {kic}: {status} ({result['files_downloaded']} files, {dvt_status}) "
                               f"[{self.stats['processed']} processed, {rate:.1f}/min]")
                    
                except Exception as e:
                    logging.error(f"Error processing KIC {kic}: {e}")
                    with self.lock:
                        self.stats['errors'] += 1
                        self.stats['processed'] += 1
        
        return results
    
    def _record_download_result(self, result: dict):
        """Record download result to Redis buffer or database directly."""
        # Calculate file counts
        file_paths = result.get('file_paths', [])
        llc_count = sum(1 for f in file_paths if '_llc.fits' in f)
        dvt_count = sum(1 for f in file_paths if '_dvt.fits' in f)
        
        # Add DVT status to result
        result['has_dvt'] = dvt_count > 0
        
        if self.redis_client is not None:
            # Buffer in Redis
            self.redis_client.lpush(self.redis_keys['download_records'], json.dumps(result).encode())
            
            # Also record individual file records
            if file_paths:
                for file_path in file_paths:
                    file_type = 'llc' if '_llc.fits' in file_path else 'dvt' if '_dvt.fits' in file_path else 'other'
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    
                    file_record = {
                        'kic': int(result['kic']),
                        'file_type': file_type,
                        'file_path': file_path,
                        'file_size': file_size,
                        'job_id': self.job_id
                    }
                    
                    self.redis_client.lpush(self.redis_keys['file_inventory'], json.dumps(file_record).encode())
        else:
            # Direct database write
            self._record_download_result_direct(result, file_paths, llc_count, dvt_count)
    
    def _record_download_result_direct(self, result: dict, file_paths: list, llc_count: int, dvt_count: int):
        """Direct database write for download results."""
        conn = sqlite3.connect(self.db_path)
        
        # Insert download record with DVT status
        conn.execute("""
            INSERT INTO download_records 
            (kic, success, files_downloaded, llc_files, dvt_files, has_dvt, error_message, job_id, file_paths)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(result['kic']),
            result['success'],
            result['files_downloaded'],
            llc_count,
            dvt_count,
            result.get('has_dvt', dvt_count > 0),
            result.get('error'),
            self.job_id,
            json.dumps(file_paths) if file_paths else None
        ))
        
        # Insert individual file records
        if file_paths:
            for file_path in file_paths:
                file_type = 'llc' if '_llc.fits' in file_path else 'dvt' if '_dvt.fits' in file_path else 'other'
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                conn.execute("""
                    INSERT INTO file_inventory 
                    (kic, file_type, file_path, file_size, job_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(result['kic']),
                    file_type,
                    file_path,
                    file_size,
                    self.job_id
                ))
        
        # CRITICAL: Commit the transaction before closing
        conn.commit()
        conn.close()
    
    def filter_kics_without_dvt(self) -> Tuple[List[int], List[int]]:
        """
        Filter out KICs that don't have DVT files (for ExoMiner mode).
        
        Returns:
            Tuple of (kics_with_dvt, kics_without_dvt)
        """
        if not self.exominer_format:
            logging.info("Not in ExoMiner mode, skipping DVT filtering")
            return [], []
        
        logging.info("Starting DVT filtering for ExoMiner mode...")
        
        # Ensure all data is synced
        if self.redis_client:
            self._sync_redis_to_db()
        
        # Query database for KICs without DVT
        conn = sqlite3.connect(self.db_path)
        
        # Get KICs with DVT
        kics_with_dvt = conn.execute("""
            SELECT DISTINCT kic 
            FROM download_records 
            WHERE has_dvt = true AND success = true
            ORDER BY kic
        """).fetchall()
        kics_with_dvt = [row[0] for row in kics_with_dvt]
        
        # Get KICs without DVT
        kics_without_dvt = conn.execute("""
            SELECT DISTINCT kic 
            FROM download_records 
            WHERE has_dvt = false AND success = true
            ORDER BY kic
        """).fetchall()
        kics_without_dvt = [row[0] for row in kics_without_dvt]
        
        conn.close()
        
        logging.info(f"Found {len(kics_with_dvt)} KICs with DVT files")
        logging.info(f"Found {len(kics_without_dvt)} KICs without DVT files")
        
        return kics_with_dvt, kics_without_dvt
    
    def remove_kics_without_dvt(self) -> int:
        """
        Remove or backup KICs that don't have DVT files (final step for ExoMiner mode).
        
        Returns:
            Number of KICs removed/backed up
        """
        if not self.exominer_format:
            return 0
        
        logging.info("Processing KICs without DVT files for ExoMiner mode...")
        
        kics_with_dvt, kics_without_dvt = self.filter_kics_without_dvt()
        
        if not kics_without_dvt:
            logging.info("All KICs have DVT files, no removal needed")
            return 0
        
        removed_count = 0
        backed_up_count = 0
        
        conn = sqlite3.connect(self.db_path)
        
        for kic in kics_without_dvt:
            kic_padded = f"{kic:09d}"
            first_four = kic_padded[:4]
            kic_dir = os.path.join(self.kepler_dir, first_four, kic_padded)
            
            if not os.path.exists(kic_dir):
                continue
            
            # Get file statistics before removal
            file_stats = self._get_kic_file_stats(kic_dir)
            
            # Record removal in database
            conn.execute("""
                INSERT INTO removed_kics 
                (kic, removal_reason, llc_files_removed, dvt_files_removed, total_size_mb_removed, job_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                kic,
                'No DVT files (required for ExoMiner)',
                file_stats['llc_count'],
                file_stats['dvt_count'],
                file_stats['total_size_mb'],
                self.job_id
            ))
            
            # Update download record
            conn.execute("""
                UPDATE download_records 
                SET removal_reason = 'No DVT files (required for ExoMiner)'
                WHERE kic = ?
            """, (kic,))
            
            # Track removed KIC details
            self.removed_kics.append({
                'kic': kic,
                'reason': 'No DVT files',
                'llc_files': file_stats['llc_count'],
                'size_mb': file_stats['total_size_mb']
            })
            
            if self.backup_no_dvt:
                # Move to backup directory
                backup_path = os.path.join(self.backup_dir, first_four, kic_padded)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.move(kic_dir, backup_path)
                logging.info(f"Backed up KIC {kic} to {backup_path} (no DVT)")
                backed_up_count += 1
            else:
                # Remove directory
                shutil.rmtree(kic_dir)
                logging.info(f"Removed KIC {kic} directory (no DVT)")
                removed_count += 1
        
        # Commit database changes before closing
        conn.commit()
        conn.close()
        
        # Update stats
        with self.lock:
            self.stats['kics_removed_no_dvt'] = removed_count
            self.stats['kics_backed_up_no_dvt'] = backed_up_count
        
        total_processed = removed_count + backed_up_count
        logging.info(f"Processed {total_processed} KICs without DVT: "
                    f"{removed_count} removed, {backed_up_count} backed up")
        
        return total_processed
    
    def _get_kic_file_stats(self, kic_dir: str) -> Dict[str, Any]:
        """Get file statistics for a KIC directory."""
        stats = {
            'llc_count': 0,
            'dvt_count': 0,
            'total_size_mb': 0
        }
        
        if not os.path.exists(kic_dir):
            return stats
        
        for file_path in Path(kic_dir).rglob('*.fits'):
            file_size = os.path.getsize(file_path)
            stats['total_size_mb'] += file_size / (1024 * 1024)
            
            if '_llc.fits' in file_path.name:
                stats['llc_count'] += 1
            elif '_dvt.fits' in file_path.name:
                stats['dvt_count'] += 1
        
        return stats
    
    def download_kics(self, kic_list: list) -> dict:
        """Download FITS files for a list of KICs with DVT filtering."""
        if not kic_list:
            logging.warning("No KICs provided")
            return self.stats
        
        logging.info(f"Starting download for {len(kic_list)} KICs")
        logging.info(f"Mode: {'ExoMiner' if self.exominer_format else 'Standard'}")
        if self.exominer_format:
            logging.info(f"DVT filtering: {'Strict' if self.strict_dvt else 'Post-download'}")
            logging.info(f"No-DVT handling: {'Backup' if self.backup_no_dvt else 'Remove'}")
        
        # Process KICs in batches
        total_batches = (len(kic_list) + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(kic_list))
            batch = kic_list[start_idx:end_idx]
            
            logging.info(f"\nProcessing batch {batch_num + 1}/{total_batches} "
                        f"(KICs {start_idx + 1}-{end_idx})")
            
            batch_results = self._process_batch(batch)
            
            # Log batch summary
            batch_success = sum(1 for r in batch_results if r['success'])
            batch_files = sum(r['files_downloaded'] for r in batch_results)
            batch_with_dvt = sum(1 for r in batch_results if r.get('has_dvt', False))
            logging.info(f"Batch {batch_num + 1} complete: {batch_success}/{len(batch)} KICs, "
                        f"{batch_files} files, {batch_with_dvt} with DVT")
            
            # Force sync after each batch to ensure data persistence
            if self.redis_client is not None:
                logging.debug(f"Syncing batch {batch_num + 1} data to database...")
                self._sync_redis_to_db()
        
        # Stop periodic sync and perform final sync
        self._stop_sync_timer()
        if self.redis_client is not None:
            logging.info("Performing final sync from Redis to database...")
            self._sync_redis_to_db()
            time.sleep(1)
            self._sync_redis_to_db()  # Second sync to catch any stragglers
            
            # Force database checkpoint
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            conn.close()
            
            logging.info("Final sync complete!")
            self._cleanup_redis_keys()
        
        # Filter KICs without DVT if in ExoMiner mode
        if self.exominer_format:
            logging.info("\nStarting DVT filtering for ExoMiner mode...")
            removed_count = self.remove_kics_without_dvt()
            if removed_count > 0:
                self.generate_dvt_filter_report()
        
        # Final summary
        elapsed = time.time() - self.stats['start_time']
        logging.info(f"\n{'='*60}")
        logging.info(f"DOWNLOAD COMPLETE!")
        logging.info(f"Total time: {elapsed/60:.1f} minutes")
        logging.info(f"KICs processed: {self.stats['processed']}")
        logging.info(f"KICs with data: {self.stats['kics_with_data']}")
        if self.exominer_format:
            logging.info(f"KICs with DVT: {self.stats['kics_with_dvt']}")
            logging.info(f"KICs without DVT: {self.stats['kics_without_dvt']}")
            logging.info(f"KICs removed (no DVT): {self.stats['kics_removed_no_dvt']}")
            logging.info(f"KICs backed up (no DVT): {self.stats['kics_backed_up_no_dvt']}")
        logging.info(f"Total files downloaded: {self.stats['downloaded']}")
        logging.info(f"Total LLC files: {self.stats['total_llc_files']}")
        logging.info(f"Total DVT files: {self.stats['total_dvt_files']}")
        logging.info(f"Errors: {self.stats['errors']}")
        logging.info(f"{'='*60}")
        
        return self.stats
    
    def generate_dvt_filter_report(self):
        """Generate detailed report about DVT filtering."""
        report_path = os.path.join(self.reports_dir, 'dvt_filter_report.txt')
        csv_path = os.path.join(self.reports_dir, 'removed_kics.csv')
        
        with open(report_path, 'w') as f:
            f.write("DVT Filter Report for ExoMiner Mode\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Job ID: {self.job_id}\n\n")
            
            f.write("Summary Statistics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total KICs processed: {self.stats['processed']}\n")
            f.write(f"KICs with DVT files: {self.stats['kics_with_dvt']}\n")
            f.write(f"KICs without DVT files: {self.stats['kics_without_dvt']}\n")
            
            if self.stats['kics_with_dvt'] + self.stats['kics_without_dvt'] > 0:
                dvt_percentage = (self.stats['kics_with_dvt'] / 
                                (self.stats['kics_with_dvt'] + self.stats['kics_without_dvt']) * 100)
                f.write(f"DVT coverage: {dvt_percentage:.1f}%\n")
            
            f.write(f"\nKICs removed (no DVT): {self.stats['kics_removed_no_dvt']}\n")
            f.write(f"KICs backed up (no DVT): {self.stats['kics_backed_up_no_dvt']}\n")
            
            if self.removed_kics:
                f.write("\n\nRemoved KICs Details:\n")
                f.write("-" * 30 + "\n")
                total_size_removed = 0
                for kic_info in self.removed_kics[:20]:  # Show first 20
                    f.write(f"KIC {kic_info['kic']}: {kic_info['llc_files']} LLC files, "
                           f"{kic_info['size_mb']:.1f} MB\n")
                    total_size_removed += kic_info['size_mb']
                
                if len(self.removed_kics) > 20:
                    f.write(f"... and {len(self.removed_kics) - 20} more\n")
                
                f.write(f"\nTotal space saved/backed up: {total_size_removed:.1f} MB\n")
        
        # Generate CSV of removed KICs
        if self.removed_kics:
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = ['kic', 'reason', 'llc_files', 'size_mb']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.removed_kics)
        
        logging.info(f"DVT filter report generated: {report_path}")
        if self.removed_kics:
            logging.info(f"Removed KICs CSV generated: {csv_path}")
    
    def _cleanup_redis_keys(self):
        """Clean up Redis keys for this job after successful completion."""
        if self.redis_client is None:
            return
        
        try:
            for key in self.redis_keys.values():
                self.redis_client.delete(key)
            logging.info(f"Cleaned up Redis keys for job {self.job_id}")
        except Exception as e:
            logging.warning(f"Could not clean up Redis keys: {e}")
    
    def retry_failed_downloads(self) -> dict:
        """Retry downloads for failed KICs."""
        retry_stats = {
            'attempted': 0,
            'succeeded': 0,
            'still_failed': 0
        }
        
        # Get failed KICs from database
        conn = sqlite3.connect(self.db_path)
        failed_kics = conn.execute(
            "SELECT kic FROM download_records WHERE success = false"
        ).fetchall()
        conn.close()
        
        if not failed_kics:
            logging.info("No failed downloads to retry")
            return retry_stats
        
        failed_kic_list = [str(row[0]) for row in failed_kics]
        retry_stats['attempted'] = len(failed_kic_list)
        
        logging.info(f"Retrying {len(failed_kic_list)} failed downloads...")
        
        # Process failed KICs
        for kic in failed_kic_list:
            result = self.download_kic(kic)
            if result['success']:
                retry_stats['succeeded'] += 1
                logging.info(f"Retry successful for KIC {kic}")
            else:
                retry_stats['still_failed'] += 1
                logging.warning(f"Retry failed for KIC {kic}: {result.get('error')}")
        
        # Final sync
        if self.redis_client:
            self._sync_redis_to_db()
        
        logging.info(f"Retry complete: {retry_stats['succeeded']}/{retry_stats['attempted']} succeeded")
        return retry_stats
    
    def generate_health_report(self, retry_stats: dict = None) -> str:
        """Generate comprehensive health check report with DVT statistics."""
        # Ensure ALL data is synced before generating report
        if self.redis_client is not None:
            logging.info("Ensuring all data is synced before generating health report...")
            self._sync_redis_to_db()
            time.sleep(1)
            self._sync_redis_to_db()
        
        report_path = os.path.join(self.job_dir, 'health_check_report.txt')
        
        conn = sqlite3.connect(self.db_path)
        
        # Get summary statistics with DVT info
        total_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records").fetchone()[0]
        successful_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE success = true").fetchone()[0]
        failed_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE success = false").fetchone()[0]
        
        # DVT statistics
        kics_with_dvt = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE has_dvt = true").fetchone()[0]
        kics_without_dvt = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE has_dvt = false AND success = true").fetchone()[0]
        
        # File statistics
        total_files = conn.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0]
        llc_files = conn.execute("SELECT COUNT(*) FROM file_inventory WHERE file_type = 'llc'").fetchone()[0]
        dvt_files = conn.execute("SELECT COUNT(*) FROM file_inventory WHERE file_type = 'dvt'").fetchone()[0]
        total_size_gb = conn.execute("SELECT SUM(file_size) / 1073741824.0 FROM file_inventory").fetchone()[0] or 0
        
        # Removed KICs statistics
        removed_kics = conn.execute("SELECT COUNT(*) FROM removed_kics").fetchone()[0] if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='removed_kics'").fetchone() else 0
        
        with open(report_path, 'w') as f:
            f.write("Kepler DR25 Download Health Check Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Job ID: {self.job_id}\n")
            f.write(f"Mode: {'ExoMiner' if self.exominer_format else 'Standard'}\n\n")
            
            f.write("Download Summary:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total KICs processed: {total_kics}\n")
            f.write(f"Successful downloads: {successful_kics}\n")
            f.write(f"Failed downloads: {failed_kics}\n")
            
            if self.exominer_format:
                f.write("\nDVT Statistics:\n")
                f.write("-" * 30 + "\n")
                f.write(f"KICs with DVT files: {kics_with_dvt}\n")
                f.write(f"KICs without DVT files: {kics_without_dvt}\n")
                if kics_with_dvt + kics_without_dvt > 0:
                    dvt_coverage = (kics_with_dvt / (kics_with_dvt + kics_without_dvt)) * 100
                    f.write(f"DVT coverage: {dvt_coverage:.1f}%\n")
                f.write(f"KICs removed (no DVT): {removed_kics}\n")
            
            f.write("\nFile Statistics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total files downloaded: {total_files}\n")
            f.write(f"LLC files: {llc_files}\n")
            f.write(f"DVT files: {dvt_files}\n")
            f.write(f"Total size: {total_size_gb:.2f} GB\n")
            
            if retry_stats:
                f.write("\nRetry Statistics:\n")
                f.write("-" * 30 + "\n")
                f.write(f"KICs attempted: {retry_stats.get('attempted', 0)}\n")
                f.write(f"Succeeded on retry: {retry_stats.get('succeeded', 0)}\n")
                f.write(f"Still failed: {retry_stats.get('still_failed', 0)}\n")
            
            # Performance metrics
            elapsed = time.time() - self.stats['start_time']
            f.write("\nPerformance Metrics:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total runtime: {elapsed/60:.1f} minutes\n")
            if elapsed > 0:
                f.write(f"KICs per minute: {total_kics/(elapsed/60):.1f}\n")
                f.write(f"Files per minute: {total_files/(elapsed/60):.1f}\n")
                f.write(f"GB per hour: {total_size_gb/(elapsed/3600):.2f}\n")
            
            # List failed KICs if any
            if failed_kics > 0:
                f.write("\nFailed KIC IDs:\n")
                f.write("-" * 30 + "\n")
                failed_list = conn.execute(
                    "SELECT kic, error_message FROM download_records WHERE success = false LIMIT 20"
                ).fetchall()
                for kic, error in failed_list:
                    f.write(f"KIC {kic}: {error}\n")
                if failed_kics > 20:
                    f.write(f"... and {failed_kics - 20} more\n")
        
        conn.close()
        
        logging.info(f"Health report generated: {report_path}")
        return report_path


def main():
    parser = argparse.ArgumentParser(description='Fast Kepler DR25 FITS Downloader with DVT Filtering')
    parser.add_argument('csv_file', help='Input CSV file with KIC IDs')
    parser.add_argument('--output-dir', default='kepler_downloads', help='Output directory')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-db', type=int, default=0, help='Redis database number')
    parser.add_argument('--no-exominer', action='store_true', help='Use Standard MAST format instead of ExoMiner (ExoMiner is default)')
    parser.add_argument('--strict-dvt', action='store_true', help='Skip KICs without DVT files immediately (ExoMiner mode)')
    parser.add_argument('--backup-no-dvt', action='store_true', help='Backup KICs without DVT instead of deleting (ExoMiner mode)')
    parser.add_argument('--retry-failed', action='store_true', help='Retry failed downloads')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Read KIC list from CSV
    try:
        df = pd.read_csv(args.csv_file, comment='#')
        
        # Look for KIC column
        kic_column = None
        for col in ['kepid', 'KIC', 'kic', 'kic_id']:
            if col in df.columns:
                kic_column = col
                break
        
        if kic_column is None:
            kic_column = df.columns[0]
            logging.warning(f"No standard KIC column found, using first column: {kic_column}")
        
        kic_list = df[kic_column].dropna().astype(str).tolist()
        logging.info(f"Loaded {len(kic_list)} KICs from {args.csv_file}")
        
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        sys.exit(1)
    
    # Generate job ID
    job_id = f"job-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create downloader instance
    downloader = FastKeplerDownloader(
        download_dir=args.output_dir,
        job_id=job_id,
        max_workers=args.workers,
        batch_size=args.batch_size,
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        redis_db=args.redis_db,
        exominer_format=not args.no_exominer,
        strict_dvt=args.strict_dvt,
        backup_no_dvt=args.backup_no_dvt
    )
    
    # Start download
    stats = downloader.download_kics(kic_list)
    
    # Retry failed downloads if requested
    retry_stats = None
    if args.retry_failed:
        retry_stats = downloader.retry_failed_downloads()
    
    # Generate health report
    report_path = downloader.generate_health_report(retry_stats)
    
    logging.info(f"Download completed! Results saved to: {downloader.job_dir}")
    logging.info(f"Health report: {report_path}")


if __name__ == "__main__":
    main()