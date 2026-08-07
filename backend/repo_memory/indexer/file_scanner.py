"""
Repository File Scanner with .gitignore Support

Scans workspace directories while respecting .gitignore rules
and default exclusions for binary files, node_modules, etc.
"""

import os
from pathlib import Path
from typing import List, Set, Optional
import fnmatch


class FileScanner:
    """
    Repository file scanner that respects .gitignore patterns.
    """
    
    # Default patterns to exclude even if not in .gitignore
    DEFAULT_EXCLUDES = {
        # Version control
        ".git",
        ".svn",
        ".hg",
        # Dependencies
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "venv",
        "env",
        ".venv",
        # Build artifacts
        "dist",
        "build",
        "*.pyc",
        "*.pyo",
        "*.egg-info",
        ".tox",
        # IDE
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        ".DS_Store",
        # Databases
        "*.db",
        "*.sqlite",
        "*.sqlite3",
    }
    
    # File extensions to index
    CODE_EXTENSIONS = {
        ".py",    # Python
        ".ts",    # TypeScript
        ".tsx",   # TypeScript React
        ".js",    # JavaScript
        ".jsx",   # JavaScript React
        ".json",  # Configuration
        ".yaml",
        ".yml",
        ".md",    # Documentation
        ".txt",
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize file scanner.
        
        Args:
            repo_path: Root directory of the repository
        """
        self.repo_path = Path(repo_path).resolve()
        self.gitignore_patterns: List[str] = []
        self._load_gitignore()
    
    def _load_gitignore(self):
        """Load .gitignore patterns from repository root"""
        gitignore_path = self.repo_path / ".gitignore"
        
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        self.gitignore_patterns.append(line)
    
    def _should_exclude(self, path: Path, relative_path: str) -> bool:
        """
        Check if a path should be excluded based on .gitignore and defaults.
        
        Args:
            path: Absolute path to check
            relative_path: Path relative to repository root
            
        Returns:
            True if path should be excluded
        """
        # Check default excludes
        for pattern in self.DEFAULT_EXCLUDES:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            # Check if any parent directory matches
            if pattern in relative_path.split(os.sep):
                return True
        
        # Check .gitignore patterns
        for pattern in self.gitignore_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                pattern_dir = pattern[:-1]
                if pattern_dir in relative_path.split(os.sep):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(relative_path, pattern):
                return True
            elif fnmatch.fnmatch(path.name, pattern):
                return True
        
        return False
    
    def scan(
        self,
        include_extensions: Optional[Set[str]] = None,
        max_depth: Optional[int] = None,
    ) -> List[Path]:
        """
        Scan repository for files, respecting .gitignore.
        
        Args:
            include_extensions: Set of file extensions to include (e.g., {'.py', '.ts'})
                              If None, uses CODE_EXTENSIONS
            max_depth: Maximum directory depth to scan (None = unlimited)
            
        Returns:
            List of Path objects for files to index
        """
        if include_extensions is None:
            include_extensions = self.CODE_EXTENSIONS
        
        files = []
        
        def _scan_dir(directory: Path, depth: int = 0):
            """Recursively scan directory"""
            if max_depth is not None and depth > max_depth:
                return
            
            try:
                for item in directory.iterdir():
                    # Get relative path for pattern matching
                    try:
                        relative_path = item.relative_to(self.repo_path)
                    except ValueError:
                        continue  # Skip items outside repo_path
                    
                    relative_str = str(relative_path)
                    
                    # Check exclusions
                    if self._should_exclude(item, relative_str):
                        continue
                    
                    if item.is_dir():
                        _scan_dir(item, depth + 1)
                    elif item.is_file():
                        # Check if extension matches
                        if item.suffix.lower() in include_extensions:
                            files.append(item)
            
            except PermissionError:
                # Skip directories we don't have permission to read
                pass
        
        _scan_dir(self.repo_path)
        return sorted(files)  # Sort for deterministic ordering
    
    def get_relative_path(self, file_path: Path) -> str:
        """
        Get path relative to repository root.
        
        Args:
            file_path: Absolute path to file
            
        Returns:
            Relative path string (POSIX-style with forward slashes)
        """
        try:
            relative = file_path.relative_to(self.repo_path)
            return str(relative).replace(os.sep, "/")
        except ValueError:
            return str(file_path)


def scan_repository(
    repo_path: str,
    include_extensions: Optional[Set[str]] = None,
    max_depth: Optional[int] = None,
) -> List[str]:
    """
    Convenience function to scan a repository.
    
    Args:
        repo_path: Root directory of the repository
        include_extensions: Set of file extensions to include
        max_depth: Maximum directory depth to scan
        
    Returns:
        List of relative file paths (as strings)
    """
    scanner = FileScanner(repo_path)
    files = scanner.scan(include_extensions=include_extensions, max_depth=max_depth)
    return [scanner.get_relative_path(f) for f in files]
