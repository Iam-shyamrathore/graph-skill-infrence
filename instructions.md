# Project Instructions & Prompt Consistency

This file contains instructions and standard prompts to ensure consistency across the project's documentation and code generation.

## General Guidelines
- All documentation must be in Markdown (`.md`) format.
- All documentation files must be stored in the `doc/` directory.
- Code should follow the architecture defined in Phase 2.
- Research documents should cite relevant concepts and be formatted for easy conversion to the final paper.

## Prompt Templates

### Research Summary Prompt
When summarizing research for a topic:
```text
**Topic:** [Topic Name]
**Objective:** Define the theoretical basis for [Component].
**Key Concepts:**
- Concept 1
- Concept 2
**Mathematical Formulations:**
- [Equation 1]
- [Equation 2]
**References/Citations:**
- [Reference 1]
```

### LLM Agent Prompt (Skill Inference)
To be used by the Agentic Exploration Component:
```text
System Context:
"You are analyzing developer activity to infer technical skills.
Be specific: 'PostgreSQL Query Optimization' not 'databases'"

Current Evidence:
{formatted_features}

Previously Identified Skills:
{skills_so_far}

Task:
Identify skills demonstrated by this evidence.
Output JSON:
[
  {
    "skill": "Skill Name",
    "confidence": 0.0-1.0,
    "reasoning": "Specific evidence..."
  }
]
```
