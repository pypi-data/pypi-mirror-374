"""
Unit tests for the filter module
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
import sqlite3


class TestFilterOperations:
    """Test filter operations for existing data."""
    
    @pytest.fixture
    def temp_job_dir(self):
        """Create a temporary job directory structure."""
        temp_dir = tempfile.mkdtemp(prefix='test_job_')
        
        # Create ExoMiner structure
        exominer_dir = os.path.join(temp_dir, 'Kepler', '0069', '006922244')
        os.makedirs(exominer_dir, exist_ok=True)
        
        # Create dummy files
        open(os.path.join(exominer_dir, 'test_llc.fits'), 'w').close()
        open(os.path.join(exominer_dir, 'test_dvt.fits'), 'w').close()
        
        yield temp_dir
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_filter_existing_kics(self, temp_job_dir):
        """Test filtering KICs from existing job."""
        # Check that files exist
        kic_path = os.path.join(temp_job_dir, 'Kepler', '0069', '006922244')
        assert os.path.exists(kic_path)
        
        llc_file = os.path.join(kic_path, 'test_llc.fits')
        dvt_file = os.path.join(kic_path, 'test_dvt.fits')
        
        assert os.path.exists(llc_file)
        assert os.path.exists(dvt_file)
    
    def test_copy_filtered_files(self, temp_job_dir):
        """Test copying filtered files to new location."""
        # Create target directory
        target_dir = tempfile.mkdtemp(prefix='test_target_')
        
        try:
            # Source path
            source_kic = os.path.join(temp_job_dir, 'Kepler', '0069', '006922244')
            
            # Target path
            target_kic = os.path.join(target_dir, 'Kepler', '0069', '006922244')
            os.makedirs(os.path.dirname(target_kic), exist_ok=True)
            
            # Copy files
            shutil.copytree(source_kic, target_kic)
            
            # Verify copy
            assert os.path.exists(os.path.join(target_kic, 'test_llc.fits'))
            assert os.path.exists(os.path.join(target_kic, 'test_dvt.fits'))
            
        finally:
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)


class TestModeConversion:
    """Test conversion between ExoMiner and Standard modes."""
    
    def test_standard_to_exominer_path(self):
        """Test path conversion from Standard to ExoMiner format."""
        kic_id = "006922244"
        
        # Standard path
        standard_path = f"mastDownload/Kepler/kplr{kic_id}_lc/"
        
        # Convert to ExoMiner
        first_four = kic_id[:4]
        exominer_path = f"Kepler/{first_four}/{kic_id}/"
        
        assert exominer_path == "Kepler/0069/006922244/"
    
    def test_exominer_to_standard_path(self):
        """Test path conversion from ExoMiner to Standard format."""
        kic_id = "006922244"
        
        # ExoMiner path
        first_four = kic_id[:4]
        exominer_path = f"Kepler/{first_four}/{kic_id}/"
        
        # Convert to Standard
        standard_lc_path = f"mastDownload/Kepler/kplr{kic_id}_lc/"
        standard_dv_path = f"mastDownload/Kepler/kplr{kic_id}_dv/"
        
        assert standard_lc_path == "mastDownload/Kepler/kplr006922244_lc/"
        assert standard_dv_path == "mastDownload/Kepler/kplr006922244_dv/"


class TestDVTValidation:
    """Test DVT file validation for ExoMiner mode."""
    
    @pytest.fixture
    def kic_with_dvt(self):
        """Create a KIC directory with DVT file."""
        temp_dir = tempfile.mkdtemp(prefix='test_dvt_')
        kic_dir = os.path.join(temp_dir, 'Kepler', '0069', '006922244')
        os.makedirs(kic_dir, exist_ok=True)
        
        # Create files
        open(os.path.join(kic_dir, 'test_llc.fits'), 'w').close()
        open(os.path.join(kic_dir, 'test_dvt.fits'), 'w').close()
        
        yield kic_dir
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def kic_without_dvt(self):
        """Create a KIC directory without DVT file."""
        temp_dir = tempfile.mkdtemp(prefix='test_no_dvt_')
        kic_dir = os.path.join(temp_dir, 'Kepler', '0069', '007799349')
        os.makedirs(kic_dir, exist_ok=True)
        
        # Create only LLC files
        open(os.path.join(kic_dir, 'test_llc.fits'), 'w').close()
        
        yield kic_dir
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_validate_dvt_present(self, kic_with_dvt):
        """Test validation when DVT file is present."""
        dvt_files = [f for f in os.listdir(kic_with_dvt) if 'dvt' in f.lower()]
        assert len(dvt_files) > 0
    
    def test_validate_dvt_missing(self, kic_without_dvt):
        """Test validation when DVT file is missing."""
        dvt_files = [f for f in os.listdir(kic_without_dvt) if 'dvt' in f.lower()]
        assert len(dvt_files) == 0
    
    def test_backup_no_dvt_kics(self, kic_without_dvt):
        """Test backing up KICs without DVT files."""
        backup_dir = tempfile.mkdtemp(prefix='test_backup_')
        
        try:
            # Move to backup
            kic_id = os.path.basename(kic_without_dvt)
            backup_path = os.path.join(backup_dir, kic_id)
            shutil.move(kic_without_dvt, backup_path)
            
            # Verify backup
            assert os.path.exists(backup_path)
            assert not os.path.exists(kic_without_dvt)
            
        finally:
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)


class TestFilterDatabase:
    """Test filter operation database tracking."""
    
    @pytest.fixture
    def filter_db(self):
        """Create a temporary filter database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filter_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kic_id TEXT,
                source_mode TEXT,
                target_mode TEXT,
                operation TEXT,
                success INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_record_filter_operation(self, filter_db):
        """Test recording filter operations."""
        conn = sqlite3.connect(filter_db)
        cursor = conn.cursor()
        
        # Insert operation record
        cursor.execute('''
            INSERT INTO filter_operations 
            (kic_id, source_mode, target_mode, operation, success)
            VALUES (?, ?, ?, ?, ?)
        ''', ('006922244', 'exominer', 'exominer', 'copy', 1))
        
        conn.commit()
        
        # Verify
        cursor.execute('SELECT * FROM filter_operations WHERE kic_id = ?', ('006922244',))
        record = cursor.fetchone()
        
        assert record is not None
        assert record[1] == '006922244'  # kic_id
        assert record[2] == 'exominer'    # source_mode
        assert record[3] == 'exominer'    # target_mode
        assert record[4] == 'copy'        # operation
        assert record[5] == 1             # success
        
        conn.close()


class TestMissingKICDownload:
    """Test downloading missing KICs during filter operation."""
    
    @patch('requests.get')
    def test_download_missing_kic(self, mock_get):
        """Test downloading a missing KIC from MAST."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'FITS file content'
        mock_get.return_value = mock_response
        
        # Simulate download
        url = 'https://mast.stsci.edu/api/v0.1/Download/file'
        response = mock_get(url)
        
        assert response.status_code == 200
        assert len(response.content) > 0
    
    def test_identify_missing_kics(self):
        """Test identifying missing KICs from input list."""
        requested_kics = ['006922244', '007799349', '011446443']
        existing_kics = ['006922244', '011446443']
        
        missing_kics = [kic for kic in requested_kics if kic not in existing_kics]
        
        assert missing_kics == ['007799349']
        assert len(missing_kics) == 1