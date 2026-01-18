# SIIN: The Definitive Architecture Booklet
**Level: Technical Deep-Dive**

This document serves as the "Architecture Booklet" for the Skill Inference Information Network (SIIN). It details the minute semantic, algorithmic, and mathematical design decisions of the codebase.

---

## 1. Graph Ontology: The HIN Schema
The core of the system is a **Heterogeneous Information Network (HIN)**. Unlike a simple social graph, a HIN preserves the multi-typed semantics of software development.

### 1.1 Node Dictionary
| Node Type | ID Format | Key Attributes |
| :--- | :--- | :--- |
| **Developer ($D$)** | `dev:{username}` | `name`, `visibility` |
| **Repository ($P$)** | `repo:{org/name}` | `stars`, `languages` (dict), `topics` (list), `description` |
| **Commit ($C$)** | `commit:{hash}` | `message`, `timestamp`, `richness` (float) |
| **File ($F$)** | `file:{path}` | `extension`, `semantic_weight` (TF-IDF) |
| **Skill ($S$)** | `skill:{name}` | `name`, `category` |

### 1.2 Edge Semantics
| Edge Type | Direction | Physics/Weight |
| :--- | :--- | :--- |
| `contributes` | $D \to P$ | Log-scaled repositories activity ($1 + \ln(commits)$). |
| `contains` | $P \to C$ | Baseline 1.0. |
| `modifies` | $C \to F$ | **Semantic Richness**: TF-IDF weight of the code patch. |
| `implies` | $F \to S$ | LLM-inferred confidence $[0, 1]$. |

---

## 2. Ingestion & Semantic Filtering
The `src/graph_builder.py` and `src/tfidf.py` modules handle the transformation of raw GitHub stream-data into weighted edges.

### 2.1 The GitHubFetcher
- **Rate Limit Resilience**: Implements a retry-on-403 logic with 60-second sleep intervals.
- **Deduplication**: Filters out forks and merge commits to ensure "original" expertise is captured.
- **Stats Extraction**: Parses individual `patch` data to extract added/deleted lines for semantic analysis.

### 2.2 TF-IDF Vectorization
We treat each code patch as a "Document".
1. **Tokenization**: Filter comments and boilerplate (e.g., `import`, `version`).
2. **Frequency Analysis**: $TF(t, d)$ measures term frequency in a patch. $IDF(t, D)$ measures rarity across all captured commits.
3. **Weighting**: $W = TF \times IDF$. High weights are assigned to niche technical terms (e.g., `transformers`, `fastapi`, `pthread_create`) while generic terms (e.g., `var`, `if`) are suppressed.

---

## 3. The Deep Exploration Agent (DeepPath)
Implemented in `src/agentic_explorer.py`, this engine performs a guided search over the HIN.

### 3.1 MDP State Representation
- **State ($s_t$)**: A tuple of `(current_node, reasoning_path, global_belief)`.
- **Action ($a_t$)**: Selecting an outgoing edge (Meta-path expansion).

### 3.2 PUCT Selection Algorithm
We use the AlphaZero-style Predictor Upper Confidence Bound applied to Trees:
$$v(s, a) = Q(s, a) + C_{puct} \cdot P(s, a) \cdot \frac{\sqrt{\sum N}}{1 + n}$$
- **Prior $P(s, a)$**: Heuristically boosted for repositories with high stars or matching language tags.
- **Search Intensity**: Default 20 iterations ensures the agent reaches leaf nodes ($S$) without exhaustive traversal.

### 3.3 Multi-Faceted Reward ($R_{total}$)
To prevent the agent from getting "stuck" on generic skills (e.g., Python), we apply:
1. **Accuracy ($R_{acc}$)**: The LLM's direct confidence score for an inferred skill.
2. **Efficiency ($R_{eff}$)**: $1/Depth^2$ - Favors direct expertise evidence over long-hop chains.
3. **Diversity ($R_{div}$)**: A "novelty bonus" proportional to the number of *new* skills identified in the current session.

---

## 4. Confidence & Evidence Fusion (Josang-Yager)
Located in `src/confidence.py`, this is the "Rigorous Core" of the system.

### 4.1 Subjective Logic (SL) Opinions
Every evidence chain is mapped to an opinion $\omega = (b, d, u, a)$:
- **Belief ($b$)**: Normalized evidence weight.
- **Uncertainty ($u$)**: $1 - b$.

### 4.2 Trust Propagation (Discounting)
For a path $D \to P \to \dots \to S$, we apply the **Josang Discounting Operator** $\otimes$:
$$\omega_{p} = \omega_{e_1} \otimes \omega_{e_2} \otimes \dots \otimes \omega_{S}$$
Minute Detail: $(1-b_1)$ acts as the uncertainty floor. If a repository has low visibility, no amount of leaf-node evidence can create high confidence.

### 4.3 Conflict Reallocation (Yager's Rule)
When combining path $p_1$ and $p_2$, we calculate conflict $K = b_1 \cdot d_2 + d_1 \cdot b_2$.
- **Dempster (Removed)**: $1/(1-K)$ - Normalizes away conflict (Certainty Inflation).
- **Yager (Implemented)**: $u_{new} = u_1 u_2 + K$. Conflict is explicitly treated as **Ignorance**. If two repos contradict on a skill, the system reports **lower confidence**, not higher.

---

## 5. API & Data Contracts

### 5.1 Profile Schema (JSON)
```json
{
  "developer": "...",
  "skills": [
    {
      "name": "Distributed Systems",
      "metrics": {
        "belief": 0.85, 
        "plausibility": 0.95,
        "uncertainty": 0.10,
        "path_count": 3
      },
      "causal_link": "Code modifications in repo X involving pthreads/locks..."
    }
  ]
}
```

### 5.2 Server Architecture (FastAPI)
- **Non-blocking Execution**: The MCTS exploration runs in a separate thread group to prevent blocking the Event Loop.
- **Caching**: Skill profiles are cached for 24 hours to mitigate GitHub rate limits.
