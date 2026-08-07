"""
Polyglot AST Parser using Tree-sitter

Extracts symbols (functions, classes, methods) from Python, TypeScript,
and JavaScript source files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

try:
    from tree_sitter import Language, Parser, Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Language = None
    Parser = None
    Node = None


@dataclass
class Symbol:
    """Represents a code symbol (function, class, method, etc.)"""
    name: str
    symbol_type: str  # function, class, method, variable
    file_path: str
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    parent_symbol: Optional[str] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None
    language: str = "unknown"
    meta: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.meta is None:
            self.meta = {}


class ASTParser:
    """
    Polyglot AST parser supporting Python, TypeScript, and JavaScript.
    
    Uses tree-sitter for robust, language-agnostic parsing.
    """
    
    # Language to file extension mapping
    LANGUAGE_MAP = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
    }
    
    def __init__(self):
        """Initialize the parser"""
        # Tree-sitter is optional - will use regex fallback if not available
        self.parsers: Dict[str, Parser] = {}
        if TREE_SITTER_AVAILABLE:
            self._init_parsers()
    
    def _init_parsers(self):
        """
        Initialize tree-sitter parsers for supported languages.
        
        Note: This is a placeholder. In production, you would:
        1. Build language grammars: tree-sitter build
        2. Load compiled .so files
        3. Create parsers for each language
        
        For now, we'll create a simplified version that can be extended.
        """
        # TODO: Initialize actual tree-sitter language parsers
        # This requires building the language grammars first
        # For MVP, we'll use a fallback regex-based approach
        pass
    
    def parse_file(self, file_path: str) -> List[Symbol]:
        """
        Parse a source file and extract symbols.
        
        Args:
            file_path: Path to source file
            
        Returns:
            List of Symbol objects found in the file
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine language from extension
        language = self.LANGUAGE_MAP.get(path.suffix.lower())
        if language is None:
            return []  # Unsupported language
        
        # Read file content
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return []
        
        # Parse based on language
        if language == "python":
            return self._parse_python(file_path, content)
        elif language in ("typescript", "javascript"):
            return self._parse_typescript_javascript(file_path, content, language)
        
        return []
    
    def _parse_python(self, file_path: str, content: str) -> List[Symbol]:
        """
        Parse Python file using regex fallback (until tree-sitter is set up).
        
        Args:
            file_path: Path to file
            content: File content
            
        Returns:
            List of symbols
        """
        import re
        
        symbols = []
        lines = content.split("\n")
        
        # Regex patterns for Python
        class_pattern = re.compile(r"^class\s+(\w+)")
        func_pattern = re.compile(r"^def\s+(\w+)\s*\(([^)]*)\)")
        method_pattern = re.compile(r"^\s+def\s+(\w+)\s*\(([^)]*)\)")
        
        current_class = None
        
        for i, line in enumerate(lines, start=1):
            # Check for class definition
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                current_class = class_name
                symbols.append(Symbol(
                    name=class_name,
                    symbol_type="class",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,  # Will need multi-line support later
                    start_col=0,
                    end_col=len(line),
                    language="python",
                ))
                continue
            
            # Check for method (indented def inside class)
            method_match = method_pattern.match(line)
            if method_match and current_class:
                method_name = method_match.group(1)
                params = method_match.group(2)
                symbols.append(Symbol(
                    name=method_name,
                    symbol_type="method",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=line.index("def"),
                    end_col=len(line),
                    parent_symbol=current_class,
                    signature=f"def {method_name}({params})",
                    language="python",
                ))
                continue
            
            # Check for function (top-level def)
            func_match = func_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                symbols.append(Symbol(
                    name=func_name,
                    symbol_type="function",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=0,
                    end_col=len(line),
                    signature=f"def {func_name}({params})",
                    language="python",
                ))
                continue
            
            # Reset current_class if we hit non-indented code that's not a class
            if line and not line[0].isspace() and not class_pattern.match(line) and not func_pattern.match(line):
                if not line.strip().startswith("#"):  # Ignore comments
                    current_class = None
        
        return symbols
    
    def _parse_typescript_javascript(
        self, file_path: str, content: str, language: str
    ) -> List[Symbol]:
        """
        Parse TypeScript/JavaScript file using regex fallback.
        
        Args:
            file_path: Path to file
            content: File content
            language: "typescript" or "javascript"
            
        Returns:
            List of symbols
        """
        import re
        
        symbols = []
        lines = content.split("\n")
        
        # Patterns for TS/JS
        class_pattern = re.compile(r"^(?:export\s+)?class\s+(\w+)")
        function_pattern = re.compile(r"^(?:export\s+)?function\s+(\w+)\s*\(([^)]*)\)")
        arrow_func_pattern = re.compile(r"^(?:export\s+)?const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>")
        method_pattern = re.compile(r"^\s+(\w+)\s*\(([^)]*)\)")
        
        current_class = None
        
        for i, line in enumerate(lines, start=1):
            # Class
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                current_class = class_name
                symbols.append(Symbol(
                    name=class_name,
                    symbol_type="class",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=0,
                    end_col=len(line),
                    language=language,
                ))
                continue
            
            # Method (inside class)
            method_match = method_pattern.match(line)
            if method_match and current_class:
                method_name = method_match.group(1)
                params = method_match.group(2)
                symbols.append(Symbol(
                    name=method_name,
                    symbol_type="method",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=line.index(method_name),
                    end_col=len(line),
                    parent_symbol=current_class,
                    signature=f"{method_name}({params})",
                    language=language,
                ))
                continue
            
            # Function
            func_match = function_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
                symbols.append(Symbol(
                    name=func_name,
                    symbol_type="function",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=0,
                    end_col=len(line),
                    signature=f"function {func_name}({params})",
                    language=language,
                ))
                continue
            
            # Arrow function
            arrow_match = arrow_func_pattern.match(line)
            if arrow_match:
                func_name = arrow_match.group(1)
                params = arrow_match.group(2)
                symbols.append(Symbol(
                    name=func_name,
                    symbol_type="function",
                    file_path=file_path,
                    start_line=i,
                    end_line=i,
                    start_col=0,
                    end_col=len(line),
                    signature=f"const {func_name} = ({params}) =>",
                    language=language,
                ))
                continue
            
            # Reset current class on non-indented code
            if line and not line[0].isspace() and not class_pattern.match(line):
                current_class = None
        
        return symbols
    
    def get_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file content for change detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception:
            return ""


def parse_file(file_path: str) -> List[Symbol]:
    """
    Convenience function to parse a single file.
    
    Args:
        file_path: Path to source file
        
    Returns:
        List of Symbol objects
    """
    parser = ASTParser()
    return parser.parse_file(file_path)
