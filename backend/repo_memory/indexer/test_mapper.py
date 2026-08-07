"""
Test Mapper - Test-to-Source File Association

Maps test files to their corresponding source files using naming conventions
and directory structures across Python, TypeScript, and JavaScript.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Optional
from difflib import SequenceMatcher


class TestMapper:
    """
    Maps test files to source files using heuristics.
    
    Attributes:
        repo_path: Repository root path
        _file_cache: Cache of scanned files by type
    """
    __test__ = False
    
    # Test naming patterns: (pattern, base_confidence)
    PYTHON_TEST_PATTERNS = [
        ("test_{name}.py", 1.0),      # test_auth.py → auth.py
        ("{name}_test.py", 1.0),      # auth_test.py → auth.py
        ("test_{name}s.py", 0.9),     # test_users.py → user.py
    ]
    
    TYPESCRIPT_TEST_PATTERNS = [
        ("{name}.test.ts", 1.0),      # auth.test.ts → auth.ts
        ("{name}.spec.ts", 1.0),      # auth.spec.ts → auth.ts
        ("{name}.test.tsx", 1.0),     # Auth.test.tsx → Auth.tsx
        ("{name}.spec.tsx", 1.0),
    ]
    
    JAVASCRIPT_TEST_PATTERNS = [
        ("{name}.test.js", 1.0),      # auth.test.js → auth.js
        ("{name}.spec.js", 1.0),      # auth.spec.js → auth.js
        ("{name}.test.jsx", 1.0),     # Auth.test.jsx → Auth.jsx
        ("{name}.spec.jsx", 1.0),
    ]
    
    # Test directory names
    TEST_DIRECTORIES = [
        "test", "tests", "__tests__", "spec", "specs", 
        "test_integration", "test_unit"
    ]
    
    # Source directory names
    SOURCE_DIRECTORIES = [
        "src", "lib", "app", "source", "core"
    ]
    
    def __init__(self, repo_path: str):
        """
        Initialize test mapper.
        
        Args:
            repo_path: Root directory of repository
        """
        self.repo_path = Path(repo_path).resolve()
        self._file_cache: Dict[str, List[Path]] = {"test": [], "source": []}
        self._scan_directory()
    
    def find_related_tests(
        self,
        source_file: str
    ) -> List[Tuple[str, float]]:
        """
        Find test files for a source file.
        
        Args:
            source_file: Path to source file (relative or absolute)
        
        Returns:
            List of (test_path, confidence) tuples, sorted by confidence
        
        Requirement: 3.4, 14
        """
        source_path = self._resolve_path(source_file)
        if not source_path.exists():
            return []
        
        source_name = source_path.stem
        language = self.get_language(str(source_path))
        
        results = []
        
        # 1. Pattern-based matching
        patterns = self._get_patterns_for_language(language)
        for pattern_template, base_confidence in patterns:
            # Generate possible test file names
            test_names = self._generate_test_names(source_name, pattern_template)
            
            for test_name in test_names:
                # Search in cached test files
                matches = self._find_files_by_name(test_name, self._file_cache["test"])
                for match in matches:
                    confidence = self._compute_confidence(
                        source_name,
                        match.stem,
                        "pattern_match"
                    ) * base_confidence
                    results.append((str(match), confidence))
        
        # 2. Directory parallel search
        parallel_tests = self._find_parallel_tests(source_path)
        results.extend(parallel_tests)
        
        # 3. Remove duplicates and sort by confidence
        seen = set()
        unique_results = []
        for path, conf in results:
            if path not in seen:
                seen.add(path)
                unique_results.append((path, conf))
        
        unique_results.sort(key=lambda x: x[1], reverse=True)
        return unique_results
    
    def find_source_for_test(
        self,
        test_file: str
    ) -> List[Tuple[str, float]]:
        """
        Find source file for a test file.
        
        Args:
            test_file: Path to test file
        
        Returns:
            List of (source_path, confidence) tuples
        
        Requirement: 3.5, 14
        """
        test_path = self._resolve_path(test_file)
        if not test_path.exists():
            return []
        
        test_name = test_path.stem
        language = self.get_language(str(test_path))
        
        # Extract source name from test name
        source_names = self._extract_source_names(test_name, language)
        
        results = []
        for source_name, confidence_mult in source_names:
            # Find source files with this name
            ext = self._get_source_extension(language)
            source_files = self._find_files_by_name(
                source_name + ext,
                self._file_cache["source"]
            )
            
            for source_file in source_files:
                confidence = self._compute_confidence(
                    source_file.stem,
                    test_name,
                    "reverse_match"
                ) * confidence_mult
                results.append((str(source_file), confidence))
        
        # Directory parallel search
        parallel_sources = self._find_parallel_sources(test_path)
        results.extend(parallel_sources)
        
        # Remove duplicates and sort
        seen = set()
        unique_results = []
        for path, conf in results:
            if path not in seen:
                seen.add(path)
                unique_results.append((path, conf))
        
        unique_results.sort(key=lambda x: x[1], reverse=True)
        return unique_results
    
    def get_language(self, file_path: str) -> str:
        """
        Infer language from file extension.
        
        Args:
            file_path: Path to file
        
        Returns:
            Language name (python, typescript, javascript, unknown)
        
        Requirement: 19.5
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.py':
            return 'python'
        elif ext in ('.ts', '.tsx'):
            return 'typescript'
        elif ext in ('.js', '.jsx'):
            return 'javascript'
        else:
            return 'unknown'
    
    def _compute_confidence(
        self,
        source_name: str,
        test_name: str,
        match_type: str
    ) -> float:
        """
        Compute confidence score for test mapping.
        
        Confidence rubric:
        - Exact match: 1.0
        - Directory parallel: 0.9
        - High similarity (>0.8): 0.8
        - Medium similarity (>0.6): 0.7
        - Low similarity (>0.4): 0.6
        - Very low similarity: 0.5
        - No match: 0.0
        
        Requirement: 14
        """
        # Exact match
        if source_name == test_name:
            return 1.0
        
        # Directory parallel gets high confidence
        if match_type == "directory_parallel":
            return 0.9
        
        # Use string similarity (Levenshtein-based)
        ratio = SequenceMatcher(None, source_name.lower(), test_name.lower()).ratio()
        
        if ratio >= 0.8:
            return 0.8
        elif ratio >= 0.6:
            return 0.7
        elif ratio >= 0.4:
            return 0.6
        elif ratio >= 0.2:
            return 0.5
        else:
            return 0.0
    
    def _scan_directory(self):
        """Populate file cache by scanning repository"""
        if not self.repo_path.exists():
            return
        
        # Scan all code files
        for ext in ['.py', '.ts', '.tsx', '.js', '.jsx']:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                # Skip hidden directories and common excludes
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if 'node_modules' in file_path.parts or '__pycache__' in file_path.parts:
                    continue
                
                # Determine if test or source
                if self._is_test_file(file_path):
                    self._file_cache["test"].append(file_path)
                else:
                    self._file_cache["source"].append(file_path)
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file"""
        name = file_path.stem.lower()
        
        # Check name patterns
        if name.startswith('test_') or name.endswith('_test'):
            return True
        if '.test.' in file_path.name or '.spec.' in file_path.name:
            return True
        
        # Check directory
        for part in file_path.parts:
            if part.lower() in self.TEST_DIRECTORIES:
                return True
        
        return False
    
    def _get_patterns_for_language(self, language: str) -> List[Tuple[str, float]]:
        """Get test patterns for language"""
        if language == 'python':
            return self.PYTHON_TEST_PATTERNS
        elif language == 'typescript':
            return self.TYPESCRIPT_TEST_PATTERNS
        elif language == 'javascript':
            return self.JAVASCRIPT_TEST_PATTERNS
        else:
            return []
    
    def _generate_test_names(self, source_name: str, pattern: str) -> List[str]:
        """Generate possible test file names from pattern"""
        names = []
        
        # Direct substitution
        if '{name}' in pattern:
            names.append(pattern.replace('{name}', source_name))
        
        # Handle plural/singular variations
        if source_name.endswith('s'):
            singular = source_name[:-1]
            if '{name}' in pattern:
                names.append(pattern.replace('{name}', singular))
        else:
            plural = source_name + 's'
            if '{name}' in pattern:
                names.append(pattern.replace('{name}', plural))
        
        return names
    
    def _extract_source_names(
        self,
        test_name: str,
        language: str
    ) -> List[Tuple[str, float]]:
        """Extract possible source names from test name"""
        results = []
        
        # Remove test prefixes/suffixes
        name = test_name.lower()
        
        if name.startswith('test_'):
            results.append((name[5:], 1.0))
        if name.endswith('_test'):
            results.append((name[:-5], 1.0))
        if name.startswith('test'):
            results.append((name[4:], 0.9))
        
        # For .test. and .spec. patterns
        if '.test.' in test_name or '.spec.' in test_name:
            base = test_name.split('.')[0]
            results.append((base, 1.0))
        
        # If no pattern matched, use as-is with low confidence
        if not results:
            results.append((test_name, 0.5))
        
        return results
    
    def _get_source_extension(self, language: str) -> str:
        """Get typical source file extension for language"""
        if language == 'python':
            return '.py'
        elif language == 'typescript':
            return '.ts'
        elif language == 'javascript':
            return '.js'
        else:
            return ''
    
    def _find_files_by_name(
        self,
        target_name: str,
        file_list: List[Path]
    ) -> List[Path]:
        """Find files matching target name in list"""
        return [f for f in file_list if f.name == target_name]
    
    def _find_parallel_tests(self, source_path: Path) -> List[Tuple[str, float]]:
        """Find tests in parallel directory structure"""
        results = []
        
        # Check if source is in a source directory
        for source_dir in self.SOURCE_DIRECTORIES:
            if source_dir in source_path.parts:
                # Try to find parallel test directory
                for test_dir in self.TEST_DIRECTORIES:
                    parallel_path = self._swap_directory(
                        source_path, source_dir, test_dir
                    )
                    if parallel_path and parallel_path.exists():
                        results.append((str(parallel_path), 0.9))
        
        return results
    
    def _find_parallel_sources(self, test_path: Path) -> List[Tuple[str, float]]:
        """Find sources in parallel directory structure"""
        results = []
        
        # Check if test is in a test directory
        for test_dir in self.TEST_DIRECTORIES:
            if test_dir in test_path.parts:
                # Try to find parallel source directory
                for source_dir in self.SOURCE_DIRECTORIES:
                    parallel_path = self._swap_directory(
                        test_path, test_dir, source_dir
                    )
                    if parallel_path and parallel_path.exists():
                        results.append((str(parallel_path), 0.9))
        
        return results
    
    def _swap_directory(
        self,
        file_path: Path,
        old_dir: str,
        new_dir: str
    ) -> Optional[Path]:
        """Swap one directory component with another"""
        parts = list(file_path.parts)
        try:
            idx = parts.index(old_dir)
            parts[idx] = new_dir
            return Path(*parts)
        except ValueError:
            return None
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path relative to repo"""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return (self.repo_path / path).resolve()
    
    def get_stats(self) -> Dict:
        """Get statistics about cached files"""
        return {
            'test_files': len(self._file_cache["test"]),
            'source_files': len(self._file_cache["source"]),
            'total_files': len(self._file_cache["test"]) + len(self._file_cache["source"]),
            'repo_path': str(self.repo_path)
        }
