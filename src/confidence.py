import networkx as nx
import numpy as np
from .meta_paths import MetaPathWalker, EXPERTISE_PATH

class MassFunction:
    """
    Represents a Basic Probability Assignment (BPA) / Subjective Opinion.
    Dict keys: 's' (Skill/Belief), 'ns' (Not Skill/Disbelief), 'theta' (Uncertainty)
    """
    def __init__(self, masses: dict):
        self.m = masses
        total = sum(self.m.values())
        if abs(total - 1.0) > 0.001:
             for k in self.m:
                 self.m[k] /= total

    def __getitem__(self, key):
        return self.m.get(key, 0.0)

    @staticmethod
    def discount(m_source, m_target):
        """
        Subjective Logic Discounting Operator (Trust Propogation).
        Represents the opinion: Source trusts Target who says Prop is true.
        """
        b_s = m_source['s']
        b_t = m_target['s']
        d_t = m_target['ns']
        u_t = m_target['theta']
        
        # SL Discounting Logic
        new_b = b_s * b_t
        new_d = b_s * d_t
        new_u = (1.0 - b_s) + (b_s * u_t)
        
        return MassFunction({'s': new_b, 'ns': new_d, 'theta': new_u})

    @staticmethod
    def combine(m1, m2):
        """
        Yager's Rule of Combination.
        Reallocates conflict mass 'K' to Uncertainty (theta) instead of normalizing it away.
        Better for KG reasoning where sources are varied but not authoritative.
        """
        # Calculate un-normalized intersections
        raw_s = (m1['s'] * m2['s'] + m1['s'] * m2['theta'] + m1['theta'] * m2['s'])
        raw_ns = (m1['ns'] * m2['ns'] + m1['ns'] * m2['theta'] + m1['theta'] * m2['ns'])
        raw_theta = (m1['theta'] * m2['theta'])
        
        # Conflict K (Intersection of S and ~S)
        k_conflict = (m1['s'] * m2['ns'] + m1['ns'] * m2['s'])
        
        # Yager's Improvement: Add conflict to theta
        new_s = raw_s
        new_ns = raw_ns
        new_theta = raw_theta + k_conflict
        
        return MassFunction({'s': new_s, 'ns': new_ns, 'theta': new_theta})

    def belief(self, hypothesis):
        return self.m.get(hypothesis, 0.0)

    def plausibility(self, hypothesis):
        return self.m.get(hypothesis, 0.0) + self.m.get('theta', 0.0)

class ConfidenceCalculator:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.walker = MetaPathWalker(graph)

    def compute_skill_confidence(self, developer_node, skill_node) -> dict:
        """
        Aggregates evidence from all paths using DST.
        """
        # 1. Find all evidence paths
        # Note: Meta-path walker defines shape, but MCTS added specific 'implies' edges.
        # We need a meta-path that includes the 'implies' edge.
        # Let's dynamically construct it or just use simple paths for the prototype.
        
        try:
            paths = list(nx.all_simple_paths(self.graph, developer_node, skill_node, cutoff=5))
        except nx.NetworkXNoPath:
            return {'belief': 0.0, 'plausibility': 0.0, 'uncertainty': 1.0}

        # 2. Calculate Visibility Denominators (PathSim adaptation)
        # Visibility(D): Total activity of developer in the graph
        dev_visibility = sum(
            self.graph[u][v].get('weight', 1.0) 
            for u, v in self.graph.edges(developer_node)
        )
        # Popularity(S): How many nodes point to this skill
        skill_popularity = sum(
            self.graph[u][skill_node].get('weight', 1.0)
            for u in self.graph.predecessors(skill_node)
        )

        # 3. Convert each path to a Mass Function using Discounting
        masses = []
        for path in paths:
            # We treat the path as a sequence of opinions
            # Developer trusts Repository -> Repository trusts Commit -> Commit trusts File -> File implies Skill
            
            # Start with an initial "Trust" opinion (The Developer's inherent visibility)
            # Normalizing visibility to a 0-1 belief score
            dev_belief = min(0.95, dev_visibility / 100.0) # Heuristic baseline
            path_opinion = MassFunction({'s': dev_belief, 'ns': 0.0, 'theta': 1.0 - dev_belief})
            
            # Discount along the path
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_weight = self.graph[u][v].get('weight', 0.5)
                
                # Treat each edge as an opinion provided by node 'u' about node 'v'
                edge_m = MassFunction({'s': edge_weight, 'ns': 0.0, 'theta': 1.0 - edge_weight})
                path_opinion = MassFunction.discount(path_opinion, edge_m)
            
            # Final Normalization Step: Global Popularity of Skill
            # If a skill is extremely common (Git), we discount the final belief
            skill_generic_penalty = 1.0 / (1.0 + np.log1p(skill_popularity))
            final_m = MassFunction({
                's': path_opinion['s'] * skill_generic_penalty,
                'ns': path_opinion['ns'],
                'theta': 1.0 - (path_opinion['s'] * skill_generic_penalty + path_opinion['ns'])
            })
            
            masses.append(final_m)

        if not masses:
            return {'belief': 0.0, 'plausibility': 0.0, 'uncertainty': 1.0}

        # 4. Fuse Evidence using Yager's Rule
        fused = masses[0]
        for m in masses[1:]:
            fused = MassFunction.combine(fused, m)

        return {
            'belief': fused.belief('s'),
            'plausibility': fused.plausibility('s'),
            'uncertainty': fused['theta'],
            'path_count': len(paths),
            'math_model': 'Josang-Yager-Hybrid'
        }
