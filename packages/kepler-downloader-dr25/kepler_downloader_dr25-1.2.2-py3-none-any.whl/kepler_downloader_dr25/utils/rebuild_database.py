#!/usr/bin/env python3
"""
Rebuild database from filesystem for existing job directories.
This fixes the issue where Redis data was not synced to SQLite.
"""

import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json


def rebuild_database_from_filesystem(job_dir):
    """Rebuild the database by scanning the filesystem."""

    db_path = os.path.join(job_dir, "download_records.db")
    kepler_dir = os.path.join(job_dir, "Kepler")

    if not os.path.exists(kepler_dir):
        print(f"❌ Kepler directory not found: {kepler_dir}")
        return False

    print(f"🔄 Rebuilding database for: {job_dir}")

    # Connect to database
    conn = sqlite3.connect(db_path)

    # Clear existing data
    conn.execute("DELETE FROM download_records")
    conn.execute("DELETE FROM file_inventory")

    # Scan filesystem
    kic_count = 0
    file_count = 0
    total_size = 0

    # Iterate through KIC directories
    for first_level in Path(kepler_dir).iterdir():
        if not first_level.is_dir():
            continue

        for kic_dir in first_level.iterdir():
            if not kic_dir.is_dir():
                continue

            kic_id = int(kic_dir.name)
            kic_count += 1

            # Count files for this KIC
            llc_files = 0
            dvt_files = 0
            file_paths = []

            for fits_file in kic_dir.glob("*.fits"):
                file_path = str(fits_file)
                file_size = fits_file.stat().st_size
                file_count += 1
                total_size += file_size
                file_paths.append(file_path)

                # Determine file type
                if "_llc.fits" in fits_file.name:
                    file_type = "llc"
                    llc_files += 1
                elif "_dvt.fits" in fits_file.name:
                    file_type = "dvt"
                    dvt_files += 1
                else:
                    file_type = "other"

                # Insert into file_inventory
                conn.execute(
                    """
                    INSERT INTO file_inventory 
                    (kic, file_type, file_path, file_size, job_id)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (kic_id, file_type, file_path, file_size, job_dir.split("/")[-1]),
                )

            # Insert into download_records
            has_dvt = dvt_files > 0
            total_files = llc_files + dvt_files

            conn.execute(
                """
                INSERT INTO download_records 
                (kic, success, files_downloaded, llc_files, dvt_files, has_dvt, error_message, job_id, file_paths)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    kic_id,
                    1,  # success = true (since files exist)
                    total_files,
                    llc_files,
                    dvt_files,
                    has_dvt,
                    None,  # no error
                    job_dir.split("/")[-1],
                    json.dumps(file_paths),
                ),
            )

            if kic_count % 100 == 0:
                print(f"  Processed {kic_count} KICs, {file_count} files...")
                conn.commit()  # Commit periodically

    # Final commit
    conn.commit()

    # Print summary
    print(f"\n✅ Database rebuilt successfully!")
    print(f"  - KICs: {kic_count}")
    print(f"  - Files: {file_count}")
    print(f"  - Total size: {total_size / (1024**3):.2f} GB")

    # Verify
    verify_count = conn.execute("SELECT COUNT(*) FROM download_records").fetchone()[0]
    verify_files = conn.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0]
    print(f"\n🔍 Verification:")
    print(f"  - Records in DB: {verify_count}")
    print(f"  - Files in DB: {verify_files}")

    conn.close()

    # Regenerate health report
    regenerate_health_report(job_dir)

    return True


def regenerate_health_report(job_dir):
    """Regenerate health report from the rebuilt database."""

    db_path = os.path.join(job_dir, "download_records.db")
    report_path = os.path.join(job_dir, "health_check_report.txt")

    conn = sqlite3.connect(db_path)

    # Get statistics
    total_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records").fetchone()[0]
    successful_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE success = 1").fetchone()[0]
    failed_kics = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE success = 0").fetchone()[0]

    kics_with_dvt = conn.execute("SELECT COUNT(DISTINCT kic) FROM download_records WHERE has_dvt = 1").fetchone()[0]
    kics_without_dvt = conn.execute(
        "SELECT COUNT(DISTINCT kic) FROM download_records WHERE has_dvt = 0 AND success = 1"
    ).fetchone()[0]

    total_files = conn.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0]
    llc_files = conn.execute("SELECT COUNT(*) FROM file_inventory WHERE file_type = 'llc'").fetchone()[0]
    dvt_files = conn.execute("SELECT COUNT(*) FROM file_inventory WHERE file_type = 'dvt'").fetchone()[0]
    total_size_gb = conn.execute("SELECT SUM(file_size) / 1073741824.0 FROM file_inventory").fetchone()[0] or 0

    conn.close()

    # Write report
    with open(report_path, "w") as f:
        f.write("Kepler DR25 Download Health Check Report (REBUILT)\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Job ID: {os.path.basename(job_dir)}\n")
        f.write("Mode: ExoMiner\n\n")

        f.write("Download Summary:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total KICs processed: {total_kics}\n")
        f.write(f"Successful downloads: {successful_kics}\n")
        f.write(f"Failed downloads: {failed_kics}\n")

        f.write("\nDVT Statistics:\n")
        f.write("-" * 30 + "\n")
        f.write(f"KICs with DVT files: {kics_with_dvt}\n")
        f.write(f"KICs without DVT files: {kics_without_dvt}\n")
        if kics_with_dvt + kics_without_dvt > 0:
            dvt_coverage = (kics_with_dvt / (kics_with_dvt + kics_without_dvt)) * 100
            f.write(f"DVT coverage: {dvt_coverage:.1f}%\n")

        f.write("\nFile Statistics:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total files downloaded: {total_files}\n")
        f.write(f"LLC files: {llc_files}\n")
        f.write(f"DVT files: {dvt_files}\n")
        f.write(f"Total size: {total_size_gb:.2f} GB\n")

    print(f"\n📋 Health report regenerated: {report_path}")


def main():
    if len(sys.argv) > 1:
        # Specific job directory provided
        job_dir = sys.argv[1]
        rebuild_database_from_filesystem(job_dir)
    else:
        # Process all job directories
        base_dir = "kepler_downloads"

        if not os.path.exists(base_dir):
            print(f"❌ Directory not found: {base_dir}")
            sys.exit(1)

        job_dirs = sorted([os.path.join(base_dir, d) for d in os.listdir(base_dir) if d.startswith("job-")])

        if not job_dirs:
            print("❌ No job directories found")
            sys.exit(1)

        print(f"Found {len(job_dirs)} job directories\n")

        for job_dir in job_dirs:
            print(f"\n{'='*60}")
            rebuild_database_from_filesystem(job_dir)


if __name__ == "__main__":
    main()
