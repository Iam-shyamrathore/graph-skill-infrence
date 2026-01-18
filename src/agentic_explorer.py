import numpy as np
import networkx as nx
from .llm_client import LLMClient

class MCTSNode:
    def __init__(self, name, parent=None, prior=1.0, depth=0):
        self.name = name # Node ID in the HIN (e.g., 'commit:abc')
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0 # Accumulated reward (InfoGain)
        self.prior = prior # P(s, a) Heuristic Probability
        self.untried_actions = [] # Neighbors in HIN not yet in Tree
        self.depth = depth
        
        # Track the reasoning path: list of node descriptions
        self.path_context = parent.path_context + [name] if parent else [name]

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.414):
        """
        Selects child using PUCT (Predictor + UCB).
        """
        choices_weights = [
            (child.value / (child.visits + 1e-6)) + 
            c_param * child.prior * np.sqrt(self.visits) / (1 + child.visits)
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

class MCTSAgent:
    def __init__(self, graph: nx.DiGraph, llm_client: LLMClient):
        self.graph = graph
        self.llm = llm_client
        self.root = MCTSNode("root")
        
        # Initialize session tracking for Diversity reward
        self.session_skills = set()
        
        # Initialize root actions with 'commit' and 'repository' nodes
        nodes = [n for n, d in graph.nodes(data=True) if d.get('type') in ['commit', 'repository']]
        nodes.sort(key=lambda x: 1 if 'repo' in x else 0) 
        self.root.untried_actions = nodes

    def select(self, node):
        while not node.is_fully_expanded():
            if len(node.untried_actions) > 0:
                return self.expand(node)
            else:
                if not node.children:
                     return node
                node = node.best_child()
        return node

    def expand(self, node):
        action_node_id = node.untried_actions.pop()
        
        # Calculate Heuristic Prior
        prior = 1.0
        node_data = self.graph.nodes[action_node_id]
        n_type = node_data.get('type')
        
        if n_type == 'repository':
            prior = 2.0 
            stars = node_data.get('stars', 0)
            prior += np.log1p(stars)
            
            langs = node_data.get('languages', {})
            if 'Python' in langs or 'Jupyter Notebook' in langs or 'Java' in langs:
                prior += 2.0
        elif n_type == 'commit':
            prior = 0.5 
            
        child_node = MCTSNode(action_node_id, parent=node, prior=prior, depth=node.depth + 1)
        node.children.append(child_node)
        return child_node

    def simulate(self, node):
        """
        Simulation Phase: Evaluate the node using CoT LLM Reasoner.
        Returns a rich reward based on Accuracy, Efficiency, and Diversity.
        """
        node_data = self.graph.nodes[node.name]
        
        context = {
            "type": node_data.get('type'),
            "message": node_data.get('message', ''),
            "description": node_data.get('description', ''),
            "topics": node_data.get('topics', []),
            "languages": node_data.get('languages', {}),
            "diff_summary": self._get_diff_summary(node.name) if node_data.get('type') == 'commit' else ""
        }
        
        print(f"  [MCTS] Simulating Path: {' -> '.join(node.path_context[-3:])}...")
        skills = self.llm.infer_skills(context, reasoning_path=node.path_context)
        
        if not skills:
            return 0.0
            
        # 1. Accuracy Reward (R_acc)
        max_conf = max([s.get('confidence', 0) for s in skills]) if skills else 0.0
        
        # 2. Efficiency Reward (R_eff): Penalize depth
        # Formula: 1 / Depth^2
        r_eff = 1.0 / (node.depth**2) if node.depth > 0 else 1.0
        
        # 3. Diversity Reward (R_div): Reward finding NEW skills
        new_skills_count = sum(1 for s in skills if s['skill'] not in self.session_skills)
        r_div = new_skills_count / len(skills) if skills else 0.0
        
        # Update session memory
        for s in skills:
            self.session_skills.add(s['skill'])
            
        # Composite Reward: α*R_acc + β*R_eff + γ*R_div
        # Weights: 0.6 Acc, 0.2 Eff, 0.2 Div
        total_reward = (0.6 * max_conf) + (0.2 * r_eff) + (0.2 * r_div)
        
        # Persist results to Graph
        self._update_graph_with_skills(node.name, skills)
        
        return total_reward

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    def run_exploration(self, iterations=10):
        print(f"--- Starting Advanced MCTS Exploration ({iterations} iterations) ---")
        self.session_skills = set() # Reset session memory
        for i in range(iterations):
            print(f"Iter {i+1}:")
            leaf = self.select(self.root)
            reward = self.simulate(leaf)
            self.backpropagate(leaf, reward)
            print(f"  Result: Reward={reward:.2f}")

    def _get_diff_summary(self, commit_node_id):
        """Helper to aggregate diffs from outgoing edges."""
        summary = ""
        for _, v, data in self.graph.out_edges(commit_node_id, data=True):
            if data.get('type') == 'modifies':
                summary += f"\nFile: {v}\nPatch: {data.get('patch_content', '')[:200]}..." 
        return summary

    def _update_graph_with_skills(self, source_node, skills):
        """Adds Skill nodes and Implies edges to the graph."""
        # Calculate Semantic Richness of the Commit (Sum of TF-IDF weights of modified files)
        commit_richness = 0.0
        for _, _, data in self.graph.out_edges(source_node, data=True):
            if data.get('type') == 'modifies':
                commit_richness += data.get('weight', 0.0)
        
        # Clip richness to meaningful range (e.g., 0.5 to 1.5 multiplier) or just use as factor
        # Research Heuristic: Richer commits = More reliable evidence
        # We start with a baseline richness of 1.0 if no files (e.g. merge commit)
        if commit_richness < 0.1: commit_richness = 0.5 
        if commit_richness > 2.0: commit_richness = 2.0

        for s in skills:
            skill_name = s['skill']
            base_conf = s['confidence']
            
            # Adjusted Confidence: LLM Confidence * Evidence Richness
            final_weight = min(0.99, base_conf * commit_richness)
            
            skill_id = f"skill:{skill_name.replace(' ', '_')}"
            
            if not self.graph.has_node(skill_id):
                self.graph.add_node(skill_id, type="skill", name=skill_name)
            
            # Edge: Commit -> Skill
            self.graph.add_edge(
                source_node, 
                skill_id, 
                type="implies", 
                weight=final_weight,
                reasoning=s.get('reasoning', '')
            )
