"""
Incremental Repository Indexer

Refreshes symbol indices, call graphs, and test mappings incrementally
when files are added, modified, or deleted, avoiding full repository rescans.
"""

from typing import List, Dict, Set, Optional
from pathlib import Path

from ..db.database import get_db_session
from ..db.models import SymbolIndexModel, CallGraphEdgeModel
from .ast_parser import parse_file, Symbol
from .symbol_graph import SymbolGraph
from .file_scanner import FileScanner


class IncrementalIndexer:
    """
    Incremental index refresher triggered after file mutations.
    """

    def __init__(self, session_id: int, repo_path: str, db_path: Optional[str] = None):
        self.session_id = session_id
        self.repo_path = Path(repo_path).resolve()
        self.db_path = db_path
        self.symbol_graph = SymbolGraph(session_id, db_path)

    def refresh_files(self, modified_files: List[str]) -> Dict[str, int]:
        """
        Incrementally re-index only the specified modified file paths.

        Args:
            modified_files: List of file paths (relative or absolute) that were modified or added

        Returns:
            Dictionary with statistics:
            - 'symbols_updated': Number of symbols re-indexed
            - 'files_processed': Number of files processed
        """
        if not modified_files:
            return {"symbols_updated": 0, "files_processed": 0}

        resolved_paths = []
        for fp in modified_files:
            p = Path(fp)
            if not p.is_absolute():
                p = (self.repo_path / p).resolve()
            if p.exists() and p.is_file():
                resolved_paths.append(p)

        if not resolved_paths:
            return {"symbols_updated": 0, "files_processed": 0}

        rel_path_strings = [
            str(p.relative_to(self.repo_path)) if p.is_relative_to(self.repo_path) else str(p)
            for p in resolved_paths
        ]

        # 1. Remove existing symbol index records for modified files
        with get_db_session(self.db_path) as session:
            session.query(SymbolIndexModel)\
                .filter(
                    SymbolIndexModel.session_id == self.session_id,
                    SymbolIndexModel.file_path.in_(rel_path_strings)
                )\
                .delete(synchronize_session=False)

            session.query(CallGraphEdgeModel)\
                .filter(
                    CallGraphEdgeModel.session_id == self.session_id,
                    CallGraphEdgeModel.caller_file.in_(rel_path_strings)
                )\
                .delete(synchronize_session=False)

            session.commit()

        # 2. Parse symbols for modified files and insert new index records
        symbols_count = 0
        with get_db_session(self.db_path) as session:
            for p, rel_str in zip(resolved_paths, rel_path_strings):
                extracted_symbols = parse_file(str(p))
                for sym in extracted_symbols:
                    index_record = SymbolIndexModel(
                        session_id=self.session_id,
                        file_path=rel_str,
                        symbol_name=sym.name,
                        symbol_type=sym.symbol_type,
                        language=p.suffix.lstrip('.').lower(),
                        start_line=sym.start_line,
                        end_line=sym.end_line,
                        start_col=sym.start_col,
                        end_col=sym.end_col,
                        parent_symbol=sym.parent_symbol,
                        signature=sym.signature,
                        docstring=sym.docstring,
                    )
                    session.add(index_record)
                    symbols_count += 1
            session.commit()

        # 3. Update NetworkX symbol graph incrementally
        self.symbol_graph.update_from_files(rel_path_strings)

        return {
            "symbols_updated": symbols_count,
            "files_processed": len(resolved_paths)
        }
