# System Architecture: Graph-Theoretic Skill Inference System

**Date:** January 2026
**Version:** 2.0 (Research Grade)

## 1. High-Level Architecture
The system implements the **SIIN (Skill Inference Information Network)** framework, featuring an MCTS-driven agent and a Dempster-Shafer confidence engine.

```mermaid
graph TD
    User([User Input: username]) --> API[GitHub API Client]
    API --> Builder[HIN Builder Engine]
    Builder --> G_Raw[Heterogeneous Graph (NetworkX)]
    
    subgraph Agentic Exploration (MCTS)
        G_Raw --> Root[Root State]
        Root --> Select[MCTS Selection (UCB)]
        Select --> Expand[Expansion]
        Expand --> Sim[Simulation (LLM Policy)]
        Sim --> Back[Backpropagation]
        Back --> Select
    end
    
    Back --> |Converged| G_Aug[Augmented Belief Graph]
    G_Aug --> DST[Dempster-Shafer Engine]
    DST --> Profile[Skill Profile (JSON)]
```

## 2. Component Analysis

### 2.1 HIN Builder Engine (`src.graph_builder`)
- **Responsibilities:**
    - Construct the Heterogeneous Information Network (HIN).
    - Compute **TF-IDF weights** for Code-Commit edges.
    - Identify instances of defined **Meta-Paths**.

### 2.2 Agentic Exploration Engine (`src.agentic_explorer`)
- **Core Logic: Monte Carlo Tree Search (MCTS)**
    - **State:** Current subgraph snapshot.
    - **Action:** Querying a specific node for latent skills.
    - **Policy $\pi(s)$:** LLM-based predictor for potential skill value.
    - **Reward:** Information Gain (Entropy Reduction).

### 2.3 Confidence Engine (`src.confidence`)
- **Core Logic: Dempster-Shafer Theory (DST)**
    - **Mass Assignment:** Convert path weights to Basic Probability Assignments (BPAs).
    - **Fusion:** Apply **Dempster's Rule of Combination** ($\oplus$) to aggregate evidence.
    - **Output:** Belief ($Bel$) and Plausibility ($Pl$) intervals.

## 3. Technology Stack
- **Graph:** NetworkX 3.2.1
- **Math:** NumPy / SciPy (for matrix operations)
- **AI:** Google Gemini 2.0 Flash
- **Viz:** Matplotlib (Force-directed layouts)
