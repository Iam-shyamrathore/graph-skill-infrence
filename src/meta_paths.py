import networkx as nx

class MetaPath:
    """
    Defines a semantic path pattern in the Heterogeneous Information Network.
    """
    def __init__(self, name: str, node_types: list[str], edge_types: list[str]):
        self.name = name
        self.node_types = node_types # e.g. ['developer', 'commit', 'file']
        self.edge_types = edge_types # e.g. ['contributes', 'modifies']
        
    def __repr__(self):
        return f"MetaPath({self.name}: {' -> '.join(self.node_types)})"

# Research-defined Meta-Paths
EXPERTISE_PATH = MetaPath(
    "ExpertiseCode",
    ['developer', 'repository', 'commit', 'file'],
    ['contributes', 'contains', 'modifies']
)

COLLABORATION_PATH = MetaPath(
    "Collaboration",
    ['developer', 'repository', 'commit'],
    ['contributes', 'contains']
)

class MetaPathWalker:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def find_paths(self, start_node: str, meta_path: MetaPath) -> list[list[str]]:
        """
        Finds all path instances in the graph matching the given meta-path schema.
        Returns a list of node_id sequences.
        """
        results = []
        self._dfs(start_node, meta_path, 0, [start_node], results)
        return results

    def _dfs(self, current_node: str, meta_path: MetaPath, depth: int, current_path: list, results: list):
        # Base case: if full path length reached
        if depth == len(meta_path.edge_types):
            results.append(list(current_path))
            return

        target_edge_type = meta_path.edge_types[depth]
        target_node_type = meta_path.node_types[depth + 1]

        for neighbor in self.graph.successors(current_node):
            edge_data = self.graph.get_edge_data(current_node, neighbor)
            node_data = self.graph.nodes[neighbor]
            
            # Type Check
            if edge_data.get('type') == target_edge_type and \
               node_data.get('type') == target_node_type:
                
                # Recurse
                current_path.append(neighbor)
                self._dfs(neighbor, meta_path, depth + 1, current_path, results)
                current_path.pop()

    def compute_path_sim(self, path_instance: list) -> float:
        """
        Computes the PathSim-like structural weight of a single path instance.
        Product of edge weights along the path.
        """
        weight = 1.0
        for i in range(len(path_instance) - 1):
            u, v = path_instance[i], path_instance[i+1]
            w = self.graph[u][v].get('weight', 1.0)
            weight *= w
        return weight
