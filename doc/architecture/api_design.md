# API Interface Design (Research Grade)

## 1. HIN Builder
```python
class HINBuilder:
    def build_with_tfidf(self, username: str) -> nx.DiGraph:
        """
        Builds the graph and computes TF-IDF vectors for all commit nodes
        relative to the repository corpus.
        """
        ...
```

## 2. MCTS Explorer
```python
class MCTSNode:
    def __init__(self, state):
        self.visits = 0
        self.value = 0.0
        self.children = {}

class MCTSAgent:
    def search(self, root_state, simulations: int = 50):
        """
        Runs MCTS simulations to select the optimal exploration path.
        """
        for _ in range(simulations):
            leaf = self.select(root_state)
            reward = self.simulate(leaf)
            self.backpropagate(leaf, reward)
        return self.best_action(root_state)
```

## 3. Dempster-Shafer Engine
```python
class DSTEngine:
    def create_mass_function(self, probability: float) -> dict:
        """
        Converts a raw probability into a Mass Function {Skill, ~Skill, Theta}.
        """
        ...

    def combine_evidence(self, mass_1: dict, mass_2: dict) -> dict:
        """
        Applies Dempster's Rule of Combination.
        """
        ...
```
