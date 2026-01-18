# Implementation Log: Step 8 - Deep Exploration Agent (DeepPath + RwT)

**Date:** January 2026
**Component:** Agentic Exploration (Advanced MCTS/RL)

## 1. Objectives
Transition the exploration strategy from a simple node-lookahead to a **Path-Aware Reasoning Tree**, incorporating state-of-the-art techniques from DeepPath (RL rewards) and RwT (MCTS for reasoning).

## 2. Technical Design

### 2.1 State Representation ($S_t$)
The state is no longer a single node ID. It consists of:
- **Current Node**: The entity being explored.
- **Reasoning Path**: The sequence of nodes/edges from the Developer to the current node.
- **Global Belief Vector**: The accumulated skill confidence scores discovered in the current MCTS session.

### 2.2 Re-weighted Reward Function
We replace the greedy max-confidence reward with a composite function:
$$R = R_{accuracy} + R_{efficiency} + R_{diversity}$$
- **Accuracy**: $LLM_{conf}$.
- **Efficiency**: $\lambda \cdot \frac{1}{Depth}$. Discourages deep, irrelevant paths.
- **Diversity**: $1 - \cos(\vec{B}, \vec{B}_{prev})$. Encourages exploring meta-paths that find *new* information relative to what the agent already "knows."

### 2.3 LLM as a Causal Reasoner
The `LLMClient` is upgraded to perform **Chain-of-Thought (CoT)**.
- **Input**: The full reasoning path (e.g., `Shyam -> graph-skill-inference -> Update MCTS Node -> agentic_explorer.py`).
- **Output**: 
    - `skill`: The identified technical skill.
    - `causal_evidence`: A textual explanation of why the path implies the skill.
    - `confidence`: Scalar probability.

## 3. Implementation Plan
1. **Modify `MCTSNode`**: Add `path` and `depth` attributes.
2. **Modify `MCTSAgent`**: 
    - Implement `compute_reward` with diversity and efficiency penalties.
    - Maintain a session-level `belief_vector` (NetworkX node cache).
3. **Modify `LLMClient`**: Update prompts to include path context and request explanations.
4. **Update `main.py`**: Ensure the pipeline propagates these richer rewards to the final profile.

## 4. References Code
- [agentic_explorer.py](file:///Users/shyam/Projects/graph-skill-inference/src/agentic_explorer.py)
- [llm_client.py](file:///Users/shyam/Projects/graph-skill-inference/src/llm_client.py)

**Status:** COMPLETED ✅
