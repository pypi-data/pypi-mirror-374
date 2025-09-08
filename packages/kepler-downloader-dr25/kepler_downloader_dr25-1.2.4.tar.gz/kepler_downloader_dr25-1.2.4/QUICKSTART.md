# Kepler-Downloader-DR25 Quick Start Guide

**Get NASA Kepler telescope data in 5 minutes**

This toolkit downloads Kepler DR25 data from NASA's MAST archive with automatic retry, smart filtering, and ML-ready formats.

## 1. Quick Installation (2 minutes)

### Install from PyPI (Recommended)
```bash
pip install kepler-downloader-dr25
```

### Or install from GitHub
```bash
git clone https://github.com/akira921x/Kepler-Downloader-DR25.git
cd Kepler-Downloader-DR25
pip install -r requirements.txt
```

## 2. Setup Redis (1 minute)

**macOS:**
```bash
brew install redis && brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server && sudo systemctl start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis-kepler redis:latest
```

## 3. Download Your First Data (2 minutes)

### Quick Test (3 targets)
```bash
# Create a test file
echo "006922244,007799349,011446443" > input/test.csv

# Download the data
python get-kepler-dr25.py input/test.csv
```

### Download Real Datasets
```bash
# Kepler Objects of Interest (~8,200 targets, ~200GB)
python get-kepler-dr25.py input_samples/cumulative_koi_2025.09.06_13.27.56.csv

# Threshold Crossing Events (~17,000 targets, ~400GB)
python get-kepler-dr25.py input_samples/q1_q17_dr25_tce_2025.09.06_13.29.19.csv
```

## Common Tasks

### Filter Existing Data (Save Time & Storage)
```bash
# Extract KOI subset from existing TCE data
python filter-get-kepler-dr25.py \
  --input-csv input_samples/cumulative_koi_2025.09.06_13.27.56.csv \
  --source-job kepler_downloads/job-with-tce-data
```

### Check Download Status
```bash
# View progress with verbose mode
python get-kepler-dr25.py input/targets.csv --verbose

# Check health report after completion
cat kepler_downloads/job-*/health_check_report.txt
```

### Find Missing Data
```bash
python util/check_missing_kics.py input/targets.csv kepler_downloads/job-XXX
```

### Retry Failed Downloads
```bash
python get-kepler-dr25.py input/targets.csv --retry-failed
```

## Data Formats

### ML-Ready Format (Default)
Best for [ExoMiner](https://github.com/nasa/ExoMiner) and [AstroNet](https://github.com/google-research/exoplanet-ml):
```bash
python get-kepler-dr25.py input/targets.csv
```

### Standard MAST Format
Traditional format for general analysis:
```bash
python get-kepler-dr25.py input/targets.csv --no-exominer
```

## Performance Tips

### Faster Downloads
```bash
# Use 8 parallel workers (default is 4)
python get-kepler-dr25.py input/targets.csv --workers 8 --batch-size 100
```

### Save Storage
```bash
# Filter instead of re-downloading
python filter-get-kepler-dr25.py \
  --input-csv input/subset.csv \
  --source-job kepler_downloads/existing-job
```

## Quick Troubleshooting

### Redis Not Running?
```bash
redis-cli ping  # Should return "PONG"
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Database Shows Zeros?
```bash
# Rebuild database from files
python util/rebuild_database.py kepler_downloads/job-XXX
```

### Network Timeouts?
```bash
# Retry with more workers
python get-kepler-dr25.py input/targets.csv --workers 8 --retry-failed
```

## Example Workflow

### Complete Research Pipeline
```bash
# 1. Download KOI data
python get-kepler-dr25.py input_samples/cumulative_koi_2025.09.06_13.27.56.csv

# 2. Check completeness
python util/check_missing_kics.py input_samples/cumulative_koi_2025.09.06_13.27.56.csv kepler_downloads/job-XXX

# 3. Generate report
python util/generate_stats.py kepler_downloads/job-XXX

# 4. Filter subset for analysis
echo "006922244,007799349" > input/my_targets.csv
python filter-get-kepler-dr25.py --input-csv input/my_targets.csv --source-job kepler_downloads/job-XXX
```

## What's Next?

After downloading:
1. Find your data in `kepler_downloads/job-YYYYMMDD_HHMMSS/`
2. Check `health_check_report.txt` for summary
3. Use FITS files with your analysis tools or ML frameworks

## Need Help?

- **Full Documentation**: [README.md](README.md)
- **Report Issues**: [GitHub Issues](https://github.com/akira921x/Kepler-Downloader-DR25/issues)
- **Sample Data**: Check `input_samples/` folder

Happy researching with Kepler data!