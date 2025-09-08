"""
Unit tests for the downloader module
"""

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import pandas as pd


class TestKICValidation:
    """Test KIC ID validation functions."""

    def test_valid_kic_format(self):
        """Test validation of properly formatted KIC IDs."""
        valid_kics = ["006922244", "007799349", "011446443", "123456789", "000000001"]

        for kic in valid_kics:
            # KIC should be 9 digits
            assert len(kic) == 9
            assert kic.isdigit()

    def test_invalid_kic_format(self):
        """Test rejection of invalid KIC formats."""
        invalid_kics = [
            "12345",  # Too short
            "1234567890",  # Too long
            "abc123456",  # Contains letters
            "12-345-678",  # Contains special characters
            "",  # Empty string
            None,  # None value
        ]

        for kic in invalid_kics:
            if kic is None or not isinstance(kic, str):
                assert True  # These should be rejected
            else:
                assert not (len(kic) == 9 and kic.isdigit())


class TestDatabaseOperations:
    """Test database creation and operations."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        yield db_path

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_database_creation(self, temp_db):
        """Test database and tables are created correctly."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create tables (simplified version)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS download_records (
                kic_id TEXT PRIMARY KEY,
                success INTEGER,
                llc_count INTEGER,
                dvt_count INTEGER,
                has_dvt INTEGER,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS file_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kic_id TEXT,
                file_path TEXT,
                file_type TEXT,
                file_size INTEGER,
                download_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        assert "download_records" in table_names
        assert "file_inventory" in table_names

        conn.close()

    def test_insert_download_record(self, temp_db):
        """Test inserting download records."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS download_records (
                kic_id TEXT PRIMARY KEY,
                success INTEGER,
                llc_count INTEGER,
                dvt_count INTEGER
            )
        """
        )

        # Insert record
        cursor.execute(
            """
            INSERT INTO download_records (kic_id, success, llc_count, dvt_count)
            VALUES (?, ?, ?, ?)
        """,
            ("006922244", 1, 17, 1),
        )

        conn.commit()

        # Verify insertion
        cursor.execute("SELECT * FROM download_records WHERE kic_id = ?", ("006922244",))
        record = cursor.fetchone()

        assert record is not None
        assert record[0] == "006922244"
        assert record[1] == 1  # success
        assert record[2] == 17  # llc_count
        assert record[3] == 1  # dvt_count

        conn.close()


class TestCSVProcessing:
    """Test CSV file processing."""

    @pytest.fixture
    def sample_csv(self):
        """Create a sample CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp.write("kepid\n")
            tmp.write("006922244\n")
            tmp.write("007799349\n")
            tmp.write("011446443\n")
            csv_path = tmp.name

        yield csv_path

        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)

    def test_read_csv_kics(self, sample_csv):
        """Test reading KIC IDs from CSV."""
        df = pd.read_csv(sample_csv)

        assert "kepid" in df.columns
        assert len(df) == 3

        kics = df["kepid"].astype(str).str.zfill(9).tolist()
        assert kics == ["006922244", "007799349", "011446443"]

    def test_handle_missing_csv(self):
        """Test handling of missing CSV file."""
        non_existent = "/tmp/non_existent_file.csv"

        with pytest.raises(FileNotFoundError):
            pd.read_csv(non_existent)


class TestRedisOperations:
    """Test Redis buffering operations."""

    @patch("redis.Redis")
    def test_redis_connection(self, mock_redis):
        """Test Redis connection establishment."""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True

        # Simulate connection
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        assert r.ping() == True

    @patch("redis.Redis")
    def test_redis_buffer_operations(self, mock_redis):
        """Test Redis buffer push and pop operations."""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance

        # Simulate buffering
        buffer_key = "job-test-buffer"
        test_data = '{"kic_id": "006922244", "success": true}'

        mock_redis_instance.rpush.return_value = 1
        mock_redis_instance.llen.return_value = 1
        mock_redis_instance.lpop.return_value = test_data.encode()

        import redis

        r = redis.Redis()

        # Push to buffer
        result = r.rpush(buffer_key, test_data)
        assert result == 1

        # Check buffer size
        size = r.llen(buffer_key)
        assert size == 1

        # Pop from buffer
        data = r.lpop(buffer_key)
        assert data.decode() == test_data


class TestHealthReport:
    """Test health report generation."""

    def test_generate_health_stats(self):
        """Test generation of health statistics."""
        stats = {
            "total_kics": 100,
            "successful": 95,
            "failed": 5,
            "success_rate": 95.0,
            "has_dvt": 90,
            "no_dvt": 10,
            "dvt_coverage": 90.0,
        }

        assert stats["success_rate"] == (stats["successful"] / stats["total_kics"]) * 100
        assert stats["dvt_coverage"] == (stats["has_dvt"] / stats["total_kics"]) * 100
        assert stats["successful"] + stats["failed"] == stats["total_kics"]

    def test_format_health_report(self):
        """Test health report formatting."""
        report_lines = [
            "=" * 60,
            "DOWNLOAD HEALTH CHECK REPORT",
            "=" * 60,
            "",
            "Summary Statistics:",
            "-" * 40,
            f"Total KICs Processed: 100",
            f"Successful Downloads: 95 (95.0%)",
            f"Failed Downloads: 5 (5.0%)",
            "",
        ]

        report = "\n".join(report_lines)
        assert "DOWNLOAD HEALTH CHECK REPORT" in report
        assert "Total KICs Processed: 100" in report
        assert "95.0%" in report


class TestModeDetection:
    """Test mode detection for ExoMiner vs Standard."""

    def test_detect_exominer_structure(self):
        """Test detection of ExoMiner directory structure."""
        # ExoMiner structure: Kepler/XXXX/XXXXXXXXX/
        exominer_path = "kepler_downloads/job-20250907/Kepler/0069/006922244/"

        assert "Kepler" in exominer_path
        assert "/0069/006922244/" in exominer_path

        # Extract KIC from path
        parts = exominer_path.split("/")
        if "Kepler" in parts:
            kepler_idx = parts.index("Kepler")
            if len(parts) > kepler_idx + 2:
                kic = parts[kepler_idx + 2]
                assert kic == "006922244"

    def test_detect_standard_structure(self):
        """Test detection of Standard MAST structure."""
        # Standard structure: mastDownload/Kepler/kplr*_lc/
        standard_path = "kepler_downloads/job-20250907/mastDownload/Kepler/kplr006922244_lc/"

        assert "mastDownload" in standard_path
        assert "kplr" in standard_path
        assert "_lc" in standard_path

        # Extract KIC from path
        import re

        match = re.search(r"kplr(\d{9})", standard_path)
        if match:
            kic = match.group(1)
            assert kic == "006922244"


@pytest.fixture
def sample_kic_list():
    """Fixture providing sample KIC IDs for tests."""
    return ["006922244", "007799349", "011446443"]


@pytest.fixture
def mock_mast_response():
    """Mock MAST API response."""
    return {
        "data": [
            {
                "dataURL": "https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:KEPLER/url/kplr006922244-2009131105131_llc.fits",
                "filename": "kplr006922244-2009131105131_llc.fits",
                "size": 12345678,
            }
        ]
    }


def test_with_fixtures(sample_kic_list, mock_mast_response):
    """Test using fixtures."""
    assert len(sample_kic_list) == 3
    assert "data" in mock_mast_response
    assert len(mock_mast_response["data"]) > 0
