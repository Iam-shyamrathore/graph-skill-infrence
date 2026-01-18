# Research: Rigorous Confidence Calculation

**Topic:** Subjective Logic (SL) & Evidence Combination in KGs
**Objective:** Replace standard DST with a Trust-Aware reasoning framework.

## 1. Theoretical Foundation: Subjective Logic
Standard DST [Shafer, 1976] assumes independent evidence sources. In Knowledge Graphs, paths often share context. We adopt **Subjective Logic** [Jøsang, 2016] to represent evidence as an **Opinion** $\omega = (b, d, u, a)$:
- $b$: **Belief** (Evidence supporting the skill).
- $d$: **Disbelief** (Evidence refuting the skill).
- $u$: **Uncertainty** (Ignorance/Entropy).
- $a$: **Base Rate** (Prior probability of a skill in the population).

## 2. Advanced Mathematical Improvements

### 2.1 The Discounting Operator (Path Reliability)
A path $p: D \to \dots \to S$ is a chain of "Trust." Instead of simple weight multiplication, we use the **Discounting Operator** $\otimes$ to model trust decay:
$$\omega_{p} = \omega_{e_1} \otimes \omega_{e_2} \otimes \dots \otimes \omega_{s}$$
This ensuring that if an intermediate repository has low visibility, the final skill evidence is significantly discounted.

### 2.2 Consensus Operator vs. Dempster’s Rule
Dempster’s rule of combination often yields counter-intuitive results under high conflict ($K \to 1$). We implement the **Belief Fusion (Consensus) Operator**:
- **Consensus ($\oplus$):** Fuses independent opinions by reinforcing agreement and reducing uncertainty.
- **Compromise:** Used when observers have different expertise.

### 2.3 Conflict Handling (Yager’s Principle)
While Dempster normalizes conflict away, we adopt **Yager's Rule for KG Evidence**. Conflicting mass is reallocated to **Uncertainty ($u$)** rather than distributed among belief categories. This prevents "Artificial Certainty" when two high-confidence sources disagree.

## 3. Drastic Improvements Identified
1. **From Global Normalization to Scalar Reallocation**: Shift from $1/(1-K)$ to $m(\Theta) \mathrel{+}= K$.
2. **Base-Rate Awareness**: Using $a$ (global skill popularity) to ground the profile in reality.
3. **Path Dependency Modeling**: Mapping opinions to **Dirichlet Distributions** to handle the scarcity of evidence in small repositories.

## 4. References
[1] Shafer, G. "A Mathematical Theory of Evidence", 1976.
[2] Jøsang, A. "Subjective Logic: A Formalism for Reasoning Under Uncertainty", 2016.
[3] "Evidence Combination in Knowledge Graphs using DST", IEEE Transactions.
[4] Josang, A., "Subjective Logic for Trust Evaluation in Social Networks", IJCAI.
