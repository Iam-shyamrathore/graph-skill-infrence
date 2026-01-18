# Research: Agentic Graph Exploration Strategy

**Topic:** Monte Carlo Tree Search (MCTS) & Reinforcement Learning
**Objective:** Define the theoretical basis for Component 2 (Agentic Exploration).
**Context:** Optimal decision-making for graph traversal under uncertainty constraints.

## 1. Problem Formulation: Graph Traversal as MDP
We formulate the skill discovery process as a **Markov Decision Process (MDP)** following the **DeepPath** framework [Xiong et al., 2017]:
- **State ($s_t$):** A representation $k_t = [e_t, e_{source}, B_t]$ where $e_t$ is the current entity embedding, $e_{source}$ is the developer, and $B_t$ is the current belief vector of skills.
- **Action ($a_t$):** Choosing a relation $r$ (meta-path step) from the current node's outgoing edges.
- **Transition ($T$):** Moving to a neighbor node via relation $r$.
- **Reward ($R_t$):** A multi-faceted reward function designed to balance accuracy, path length, and information novelty:
$$R = \alpha R_{acc} + \beta R_{eff} + \gamma R_{div}$$
  - **Accuracy ($R_{acc}$):** The semantic confidence provided by the LLM Reasoner for the inferred skill.
  - **Efficiency ($R_{eff}$):** Modeled as $1/L^2$ where $L$ is path depth, forcing the agent to find the most direct evidence.
  - **Diversity ($R_{div}$):** Measured as the Information Gain relative to the entropy of the current Global Belief Vector. Rewards discovery of "Far" skills (e.g., switching from Backend to DevOps).

## 2. Algorithm: MCTS for Reasoning with Trees (RwT)
We adopt the **Reasoning with Trees (RwT)** paradigm [COLING 2025] which uses MCTS to iteratively refine reasoning paths.

### 2.1 The Four Phases
1.  **Selection (Intelligent Search):**
    Nodes are selected using PUCT (Predictor + UCB). The prior $P(s,a)$ is a learned heuristic from Repo Stars and Language tags.

2.  **Expansion (Structural Constraint):**
    The explorer adheres strictly to the HIN Graph Schema $T_G$ to ensure only valid semantic relations are traversed.

3.  **Simulation (Chain-of-Thought Reasoner):**
    Instead of zero-shot inference, we use **CoT Reasoning**:
    - **Input**: The full reasoning path from the Developer node to the current leaf.
    - **Process**: LLM evaluates the *sequence* of actions (e.g., "Developer created repo X, then modified file Y in commit Z").
    - **Output**: 
        - $v$: Reward estimate.
        - $E$: Causal explanation for the skill inference.

4.  **Backpropagation:**
    The composite reward $R$ is propagated back through the reasoning tree, updating the Q-values of each state-action pair $(s, a)$.

## 3. Active Learning Criteria
To minimize expensive LLM calls, we use **Uncertainty Sampling**:
- If a skill has high **Belief** and low **Uncertainty** (via DST), we prune further exploration in that branch.
- Focus exploration on nodes that maximize the **Information Gain** regarding latent skills.

## 4. References
[1] "DeepPath: A Reinforcement Learning Method for Knowledge Graph Reasoning", EMNLP 2017.
[2] "Reasoning with Trees: Faithful Question Answering over Knowledge Graph", 2024.
[3] "ReKG-MCTS: Reinforcing LLM Reasoning on Knowledge Graphs", ACL 2024.
