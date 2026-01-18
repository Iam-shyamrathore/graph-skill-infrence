# Implementation Log: Step 2 - Semantic Weighting Calculation

**Date:** January 2026
**Component:** Graph Edge Weighting (TF-IDF)

## 1. Objectives Achieved
1.  **Code Semantics Engine:** Created `TFIDFCalculator` in `src/tfidf.py`.
2.  **Corpus Fitting:** The system now aggregates all commit patches to form a developer-specific vocabulary.
3.  **Weighted Graph:** The `HINBuilder` now computes and assigns a scalar weight $w \in [0.1, 1.0]$ to every `modifies` edge.

## 2. Mathematical Logic (TF-IDF)

### 2.1 Preprocessing
Raw `git diff` output is noisy. We apply a filter:
- **Filtering:** Keep lines starting with `+`. Remove `+++` metadata headers.
- **Tokenization:** Regex `\b\w\w+\b` captures variables like `get_user_data` while ignoring punctuation logic.

### 2.2 Weighting Formula
We utilize the Term Frequency-Inverse Document Frequency (TF-IDF) statistic to measure the importance of a code change.
$$W(commit, file) = \log(1 + \sum_{t \in patch} tf(t) \cdot idf(t))$$
- **High Weight:** Rare keywords (e.g., `TensorFlow`, `useEffect`, specific algo names).
- **Low Weight:** Common keywords across all commits (e.g., `print`, `var`, `TODO`).
- **Normalization:** We squash the unbounded sum using a logarithmic scale and clip it to $[0.1, 1.0]$ to serve as a probability proxy for the graph traversal.

## 3. Algorithm: HIN Construction v2
1.  **Iterate** Step 1 to build topology.
2.  **Collect** all raw `patch` content into a list (Corpus).
3.  **Fit** `TfidfVectorizer` on Corpus.
4.  **Re-iterate** edges:
    - If `type == 'modifies'`:
        - Transform patch to vector.
        - Sum non-zero elements.
        - Normalize and update edge weight.

## 4. References & Code
- `src/tfidf.py`: [Class TFIDFCalculator](file:///Users/shyam/Projects/graph-skill-inference/src/tfidf.py)
- `src/graph_builder.py`: [Modified Build Method](file:///Users/shyam/Projects/graph-skill-inference/src/graph_builder.py#L93)
