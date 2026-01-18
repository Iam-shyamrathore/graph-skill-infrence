# Research: Advanced Graph Construction for Developer Profiling

**Topic:** Heterogeneous Information Network (HIN) Construction
**Objective:** Define the theoretical basis for Component 1 (Graph Construction) with academic rigor.
**Context:** Converting unstructured GitHub data into a semantically rich Heterogeneous Information Network.

## 1. Theoretical Foundation: Heterogeneous Information Networks (HIN)
We formally define the developer profile as a **Heterogeneous Information Network (HIN)**, denoted as $G = (V, E)$, with an entity type mapping $\phi: V \rightarrow \mathcal{A}$ and a relation type mapping $\psi: E \rightarrow \mathcal{R}$, where $|\mathcal{A}| > 1$ or $|\mathcal{R}| > 1$.

### 1.1 Schema Definition
The network schema $T_G = (\mathcal{A}, \mathcal{R})$ defines the permissible structure.
**Node Types ($\mathcal{A}$):**
- $D$: Developer
- $P$: Project (Repository)
- $C$: Commit (Atomic Change)
- $F$: File (Source Code)
- $S$: Skill (Latent Attribute)
- $I$: Issue (Task/Discussion)

**Meta-Paths:**
Meta-paths $\mathcal{P}$ define composite relations that capture semantic meaning [Sun et al., 2011].
- **Expertise Path ($D \xrightarrow{author} C \xrightarrow{modify} F \xrightarrow{contain} S$):** Connects a developer to a skill through code modifications.
- **Collaboration Path ($D_1 \xrightarrow{comment} I \xleftarrow{open} D_2$):** Connects developers via discussion.
- **Project Focus ($D \xrightarrow{commit} P \xrightarrow{use} L_{ang}$):** Connects developer to languages used.

## 2. Advanced Weighting Mechanisms

### 2.1 TF-IDF for Code Semantics
To quantify the "richness" of a commit $c$ regarding a file $f$, we adapt **TF-IDF**:
$$W_{c,f} = tf(t, c) \cdot idf(t, \mathcal{C})$$
Where:
- $t$ represents semantic tokens (imports, function calls) in the diff.
- $\mathcal{C}$ is the corpus of all commits in the graph.
This down-weights boilerplate changes (e.g., formatting) and up-weights semantic changes (e.g., `import torch`).

### 2.2 Proficiency Weight Modeling
We define the edge weight $W(d, s)$ (Developer $\to$ Skill) as an aggregated **Belief Score** derived from meta-path instances. Instead of a simple sum, we employ a PathSim-normalized evidence fusion strategy.

For each path $p$ matching meta-path $\mathcal{P}_{d \to s}$, we calculate its **Relative Strength**:
$$m_p(\{s\}) = \frac{2 \cdot \text{Weight}(p)}{\text{Visibility}(d) + \text{Popularity}(s)}$$
Where:
- $\text{Weight}(p)$: Product of TF-IDF and LLM confidence along the path.
- $\text{Visibility}(d)$: Total semantic weight of all edges originating from the developer.
- $\text{Popularity}(s)$: Global occurrence frequency of the skill in the graph.

The final proficiency score is the **Belief** resulting from the fusion of all paths using **Dempster's Rule of Combination**:
$$S(d, s) = \bigoplus_{p \in \mathcal{P}_{d \to s}} m_p$$
This normalization ensures that generic skills are penalized by their high popularity, while the DST fusion prevents score inflation from redundant evidence.

## 3. References
[1] Sun, Y., et al. "PathSim: Meta path-based top-k similarity search in heterogeneous information networks." VLDB 2011.
[2] "Heterogeneous Graph Neural Networks for Keyphrase Generation", EMNLP.
[3] "Developer Ranking with TF-IDF and PageRank", IEEE Trans. on Software Engineering.
