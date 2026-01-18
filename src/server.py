from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import json
import os
import pickle
import networkx as nx
import requests
from .config import Config
from .main import run_pipeline

app = FastAPI()

# Track in-progress profiling tasks to avoid duplicates
profiling_tasks = set()

# GITHUB OAUTH CONFIG
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH ENDPOINTS ---

@app.get("/auth/github")
def login_github():
    """Redirects to GitHub for OAuth."""
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=user,repo"
    )

@app.get("/auth/callback")
def auth_callback(code: str):
    """Handles GitHub callback and exchanges code for token."""
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code
        },
        headers={"Accept": "application/json"}
    )
    data = token_res.json()
    if "access_token" not in data:
        raise HTTPException(status_code=400, detail="OAuth failed")
    
    token = data["access_token"]
    
    # Fetch user info to get the username
    user_res = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    ).json()
    username = user_res.get("login", "unknown")

    return RedirectResponse(f"{FRONTEND_URL}/?token={token}&user={username}")

# --- DATA ENDPOINTS ---

@app.get("/profile/{username}")
async def get_profile(username: str, background_tasks: BackgroundTasks):
    path = os.path.join("output", f"{username}_profile.json")
    
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
            
    # If not found, check if already profiling
    if username in profiling_tasks:
        return {"status": "processing", "message": "Inference engine is active. Manifold decoding in progress."}
    
    # Start background profiling
    profiling_tasks.add(username)
    background_tasks.add_task(trigger_profiling, username)
    
    return {"status": "accepted", "message": "Inference requested. Initializing MCTS exploration."}

def trigger_profiling(username: str):
    try:
        run_pipeline(username, iterations=15)
    except Exception as e:
        print(f"--- ERROR: Profiling failed for {username} ---")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Details: {str(e)}")
        # If it's a 401, it's almost certainly a missing/invalid GITHUB_TOKEN in Railway
        if "401" in str(e) or "BadCredentials" in type(e).__name__:
            print("CRITICAL: GITHUB_TOKEN is either missing or invalid in your Railway Environment Variables.")
    finally:
        if username in profiling_tasks:
            profiling_tasks.remove(username)

@app.get("/graph/{username}")
def get_graph(username: str):
    # (Existing graph conversion logic...)
    path = os.path.join("output", f"{username}_graph.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Graph not found")
        
    with open(path, "rb") as f:
        G = pickle.load(f)
    
    type_map = {
        'developer': 'dev',
        'repository': 'repo',
        'skill': 'skill',
        'commit': 'commit'
    }
    
    nodes = []
    for n, d in G.nodes(data=True):
        raw_type = d.get('type', 'unknown')
        group = type_map.get(raw_type, raw_type)
        
        # Determine best label
        label = d.get('name') or d.get('login') or n
        if group == 'dev':
            label = f"Developer: {label}"
        
        # Scaling
        val = 5
        if group == 'dev': val = 40 # Increased significantly for visibility
        elif group == 'skill': val = 15
        elif group == 'repo': val = 10
        
        nodes.append({
            "id": n,
            "group": group,
            "label": label,
            "val": val
        })
        
    links = []
    for u, v, d in G.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "type": d.get('type', 'rel')
        })
        
    return {"nodes": nodes, "links": links}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
