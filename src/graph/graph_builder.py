import networkx as nx 
import jedi
from typing import List, Dict, Tuple
from joblib import Parallel, delayed
from src.utils.config.logger_config import logger
from src.utils.code_parsing import (
    find_python_files,
    parse_source,
    get_definitions_relationships
)

class GraphBuilder:
    def __init__(self, project_root):
        self.project_root = project_root
        self.project = jedi.Project(project_root)
        self.graph = nx.DiGraph()
        self.definitions = {}
        self.calls = []

        
    def build(self):
        """
        Build a call graph for all Python files under the project_root directory.
        The graph is represented as a NetworkX directed graph (DiGraph):
        - Nodes represent definitions (functions, methods, classes) with their properties.
        - Edges represent relationships:
            "nested": a definition declared inside another (e.g., method inside a class).
            "call": a function/method call from one definition to another.
        Returns the constructed graph.
        """
        # Create nodes: Gather all definitions from all Python files
        logger.info(f"PROJECT ROOT: {self.project_root}")

        file_source_tuple_list = Parallel(n_jobs=-1)(delayed(self._read_file)(file_path) 
                                      for file_path in find_python_files(self.project_root))
        

        for source, file_path in file_source_tuple_list:
            defs, calls_list = self._process_file(source, file_path)

            for def_id, info in defs.items():
                self.definitions.update(defs)
                self.graph.add_node(def_id, **info)

            self.calls.extend(calls_list)
        
        self._add_nested_edges()
        self._add_call_edges()
        self._add_inheritance_edges()

        return self.graph
    
    def _read_file(self, file_path: str) -> Tuple[str, str]:
        """
        Reads the content of a single file.

        Args:
            file_path (str): Path to the file to be read.

        Returns:
            Dict[str, str]: A dictionary with the file path as key and file content as value.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), file_path
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        
        
    def _process_file(self, source, file_path) -> Tuple:
        """
        Process a single file, returning definitions and calls.
        """
        tree = parse_source(source, str(file_path))
        defs, calls_list = get_definitions_relationships(
            source=source, 
            tree=tree, 
            file_path=str(file_path), 
            project=self.project
        )
        return defs, calls_list
    
   

    def _add_nested_edges(self):
        for def_id, info in self.definitions.items():
            parent_id = info.get('parent_id')
            if parent_id:
                self.graph.add_edge(def_id, parent_id, relation='nested_in')

    def _add_call_edges(self):
        for call in self.calls:
            caller_id = call.get("caller_id")
            candidate_id = call.get("candidate_id")
            if caller_id in self.graph.nodes and candidate_id in self.graph.nodes:
                self.graph.add_edge(caller_id, candidate_id, relation='call')

    def _add_inheritance_edges(self):
        for def_id, info in self.definitions.items():
            if info['type'] == 'class' and info['inherits_from']:
                for base_class in info['inherits_from']:
                    if base_class in self.graph.nodes:
                        self.graph.add_edge(def_id, base_class, relation='inherits_from')

