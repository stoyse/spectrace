"""
Tests for Ghidra integration functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from services.ghidra_service import GhidraDecompiler
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestGhidraDecompiler:
    """Test cases for GhidraDecompiler service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.decompiler = GhidraDecompiler()
    
    def test_validate_binary_file_valid_elf(self):
        """Test validation of valid ELF file."""
        # Create a temporary file with ELF magic
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 100)  # ELF header
            tmp.flush()
            
            is_valid, message = self.decompiler.validate_binary_file(tmp.name)
            
            assert is_valid is True
            assert "Valid binary file" in message
            
        os.unlink(tmp.name)
    
    def test_validate_binary_file_valid_pe(self):
        """Test validation of valid PE file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'MZ' + b'\x00' * 100)  # PE/DOS header
            tmp.flush()
            
            is_valid, message = self.decompiler.validate_binary_file(tmp.name)
            
            assert is_valid is True
            assert "Valid binary file" in message
            
        os.unlink(tmp.name)
    
    def test_validate_binary_file_empty(self):
        """Test validation of empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.flush()  # Empty file
            
            is_valid, message = self.decompiler.validate_binary_file(tmp.name)
            
            assert is_valid is False
            assert "File is empty" in message
            
        os.unlink(tmp.name)
    
    def test_validate_binary_file_too_large(self):
        """Test validation of file that's too large."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Create a file larger than 100MB (simulated)
            tmp.write(b'A' * 1000)  # Small file for testing
            tmp.flush()
            
            # Mock file size check
            with patch('os.path.getsize', return_value=101 * 1024 * 1024):
                is_valid, message = self.decompiler.validate_binary_file(tmp.name)
                
                assert is_valid is False
                assert "File too large" in message
            
        os.unlink(tmp.name)
    
    def test_validate_binary_file_nonexistent(self):
        """Test validation of non-existent file."""
        is_valid, message = self.decompiler.validate_binary_file("/nonexistent/file")
        
        assert is_valid is False
        assert "File does not exist" in message
    
    @patch('services.ghidra_service.GhidraDecompiler._run_ghidra_analysis')
    @patch('services.ghidra_service.GhidraDecompiler._create_decompile_script')
    @patch('services.ghidra_service.GhidraDecompiler._parse_results')
    async def test_decompile_binary_success(self, mock_parse, mock_script, mock_run):
        """Test successful binary decompilation."""
        # Mock successful Ghidra execution
        mock_script.return_value = "/tmp/script.java"
        mock_run.return_value = (True, "Analysis completed", "")
        mock_parse.return_value = {
            'assembly_code': 'mov eax, 1\nret',
            'decompiled_code': 'int main() { return 1; }',
            'metadata': {'language': 'x86'}
        }
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 100)
            tmp.flush()
            
            result = await self.decompiler.decompile_binary(tmp.name, "test.bin")
            
            assert result['success'] is True
            assert 'mov eax' in result['assembly_code']
            assert 'int main' in result['decompiled_code']
            assert result['metadata']['language'] == 'x86'
            
        os.unlink(tmp.name)
    
    @patch('services.ghidra_service.GhidraDecompiler._run_ghidra_analysis')
    @patch('services.ghidra_service.GhidraDecompiler._create_decompile_script')
    async def test_decompile_binary_ghidra_failure(self, mock_script, mock_run):
        """Test decompilation when Ghidra fails."""
        mock_script.return_value = "/tmp/script.java"
        mock_run.return_value = (False, "", "Java not found")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 100)
            tmp.flush()
            
            result = await self.decompiler.decompile_binary(tmp.name, "test.bin")
            
            assert result['success'] is False
            assert 'Java runtime not found' in result.get('error', '')
            
        os.unlink(tmp.name)

class TestDecompileEndpoint:
    """Test cases for the decompile API endpoint."""
    
    def test_decompile_endpoint_missing_file(self):
        """Test decompile endpoint without file."""
        response = client.post("/api/v1/decompile")
        assert response.status_code == 422  # Validation error
    
    def test_decompile_endpoint_with_valid_file(self):
        """Test decompile endpoint with valid file."""
        # Create a small ELF-like file for testing
        file_content = b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 100
        
        with patch('services.ghidra_service.GhidraDecompiler.decompile_binary') as mock_decompile:
            mock_decompile.return_value = {
                'success': True,
                'assembly_code': 'test assembly',
                'decompiled_code': 'test C code',
                'metadata': {'filename': 'test.bin'}
            }
            
            files = {'file': ('test.bin', file_content, 'application/octet-stream')}
            response = client.post("/api/v1/decompile", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['assembly_code'] == 'test assembly'
            assert data['decompiled_code'] == 'test C code'
    
    def test_decompile_endpoint_large_file(self):
        """Test decompile endpoint with file that's too large."""
        # Mock a large file
        file_content = b'A' * 1000  # Small content for test
        
        # Mock file size to be too large
        with patch('fastapi.UploadFile.size', 101 * 1024 * 1024):
            files = {'file': ('large.bin', file_content, 'application/octet-stream')}
            response = client.post("/api/v1/decompile", files=files)
            
            assert response.status_code == 400
            assert 'too large' in response.json()['detail'].lower()
    
    def test_decompile_endpoint_no_filename(self):
        """Test decompile endpoint with file without filename."""
        file_content = b'\x7fELF\x01\x01\x01\x00' + b'\x00' * 100
        files = {'file': ('', file_content, 'application/octet-stream')}
        
        response = client.post("/api/v1/decompile", files=files)
        
        assert response.status_code == 400
        assert 'filename is required' in response.json()['detail'].lower()

@pytest.fixture
def sample_elf_binary():
    """Create a sample ELF binary for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:
        # Simple ELF header (minimal)
        elf_header = (
            b'\x7fELF'          # ELF magic
            b'\x01'             # 32-bit
            b'\x01'             # Little endian
            b'\x01'             # ELF version
            b'\x00'             # System V ABI
            b'\x00' * 8         # Padding
            b'\x02\x00'         # Executable file
            b'\x03\x00'         # x86 architecture
            b'\x01\x00\x00\x00' # Version
            b'\x00' * 20        # Rest of header
        )
        tmp.write(elf_header + b'\x00' * 100)  # Add some content
        tmp.flush()
        yield tmp.name
    
    os.unlink(tmp.name)

class TestIntegrationFlow:
    """Integration tests for the complete binary analysis flow."""
    
    @pytest.mark.asyncio
    async def test_full_binary_analysis_flow(self, sample_elf_binary):
        """Test the complete flow from binary upload to analysis results."""
        # This would test the full integration but requires a running Ghidra installation
        # For now, we'll test the API structure
        
        decompiler = GhidraDecompiler()
        
        # Test file validation
        is_valid, _ = decompiler.validate_binary_file(sample_elf_binary)
        assert is_valid is True
        
        # The actual decompilation test would require Ghidra to be installed
        # In a real environment, you would test:
        # result = await decompiler.decompile_binary(sample_elf_binary, "test.bin")
        # assert result['success'] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])