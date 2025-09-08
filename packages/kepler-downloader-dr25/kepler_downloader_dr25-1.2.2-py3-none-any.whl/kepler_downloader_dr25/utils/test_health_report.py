#!/usr/bin/env python3
"""
Test script to verify health report generation after bug fixes.
"""

import sqlite3
import os
import sys
from pathlib import Path


def check_database_contents(job_dir):
    """Check if database has data."""
    db_path = os.path.join(job_dir, "download_records.db")

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)

    # Check download_records
    download_count = conn.execute("SELECT COUNT(*) FROM download_records").fetchone()[0]
    print(f"📊 Download records: {download_count}")

    # Check file_inventory
    file_count = conn.execute("SELECT COUNT(*) FROM file_inventory").fetchone()[0]
    print(f"📁 File inventory: {file_count}")

    # Check some statistics
    if download_count > 0:
        successful = conn.execute("SELECT COUNT(*) FROM download_records WHERE success = 1").fetchone()[0]
        with_dvt = conn.execute("SELECT COUNT(*) FROM download_records WHERE has_dvt = 1").fetchone()[0]
        print(f"✅ Successful downloads: {successful}")
        print(f"📦 KICs with DVT: {with_dvt}")

    conn.close()

    return download_count > 0 or file_count > 0


def check_health_report(job_dir):
    """Check health report contents."""
    report_path = os.path.join(job_dir, "health_check_report.txt")

    if not os.path.exists(report_path):
        print(f"❌ Health report not found: {report_path}")
        return False

    with open(report_path, "r") as f:
        content = f.read()

    # Check if report has actual data (not all zeros)
    has_data = False
    if "Total KICs processed: 0" not in content or "Total files downloaded: 0" not in content:
        has_data = True

    print("\n📋 Health Report Summary:")
    print("-" * 40)

    # Extract key metrics
    for line in content.split("\n"):
        if (
            "Total KICs processed:" in line
            or "Total files downloaded:" in line
            or "Total size:" in line
            or "KICs with DVT files:" in line
        ):
            print(line.strip())

    return has_data


def main():
    # Check the most recent job directories
    base_dir = "kepler_downloads"

    if not os.path.exists(base_dir):
        print(f"❌ Directory not found: {base_dir}")
        sys.exit(1)

    # Find all job directories
    job_dirs = sorted([d for d in os.listdir(base_dir) if d.startswith("job-")])

    if not job_dirs:
        print("❌ No job directories found")
        sys.exit(1)

    print(f"Found {len(job_dirs)} job directories\n")

    # Check the last two jobs
    for job_dir in job_dirs[-2:]:
        full_path = os.path.join(base_dir, job_dir)
        print(f"\n{'='*50}")
        print(f"Checking: {job_dir}")
        print("=" * 50)

        # Check database
        has_db_data = check_database_contents(full_path)

        # Check health report
        has_report_data = check_health_report(full_path)

        # Summary
        print("\n🔍 Summary:")
        if has_db_data:
            print("✅ Database has data")
        else:
            print("❌ Database is empty")

        if has_report_data:
            print("✅ Health report has data")
        else:
            print("❌ Health report shows all zeros")


if __name__ == "__main__":
    main()
