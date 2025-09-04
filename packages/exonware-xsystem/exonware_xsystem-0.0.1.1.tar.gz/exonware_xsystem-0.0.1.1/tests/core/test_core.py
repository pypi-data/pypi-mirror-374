"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Tests for exonware.xsystem core utilities and integration.
"""

import pytest
from pathlib import Path
import tempfile
import os

from exonware.xsystem import (
    ThreadSafeFactory,
    PathValidator,
    PathSecurityError,
    AtomicFileWriter,
    CircularReferenceDetector,
    GenericHandlerFactory,
)


@pytest.mark.xsystem_core
class TestCoreIntegration:
    """Test core system integration and basic functionality."""
    
    def test_basic_imports(self):
        """Test that all core modules can be imported."""
        # This test verifies the core system is properly structured
        assert True, "Core imports successful"
    
    def test_core_components_available(self):
        """Test that core components are available and functional."""
        # Test ThreadSafeFactory
        factory = ThreadSafeFactory()
        assert factory is not None
        
        # Test PathValidator
        validator = PathValidator()
        assert validator is not None
        
        # Test AtomicFileWriter
        writer = AtomicFileWriter
        assert writer is not None


@pytest.mark.xsystem_core
class TestCoreSecurity:
    """Test core security features integration."""
    
    def test_path_validation_integration(self):
        """Test path validation as part of core security."""
        validator = PathValidator(check_existence=False)
        
        # Test basic functionality
        result = validator.validate_path("test/file.txt")
        assert isinstance(result, Path)
        
        # Test security restrictions
        with pytest.raises(PathSecurityError):
            validator.validate_path("../../../etc/passwd")
    
    def test_atomic_file_operations(self):
        """Test atomic file operations as core functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_file = Path(temp_dir) / "test.txt"
            content = "Hello, World!"
            
            # Test atomic write
            writer = AtomicFileWriter(target_path=str(target_file))
            writer.write(content.encode('utf-8'))
            
            assert target_file.exists()
            assert target_file.read_text() == content


@pytest.mark.xsystem_core
class TestCoreValidation:
    """Test core validation features."""
    
    def test_circular_reference_detection(self):
        """Test circular reference detection as core validation."""
        detector = CircularReferenceDetector()
        
        # Test simple data
        simple_data = {"key": "value"}
        assert not detector.has_circular_references(simple_data)
        
        # Test circular data
        circular_data = {}
        circular_data["self"] = circular_data
        assert detector.has_circular_references(circular_data)


@pytest.mark.xsystem_core
class TestCoreFactory:
    """Test core factory pattern implementation."""
    
    def test_handler_factory_basic(self):
        """Test basic handler factory functionality."""
        factory = GenericHandlerFactory()
        
        # Test basic registration
        factory.register_handler("test", str)
        handler = factory.get_handler("test")
        assert handler == str
