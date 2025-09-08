#!/usr/bin/env python3
"""
Check for missing KICs between a CSV file and a job directory.
Useful for identifying failed downloads or incomplete jobs.
"""

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd


def check_missing_kics(csv_file, job_dir):
    """
    Compare KICs in CSV file with downloaded KICs in job directory.

    Args:
        csv_file: Path to input CSV with KIC IDs
        job_dir: Path to job directory with download_records.db

    Returns:
        Set of missing KIC IDs
    """
    # Read KICs from CSV
    df = pd.read_csv(csv_file)

    # Find KIC column
    kic_column = None
    for col in df.columns:
        if "kic" in col.lower() or "kepid" in col.lower():
            kic_column = col
            break

    if not kic_column:
        print(f"Error: No KIC/KepID column found in {csv_file}")
        return set()

    csv_kics = set(df[kic_column].astype(str).str.zfill(9))
    print(f"Found {len(csv_kics)} KICs in CSV file")

    # Read downloaded KICs from database
    db_path = os.path.join(job_dir, "download_records.db")
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return csv_kics

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get successful downloads
    cursor.execute("SELECT kic_id FROM download_records WHERE success = 1")
    downloaded_kics = {row[0] for row in cursor.fetchall()}
    conn.close()

    print(f"Found {len(downloaded_kics)} successfully downloaded KICs")

    # Find missing KICs
    missing_kics = csv_kics - downloaded_kics

    return missing_kics


def main():
    if len(sys.argv) != 3:
        print("Usage: python check_missing_kics.py <csv_file> <job_directory>")
        print("Example: python util/check_missing_kics.py input/target.csv kepler_downloads/job-20250907_015817")
        sys.exit(1)

    csv_file = sys.argv[1]
    job_dir = sys.argv[2]

    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)

    if not os.path.exists(job_dir):
        print(f"Error: Job directory not found: {job_dir}")
        sys.exit(1)

    print("\nChecking missing KICs...")
    print(f"CSV file: {csv_file}")
    print(f"Job directory: {job_dir}")
    print("-" * 50)

    missing_kics = check_missing_kics(csv_file, job_dir)

    if missing_kics:
        print(f"\n⚠️  Found {len(missing_kics)} missing KICs")

        # Save to file
        output_file = f"missing_kics_{Path(job_dir).name}.csv"
        pd.DataFrame({"kepid": sorted(missing_kics)}).to_csv(output_file, index=False)
        print(f"✅ Missing KICs saved to: {output_file}")

        # Show first 10
        print("\nFirst 10 missing KICs:")
        for kic in sorted(missing_kics)[:10]:
            print(f"  - {kic}")

        if len(missing_kics) > 10:
            print(f"  ... and {len(missing_kics) - 10} more")
    else:
        print("\n✅ All KICs successfully downloaded!")

    return 0 if not missing_kics else 1


if __name__ == "__main__":
    sys.exit(main())
