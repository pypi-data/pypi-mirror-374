#!/usr/bin/env python3
"""
Generate comprehensive statistics for a completed job.
Provides detailed analysis of downloads, file types, and sizes.
"""

import os
import sqlite3
import sys

import pandas as pd


def format_size(bytes):
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def generate_stats(job_dir):
    """Generate comprehensive statistics for a job directory."""

    stats = {}

    # Basic info
    stats["job_id"] = os.path.basename(job_dir)
    stats["job_path"] = job_dir

    # Check database
    db_path = os.path.join(job_dir, "download_records.db")
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return None

    conn = sqlite3.connect(db_path)

    # Download statistics
    df_downloads = pd.read_sql_query("SELECT * FROM download_records", conn)
    stats["total_kics"] = len(df_downloads)
    stats["successful_kics"] = len(df_downloads[df_downloads["success"] == 1])
    stats["failed_kics"] = len(df_downloads[df_downloads["success"] == 0])
    stats["success_rate"] = (stats["successful_kics"] / stats["total_kics"] * 100) if stats["total_kics"] > 0 else 0

    # DVT statistics
    stats["kics_with_dvt"] = len(df_downloads[df_downloads["has_dvt"] == 1])
    stats["kics_without_dvt"] = len(df_downloads[df_downloads["has_dvt"] == 0])
    stats["dvt_coverage"] = (
        (stats["kics_with_dvt"] / stats["successful_kics"] * 100) if stats["successful_kics"] > 0 else 0
    )

    # File statistics
    df_files = pd.read_sql_query("SELECT * FROM file_inventory", conn)
    stats["total_files"] = len(df_files)

    # File type breakdown
    file_types = df_files["file_type"].value_counts().to_dict()
    stats["llc_files"] = file_types.get("llc", 0)
    stats["dvt_files"] = file_types.get("dvt", 0)
    stats["dvr_files"] = file_types.get("dvr", 0)
    stats["other_files"] = stats["total_files"] - stats["llc_files"] - stats["dvt_files"] - stats["dvr_files"]

    # Size statistics
    stats["total_size_bytes"] = df_files["file_size"].sum()
    stats["total_size"] = format_size(stats["total_size_bytes"])
    stats["avg_file_size"] = format_size(df_files["file_size"].mean()) if len(df_files) > 0 else "0 B"

    # Check for removed KICs (ExoMiner mode)
    try:
        df_removed = pd.read_sql_query("SELECT * FROM removed_kics", conn)
        stats["removed_kics"] = len(df_removed)
    except Exception:
        stats["removed_kics"] = 0

    # Mode detection
    kepler_dir = os.path.join(job_dir, "Kepler")
    mast_dir = os.path.join(job_dir, "mastDownload")

    if os.path.exists(kepler_dir):
        stats["mode"] = "ExoMiner"
    elif os.path.exists(mast_dir):
        stats["mode"] = "Standard"
    else:
        stats["mode"] = "Unknown"

    conn.close()

    return stats


def print_stats(stats):
    """Print statistics in a formatted way."""

    print("\n" + "=" * 60)
    print(f"📊 Job Statistics: {stats['job_id']}")
    print("=" * 60)

    print(f"\n📁 Mode: {stats['mode']}")
    print(f"📍 Path: {stats['job_path']}")

    print("\n📥 Download Summary:")
    print(f"  Total KICs attempted: {stats['total_kics']:,}")
    print(f"  Successful downloads: {stats['successful_kics']:,}")
    print(f"  Failed downloads: {stats['failed_kics']:,}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")

    if stats["mode"] == "ExoMiner":
        print("\n🔍 DVT Statistics:")
        print(f"  KICs with DVT: {stats['kics_with_dvt']:,}")
        print(f"  KICs without DVT: {stats['kics_without_dvt']:,}")
        print(f"  DVT coverage: {stats['dvt_coverage']:.1f}%")
        if stats["removed_kics"] > 0:
            print(f"  Removed KICs (no DVT): {stats['removed_kics']:,}")

    print("\n📄 File Statistics:")
    print(f"  Total files: {stats['total_files']:,}")
    print(f"  LLC files: {stats['llc_files']:,}")
    print(f"  DVT files: {stats['dvt_files']:,}")
    if stats["dvr_files"] > 0:
        print(f"  DVR files: {stats['dvr_files']:,}")
    if stats["other_files"] > 0:
        print(f"  Other files: {stats['other_files']:,}")

    print("\n💾 Storage Statistics:")
    print(f"  Total size: {stats['total_size']}")
    print(f"  Average file size: {stats['avg_file_size']}")

    print("\n" + "=" * 60)


def export_stats(stats, output_file):
    """Export statistics to CSV file."""
    df = pd.DataFrame([stats])
    df.to_csv(output_file, index=False)
    print(f"\n✅ Statistics exported to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_stats.py <job_directory> [--export stats.csv]")
        print("Example: python util/generate_stats.py kepler_downloads/job-20250907_015817")
        print("         python util/generate_stats.py kepler_downloads/job-20250907_015817 --export job_stats.csv")
        sys.exit(1)

    job_dir = sys.argv[1]

    if not os.path.exists(job_dir):
        print(f"Error: Job directory not found: {job_dir}")
        sys.exit(1)

    # Generate statistics
    stats = generate_stats(job_dir)

    if stats:
        print_stats(stats)

        # Check for export option
        if len(sys.argv) > 2 and sys.argv[2] == "--export":
            output_file = sys.argv[3] if len(sys.argv) > 3 else f"stats_{stats['job_id']}.csv"
            export_stats(stats, output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
