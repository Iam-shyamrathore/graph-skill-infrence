import argparse
import json
import os
import networkx as nx
from src.config import Config
from src.graph_builder import HINBuilder
from src.agentic_explorer import MCTSAgent
from src.confidence import ConfidenceCalculator

def save_profile(profile, username):
    os.makedirs("output", exist_ok=True)
    path = f"output/{username}_profile.json"
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"Profile saved to {path}")

import pickle

def save_graph(graph, username):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{username}_graph.pkl", "wb") as f:
        pickle.dump(graph, f)
    # nx.write_gpickle(graph, f"output/{username}_graph.gpickle")
    print(f"Graph saved to output/{username}_graph.gpickle")

def run_pipeline(username: str, iterations: int = 20):
    """
    Main entry point for the skill inference pipeline.
    Constructs the graph, runs MCTS exploration, and calculates confidence metrics.
    """
    # 1. Verification
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return None

    print(f"=== Starting Dynamic Profiling for User: {username} ===")
    
    # 2. Graph Construction
    print("\n[Phase 1] Building Heterogeneous Information Network...")
    builder = HINBuilder(username)
    graph = builder.build_raw_topology()
    
    # 3. Agentic Exploration
    print(f"\n[Phase 2] Agentic Exploration (MCTS) - Budget: {iterations} iters...")
    from src.llm_client import LLMClient
    llm = LLMClient()
    agent = MCTSAgent(graph, llm)
    
    agent.run_exploration(iterations=iterations)
    
    # 4. Confidence Calculation
    print("\n[Phase 3] Calculates Belief Mass Functions (Dempster-Shafer)...")
    calc = ConfidenceCalculator(graph)
    
    # Identify all Skill nodes found
    all_skills = [n for n, d in graph.nodes(data=True) if d.get('type') == 'skill']
    developer_node = f"dev:{username}"
    
    final_profile = {
        "developer": username,
        "skills": []
    }
    
    for skill_node in all_skills:
        skill_name = graph.nodes[skill_node].get('name')
        metrics = calc.compute_skill_confidence(developer_node, skill_node)
        
        # Filter low belief skills
        if metrics['belief'] > 0.05:
            final_profile["skills"].append({
                "name": skill_name,
                "metrics": metrics
            })
            
    # Sort by belief
    final_profile["skills"].sort(key=lambda x: x['metrics']['belief'], reverse=True)
    
    # 5. Output
    print(f"\n[Result] Identified {len(final_profile['skills'])} skills.")
    save_profile(final_profile, username)
    save_graph(graph, username)
    return final_profile

def main():
    parser = argparse.ArgumentParser(description="Graph-Theoretic Skill Inference System")
    parser.add_argument("--user", required=True, help="GitHub username to profile")
    parser.add_argument("--iterations", type=int, default=20, help="MCTS iterations")
    args = parser.parse_args()
    
    run_pipeline(args.user, args.iterations)

if __name__ == "__main__":
    main()
