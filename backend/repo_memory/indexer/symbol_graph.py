"""
Symbol Graph - NetworkX-based dependency tracking

Builds and manages a directed graph of code symbols and their dependencies.
Supports import relationships, function calls, and inheritance tracking.
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import deque
from datetime import datetime

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

from ..db.database import get_db_session
from ..db.models import SymbolIndexModel, CallGraphEdgeModel


class SymbolGraph:
    """
    NetworkX-based directed graph tracking code dependencies.
    
    Attributes:
        graph: NetworkX DiGraph storing symbols and dependencies
        session_id: Database session ID for persistence
        _cache: Cache for transitive dependency queries
        _node_index: Fast lookup index: symbol_name -> node_ids
    """
    
    def __init__(self, session_id: int, db_path: Optional[str] = None):
        """
        Initialize empty graph for session.
        
        Args:
            session_id: Database session ID
            db_path: Optional path to database file
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "NetworkX not installed. Install with: pip install networkx"
            )
        
        self.graph = nx.DiGraph()
        self.session_id = session_id
        self.db_path = db_path
        self._cache: Dict[Tuple, List] = {}
        self._node_index: Dict[str, Set[str]] = {}
        self._graph_version = "1.0"
    
    def build_from_database(self):
        """
        Load symbols and edges from database.
        
        Requirement: 1, 15
        """
        with get_db_session(self.db_path) as session:
            # Query all symbols for this session
            symbols = session.query(SymbolIndexModel)\
                .filter_by(session_id=self.session_id)\
                .all()
            
            # Add nodes
            for sym in symbols:
                self.add_symbol(
                    symbol_name=sym.symbol_name,
                    file_path=sym.file_path,
                    symbol_type=sym.symbol_type,
                    parent_symbol=sym.parent_symbol,
                    start_line=sym.start_line,
                    end_line=sym.end_line
                )
            
            # Query all edges
            edges = session.query(CallGraphEdgeModel)\
                .filter_by(session_id=self.session_id)\
                .all()
            
            # Add edges
            for edge in edges:
                from_node = f"{edge.caller_file}::{edge.caller_symbol}"
                to_node = f"{edge.callee_file}::{edge.callee_symbol}"
                
                if from_node in self.graph and to_node in self.graph:
                    self.add_dependency(
                        from_symbol=from_node,
                        to_symbol=to_node,
                        edge_type=edge.edge_type,
                        confidence=edge.confidence
                    )
    
    def add_symbol(
        self,
        symbol_name: str,
        file_path: str,
        symbol_type: str,
        **attrs
    ):
        """
        Add node to graph.
        
        Args:
            symbol_name: Name of the symbol
            file_path: Path to file containing symbol
            symbol_type: Type (function, class, method, variable)
            **attrs: Additional attributes
        
        Requirement: 1.4
        """
        # Create unique node ID
        node_id = f"{file_path}::{symbol_name}"
        
        # Add node with attributes
        self.graph.add_node(
            node_id,
            symbol_name=symbol_name,
            file_path=file_path,
            symbol_type=symbol_type,
            **attrs
        )
        
        # Update index
        if symbol_name not in self._node_index:
            self._node_index[symbol_name] = set()
        self._node_index[symbol_name].add(node_id)
    
    def add_dependency(
        self,
        from_symbol: str,
        to_symbol: str,
        edge_type: str,
        confidence: float = 1.0
    ):
        """
        Add directed edge representing dependency.
        
        Args:
            from_symbol: Source symbol node ID
            to_symbol: Target symbol node ID
            edge_type: Type of dependency (import, call, inheritance)
            confidence: Confidence score (0.0-1.0)
        
        Requirement: 1.5
        """
        if from_symbol not in self.graph or to_symbol not in self.graph:
            return  # Skip if nodes don't exist
        
        self.graph.add_edge(
            from_symbol,
            to_symbol,
            edge_type=edge_type,
            confidence=confidence
        )
    
    def get_callers(self, symbol_name: str) -> List[str]:
        """
        Return symbols that depend on this symbol (incoming edges).
        
        Args:
            symbol_name: Name of symbol to query
        
        Returns:
            List of node IDs that call/import this symbol
        
        Requirement: 2.1
        """
        # Find all nodes with this symbol name
        target_nodes = self._node_index.get(symbol_name, set())
        
        callers = set()
        for node in target_nodes:
            # Get predecessors (incoming edges)
            callers.update(self.graph.predecessors(node))
        
        return list(callers)
    
    def get_callees(self, symbol_name: str) -> List[str]:
        """
        Return symbols this symbol depends on (outgoing edges).
        
        Args:
            symbol_name: Name of symbol to query
        
        Returns:
            List of node IDs this symbol calls/imports
        
        Requirement: 2.2
        """
        # Find all nodes with this symbol name
        source_nodes = self._node_index.get(symbol_name, set())
        
        callees = set()
        for node in source_nodes:
            # Get successors (outgoing edges)
            callees.update(self.graph.successors(node))
        
        return list(callees)
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """
        Return all external files this file depends on.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of file paths this file depends on
        
        Requirement: 2.3
        """
        # Find all nodes from this file
        file_nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get('file_path') == file_path
        ]
        
        # Get all dependencies
        dependent_files = set()
        for node in file_nodes:
            for successor in self.graph.successors(node):
                successor_file = self.graph.nodes[successor].get('file_path')
                if successor_file and successor_file != file_path:
                    dependent_files.add(successor_file)
        
        return list(dependent_files)
    
    def get_transitive_dependencies(
        self,
        symbol_name: str,
        max_depth: Optional[int] = None
    ) -> List[Tuple[str, int]]:
        """
        BFS traversal to get transitive dependencies.
        
        Args:
            symbol_name: Symbol to start from
            max_depth: Maximum depth to traverse (None = unlimited)
        
        Returns:
            List of (node_id, distance_from_root) tuples
        
        Requirement: 11
        """
        # Check cache
        cache_key = (symbol_name, max_depth)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Find starting nodes
        start_nodes = self._node_index.get(symbol_name, set())
        if not start_nodes:
            return []
        
        # BFS traversal
        visited = set()
        queue = deque([(node, 0) for node in start_nodes])
        results = []
        
        while queue:
            node, depth = queue.popleft()
            
            if node in visited:
                continue
            
            if max_depth is not None and depth > max_depth:
                continue
            
            visited.add(node)
            
            # Add to results (skip starting nodes)
            if depth > 0:
                results.append((node, depth))
            
            # Add successors to queue
            for successor in self.graph.successors(node):
                if successor not in visited:
                    queue.append((successor, depth + 1))
        
        # Cache result
        self._cache[cache_key] = results
        return results
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Find all cycles using NetworkX algorithms.
        
        Returns:
            List of cycles, each cycle is a list of node IDs
        
        Requirement: 12
        """
        try:
            # NetworkX built-in cycle detection
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def has_cycle(self, symbol_name: str) -> bool:
        """
        Check if symbol participates in any cycle.
        
        Args:
            symbol_name: Symbol to check
        
        Returns:
            True if symbol is in a cycle
        
        Requirement: 12.5
        """
        nodes = self._node_index.get(symbol_name, set())
        cycles = self.detect_cycles()
        
        for cycle in cycles:
            if any(node in cycle for node in nodes):
                return True
        
        return False
    
    def save(self):
        """
        Persist graph to CallGraphEdgeModel.
        
        Requirement: 15
        """
        with get_db_session(self.db_path) as session:
            # Delete existing edges for this session
            session.query(CallGraphEdgeModel)\
                .filter_by(session_id=self.session_id)\
                .delete()
            
            # Save all edges
            for from_node, to_node, data in self.graph.edges(data=True):
                from_attrs = self.graph.nodes[from_node]
                to_attrs = self.graph.nodes[to_node]
                
                edge = CallGraphEdgeModel(
                    session_id=self.session_id,
                    caller_file=from_attrs['file_path'],
                    caller_symbol=from_attrs['symbol_name'],
                    callee_file=to_attrs['file_path'],
                    callee_symbol=to_attrs['symbol_name'],
                    edge_type=data.get('edge_type', 'unknown'),
                    confidence=data.get('confidence', 1.0),
                    meta={'graph_version': self._graph_version}
                )
                session.add(edge)
            
            session.commit()
    
    def load(self):
        """
        Reconstruct graph from database.
        
        Requirement: 15.3
        """
        self.build_from_database()
    
    def update_from_files(self, modified_files: List[str]):
        """
        Incremental update for changed files.
        
        Args:
            modified_files: List of file paths that changed
        
        Requirement: 21
        """
        # Find nodes from modified files
        nodes_to_update = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get('file_path') in modified_files
        ]
        
        # Remove outgoing edges from these nodes
        edges_to_remove = []
        for node in nodes_to_update:
            edges_to_remove.extend(self.graph.out_edges(node))
        
        self.graph.remove_edges_from(edges_to_remove)
        
        # Clear cache for affected symbols
        self.clear_cache()
    
    def clear_cache(self):
        """
        Invalidate cached transitive results.
        
        Requirement: 18.5
        """
        self._cache.clear()
    
    def get_stats(self) -> Dict:
        """
        Get graph statistics.
        
        Returns:
            Dictionary with node count, edge count, etc.
        """
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'cached_queries': len(self._cache),
            'indexed_symbols': len(self._node_index),
            'session_id': self.session_id,
            'has_cycles': len(self.detect_cycles()) > 0
        }
