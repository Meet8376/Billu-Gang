"""
Unit tests for file scanner
"""

import tempfile
from pathlib import Path
import pytest

from backend.repo_memory.indexer.file_scanner import FileScanner, scan_repository


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create directory structure
        (repo_path / "src").mkdir()
        (repo_path / "tests").mkdir()
        (repo_path / "node_modules").mkdir()
        (repo_path / "__pycache__").mkdir()
        (repo_path / ".git").mkdir()
        
        # Create files
        (repo_path / "src" / "main.py").write_text("# Main file")
        (repo_path / "src" / "utils.py").write_text("# Utils file")
        (repo_path / "src" / "app.ts").write_text("// TypeScript file")
        (repo_path / "tests" / "test_main.py").write_text("# Test file")
        (repo_path / "README.md").write_text("# README")
        (repo_path / "package.json").write_text("{}")
        
        # Files that should be ignored
        (repo_path / "node_modules" / "module.js").write_text("// Module")
        (repo_path / "__pycache__" / "cache.pyc").write_text("cache")
        (repo_path / ".git" / "config").write_text("git config")
        
        # Create .gitignore
        (repo_path / ".gitignore").write_text("*.log\nbuild/\n")
        
        # Create files that should be ignored by .gitignore
        (repo_path / "debug.log").write_text("log file")
        (repo_path / "build").mkdir()
        (repo_path / "build" / "output.js").write_text("// Build output")
        
        yield repo_path


def test_file_scanner_init(temp_repo):
    """Test FileScanner initialization"""
    scanner = FileScanner(str(temp_repo))
    assert scanner.repo_path == temp_repo
    assert isinstance(scanner.gitignore_patterns, list)


def test_scan_repository(temp_repo):
    """Test scanning repository with default settings"""
    scanner = FileScanner(str(temp_repo))
    files = scanner.scan()
    
    # Convert to relative paths for easier checking
    relative_files = [scanner.get_relative_path(f) for f in files]
    
    # Should include source files
    assert "src/main.py" in relative_files
    assert "src/utils.py" in relative_files
    assert "src/app.ts" in relative_files
    assert "tests/test_main.py" in relative_files
    assert "README.md" in relative_files
    assert "package.json" in relative_files
    
    # Should exclude default patterns
    assert not any("node_modules" in f for f in relative_files)
    assert not any("__pycache__" in f for f in relative_files)
    assert not any(".git" in f for f in relative_files)
    
    # Should exclude .gitignore patterns
    assert "debug.log" not in relative_files
    assert not any("build" in f for f in relative_files)


def test_scan_with_extension_filter(temp_repo):
    """Test scanning with specific file extensions"""
    scanner = FileScanner(str(temp_repo))
    files = scanner.scan(include_extensions={".py"})
    
    relative_files = [scanner.get_relative_path(f) for f in files]
    
    # Should only include Python files
    assert "src/main.py" in relative_files
    assert "src/utils.py" in relative_files
    assert "tests/test_main.py" in relative_files
    
    # Should not include other extensions
    assert "src/app.ts" not in relative_files
    assert "README.md" not in relative_files
    assert "package.json" not in relative_files


def test_scan_with_max_depth(temp_repo):
    """Test scanning with depth limit"""
    scanner = FileScanner(str(temp_repo))
    files = scanner.scan(max_depth=0)
    
    relative_files = [scanner.get_relative_path(f) for f in files]
    
    # Should only include files at root level
    assert "README.md" in relative_files
    assert "package.json" in relative_files
    
    # Should not include files in subdirectories
    assert not any("src/" in f for f in relative_files)
    assert not any("tests/" in f for f in relative_files)


def test_gitignore_patterns(temp_repo):
    """Test .gitignore pattern matching"""
    scanner = FileScanner(str(temp_repo))
    
    # Check loaded patterns
    assert "*.log" in scanner.gitignore_patterns
    assert "build/" in scanner.gitignore_patterns


def test_default_excludes():
    """Test default exclusion patterns"""
    assert "node_modules" in FileScanner.DEFAULT_EXCLUDES
    assert "__pycache__" in FileScanner.DEFAULT_EXCLUDES
    assert ".git" in FileScanner.DEFAULT_EXCLUDES
    assert "venv" in FileScanner.DEFAULT_EXCLUDES


def test_scan_repository_convenience_function(temp_repo):
    """Test convenience function"""
    files = scan_repository(str(temp_repo))
    
    assert isinstance(files, list)
    assert len(files) > 0
    assert all(isinstance(f, str) for f in files)
    
    # Should include expected files
    assert "src/main.py" in files
    assert "src/utils.py" in files


def test_relative_path_conversion(temp_repo):
    """Test relative path conversion"""
    scanner = FileScanner(str(temp_repo))
    
    test_file = temp_repo / "src" / "main.py"
    relative = scanner.get_relative_path(test_file)
    
    # Should use POSIX-style forward slashes
    assert relative == "src/main.py"
    assert "\\" not in relative


def test_empty_repository():
    """Test scanning empty repository"""
    with tempfile.TemporaryDirectory() as tmpdir:
        scanner = FileScanner(tmpdir)
        files = scanner.scan()
        
        assert files == []


def test_repository_without_gitignore():
    """Test scanning repository without .gitignore"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / "test.py").write_text("# Test")
        
        scanner = FileScanner(str(repo_path))
        assert scanner.gitignore_patterns == []
        
        files = scanner.scan()
        assert len(files) == 1
