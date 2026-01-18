# Data Models & Schemas (Research Grade)

## 1. Graph Entities

### Nodes (Enhanced)
| Type | Attribute | Description |
|------|-----------|-------------|
| **Developer** | `profile_vector` | Embedding of bio/activity |
| **Commit** | `tfidf_vector` | Sparse vector of code tokens |
| **Skill** | `belief_mass` | DST Mass $\{m(S), m(\neg S), m(\Theta)\}$ |

### Edges (Weighted)
| Relation | Weight Logic |
|----------|--------------|
| `modifies` | TF-IDF Score ($W_{c,f}$) |
| `implies` | LLM Confidence $\rightarrow$ Mass Function |

## 2. API Response Schemas

### MCTS Trace Log
To analyze the "reasoning" of the agent, we log the tree search:
```json
{
  "iteration": 5,
  "selected_node": "commit:a3f2b",
  "ucb_score": 1.45,
  "simulated_reward": 0.8,
  "path_updates": ["node_1", "node_5"]
}
```

### Final Research Profile (JSON)
```json
{
  "developer": "username",
  "skills": [
    {
      "name": "Distributed Systems",
      "metrics": {
        "belief": 0.85,
        "plausibility": 0.92,
        "uncertainty": 0.07
      },
      "evidence_paths": [
        {
          "meta_path": "Dev->Commit->File->Skill",
          "weight": 0.76
        }
      ]
    }
  ]
}
```
