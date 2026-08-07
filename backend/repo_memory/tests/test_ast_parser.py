"""
Unit tests for AST parser
"""

import tempfile
from pathlib import Path
import pytest

from backend.repo_memory.indexer.ast_parser import ASTParser, parse_file, Symbol


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""# Test Python file

def top_level_function(arg1, arg2):
    '''A top-level function'''
    pass

class TestClass:
    def method_one(self):
        pass
    
    def method_two(self, param):
        return param

class AnotherClass:
    pass

def another_function():
    pass
""")
        path = f.name
    
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def temp_typescript_file():
    """Create a temporary TypeScript file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
        f.write("""// Test TypeScript file

export function topLevelFunction(arg1: string, arg2: number) {
    return arg1;
}

export class TestClass {
    methodOne() {
        return true;
    }
    
    methodTwo(param: string) {
        return param;
    }
}

export const arrowFunction = (x: number) => {
    return x * 2;
};

class InternalClass {
}
""")
        path = f.name
    
    yield path
    Path(path).unlink(missing_ok=True)


def test_parser_initialization():
    """Test ASTParser initialization"""
    parser = ASTParser()
    assert parser is not None


def test_parse_python_file(temp_python_file):
    """Test parsing Python file"""
    parser = ASTParser()
    symbols = parser.parse_file(temp_python_file)
    
    # Should find functions and classes
    assert len(symbols) > 0
    
    # Extract symbol names
    symbol_names = [s.name for s in symbols]
    
    # Check for expected symbols
    assert "top_level_function" in symbol_names
    assert "TestClass" in symbol_names
    assert "method_one" in symbol_names
    assert "method_two" in symbol_names
    assert "AnotherClass" in symbol_names
    assert "another_function" in symbol_names
    
    # Check symbol types
    func_symbols = [s for s in symbols if s.symbol_type == "function"]
    class_symbols = [s for s in symbols if s.symbol_type == "class"]
    method_symbols = [s for s in symbols if s.symbol_type == "method"]
    
    assert len(func_symbols) >= 2  # top_level_function, another_function
    assert len(class_symbols) >= 2  # TestClass, AnotherClass
    assert len(method_symbols) >= 2  # method_one, method_two
    
    # Check language is set
    assert all(s.language == "python" for s in symbols)
    
    # Check method parent relationships
    method_one = next(s for s in symbols if s.name == "method_one")
    assert method_one.parent_symbol == "TestClass"


def test_parse_typescript_file(temp_typescript_file):
    """Test parsing TypeScript file"""
    parser = ASTParser()
    symbols = parser.parse_file(temp_typescript_file)
    
    assert len(symbols) > 0
    
    symbol_names = [s.name for s in symbols]
    
    # Check for expected symbols
    assert "topLevelFunction" in symbol_names
    assert "TestClass" in symbol_names
    assert "arrowFunction" in symbol_names
    
    # Check language is set
    assert all(s.language == "typescript" for s in symbols)


def test_parse_file_convenience_function(temp_python_file):
    """Test parse_file convenience function"""
    symbols = parse_file(temp_python_file)
    
    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert all(isinstance(s, Symbol) for s in symbols)


def test_parse_nonexistent_file():
    """Test parsing file that doesn't exist"""
    parser = ASTParser()
    
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/nonexistent/file.py")


def test_parse_unsupported_extension():
    """Test parsing file with unsupported extension"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("text file")
        path = f.name
    
    try:
        parser = ASTParser()
        symbols = parser.parse_file(path)
        
        # Should return empty list for unsupported files
        assert symbols == []
    finally:
        Path(path).unlink(missing_ok=True)


def test_symbol_dataclass():
    """Test Symbol dataclass"""
    symbol = Symbol(
        name="test_func",
        symbol_type="function",
        file_path="/test/file.py",
        start_line=1,
        end_line=5,
        start_col=0,
        end_col=20,
        language="python",
    )
    
    assert symbol.name == "test_func"
    assert symbol.symbol_type == "function"
    assert symbol.file_path == "/test/file.py"
    assert symbol.start_line == 1
    assert symbol.end_line == 5
    assert symbol.parent_symbol is None
    assert symbol.meta == {}


def test_symbol_with_parent():
    """Test Symbol with parent relationship"""
    symbol = Symbol(
        name="method",
        symbol_type="method",
        file_path="/test/file.py",
        start_line=10,
        end_line=15,
        start_col=4,
        end_col=24,
        parent_symbol="ParentClass",
        language="python",
    )
    
    assert symbol.parent_symbol == "ParentClass"


def test_get_file_hash(temp_python_file):
    """Test file hash calculation"""
    parser = ASTParser()
    hash1 = parser.get_file_hash(temp_python_file)
    
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 hex digest length
    
    # Hash should be consistent
    hash2 = parser.get_file_hash(temp_python_file)
    assert hash1 == hash2


def test_javascript_file():
    """Test parsing JavaScript file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("""
function jsFunction(param) {
    return param;
}

const arrowFunc = (x) => x * 2;

class JSClass {
    method() {
        return true;
    }
}
""")
        path = f.name
    
    try:
        parser = ASTParser()
        symbols = parser.parse_file(path)
        
        assert len(symbols) > 0
        assert all(s.language == "javascript" for s in symbols)
        
        symbol_names = [s.name for s in symbols]
        assert "jsFunction" in symbol_names
        assert "arrowFunc" in symbol_names
        assert "JSClass" in symbol_names
    finally:
        Path(path).unlink(missing_ok=True)


def test_line_numbers(temp_python_file):
    """Test that line numbers are captured"""
    symbols = parse_file(temp_python_file)
    
    for symbol in symbols:
        assert symbol.start_line > 0
        assert symbol.end_line >= symbol.start_line
        assert symbol.start_col >= 0
