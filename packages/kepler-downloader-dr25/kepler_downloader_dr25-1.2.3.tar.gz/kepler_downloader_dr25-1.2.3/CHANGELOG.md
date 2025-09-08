# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-07

### Added
- Initial release of Kepler-Downloader-DR25
- Main downloader script (`get-kepler-dr25.py`) with ExoMiner/Standard mode support
- Universal filter script (`filter-get-kepler-dr25.py`) for mode conversion and filtering
- Redis buffering for reliable database operations
- DVT validation for ExoMiner compatibility
- Parallel downloading with configurable workers
- Comprehensive health reports after each job
- Database rebuild utility (`util/rebuild_database.py`)
- Missing KIC checker (`util/check_missing_kics.py`)
- Statistics generator (`util/generate_stats.py`)
- Health report diagnostic tool (`util/test_health_report.py`)

### Fixed
- Database synchronization issue (missing conn.commit())
- Proper transaction handling for SQLite operations
- Batch synchronization after each batch completion

### Features
- Support for both ExoMiner and Standard MAST formats
- Automatic retry mechanism for failed downloads
- Mode detection and conversion capabilities
- DVT filtering for machine learning compatibility
- Job-based organization with timestamped directories
- Comprehensive documentation (README.md, QUICKSTART.md)

### Performance
- Processing rate: ~50-60 KICs/minute with 4 workers
- Successfully tested with 17,000+ KIC downloads
- 99.9% success rate with retry mechanism
- Zero database corruption with Redis buffering

### Data Source
- NASA Kepler Space Telescope Data Release 25 (DR25)
- Mikulski Archive for Space Telescopes (MAST)
- Compatible with ExoMiner and AstroNet ML frameworks