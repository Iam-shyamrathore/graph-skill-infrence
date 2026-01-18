# Research: PathSim-Augmented Skill Weighted Propagation

**Topic:** HIN Semantic Proximity (Adapted from Sun et al., 2011)
**Objective:** Incorporate peer-visibility and self-visibility into skill confidence scores.

## 1. The PathSim Similarity Metric
PathSim is defined for two objects $x, y$ of the same type under a symmetric meta-path $P$:
$$s(x, y) = \frac{2 \times M_{x,y}}{M_{x,x} + M_{y,y}}$$
Where $M_{x,y}$ is the number of path instances between $x$ and $y$.

## 2. Adaptation for Skill Inference (SIIN-PathSim)
Since Developer ($D$) and Skill ($S$) are different types, we adapt PathSim to measure the **Strength of Association**:

### 2.1 Meta-Path Symmetry
We define the symmetric meta-path for Expertise as $P = D \to C \to F \to \text{Skill} \leftarrow F' \leftarrow C' \leftarrow D'$.
To calculate the confidence of $D$ having $S$, we evaluate the projection:
$$Conf(D, S) = \frac{2 \times \text{Volume}(D \xrightarrow{Expertise} S)}{\text{Visibility}(D) + \text{Popularity}(S)}$$

### 2.2 Parameters
1. **$\text{Volume}(D \to S)$**: Sum of TF-IDF weighted paths from developer to the specific skill node.
2. **$\text{Visibility}(D)$**: Total semantic weighted activity of the developer across all files.
3. **$\text{Popularity}(S)$**: How often this skill appears across the entire graph/corpus. 

## 3. Implementation in DST
The SIIN-PathSim score will replace the simple product in the Mass Function assignment:
$$m(\{S\}) = \sigma(\text{PathSim}(D, S))$$
$m(\Theta) = 1 - m(\{S\})$

This prevents "Generic" skills (like 'Clean Code' or 'Git') from getting high belief scores just because they appear often, as their high **Popularity ($S$)** will normalize the score down.
