import networkx as nx
from github import Github, GithubException
from tqdm import tqdm
import time
from .config import Config
from .tfidf import TFIDFCalculator

class GitHubFetcher:
    """
    Handles interactions with the GitHub API to retrieve raw data for the HIN.
    Implements rate limiting and partial data fetching.
    """
    def __init__(self):
        Config.validate()
        self.client = Github(Config.GITHUB_TOKEN, timeout=60)
        self.user_cache = {}

    def get_user_data(self, username: str) -> dict:
        """
        Fetches basic user profile data.
        """
        try:
            user = self.client.get_user(username)
            return {
                "login": user.login,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "bio": user.bio,
                "public_repos": user.public_repos
            }
        except GithubException as e:
            print(f"Error fetching user {username}: {e}")
            return {}

    def get_top_repos(self, username: str, limit: int = Config.MAX_REPOS) -> list:
        """
        Fetches top N repositories sorted by updated_at time (recency).
        Rationale: Recent activity is more relevant for current skill inference.
        """
        user = self.client.get_user(username)
        # Optimization: Fetch 100 per page to minimize pagination calls
        repos = user.get_repos(sort="updated", direction="desc")
        
        results = []
        # Use total=None because we might skip forks
        pbar = tqdm(repos, desc="Scanning Repos", total=limit*2) 
        
        for repo in pbar:
            if len(results) >= limit:
                pbar.close()
                break
                
            pbar.set_description(f"Checking {repo.name[:20]}")
            
            if repo.fork:
                continue 
                
            try:
                # Add explicit timeouts for secondary calls if possible, 
                # or just wrap in broad try-except to prevent hanging
                results.append({
                    "name": repo.full_name,
                    "language": repo.language,
                    "languages": repo.get_languages(), # API Call
                    "topics": repo.get_topics(), # API Call
                    "stars": repo.stargazers_count,
                    "description": repo.description,
                    "object": repo 
                })
            except Exception as e:
                print(f"\n[Warning] Skipped metadata for {repo.name}: {e}")
                # Fallback implementation
                results.append({
                    "name": repo.full_name,
                    "language": repo.language,
                    "languages": {},
                    "topics": [],
                    "stars": repo.stargazers_count,
                    "description": repo.description,
                    "object": repo
                })
        return results

    def get_commits(self, repo_obj, author: str, limit: int = Config.MAX_COMMITS) -> list:
        """
        Fetches commits for a specific repository authored by the target user.
        Includes stats (additions/deletions) and files modified.
        """
        commits = repo_obj.get_commits(author=author)
        results = []
        
        try:
            for commit in commits[:limit]:
                # We need detailed data for tf-idf (patch/diff)
                # Note: getting files for every commit is expensive (N+1 API calls)
                # Optimization: We sleep briefly to avoid secondary rate limits
                time.sleep(0.25)
                
                # Retry logic for fetching files (network sensitive)
                files_data = []
                attempts = 0
                max_retries = 3
                success = False
                
                while attempts < max_retries and not success:
                    try:
                        for f in commit.files:
                            files_data.append({
                                "filename": f.filename,
                                "status": f.status,
                                "additions": f.additions,
                                "deletions": f.deletions,
                                "patch": f.patch if f.patch else "" # The actual code diff
                            })
                        success = True
                    except Exception as e:
                        attempts += 1
                        print(f"    [Warning] Timeout fetching commit {commit.sha[:7]}. Retrying ({attempts}/{max_retries})...")
                        time.sleep(2 ** attempts) # Exponential backoff
                
                if not success:
                    print(f"    [Error] Skipping commit {commit.sha[:7]} after {max_retries} failures.")
                    continue

                results.append({
                    "sha": commit.sha,
                    "date": commit.commit.author.date.isoformat(),
                    "message": commit.commit.message,
                    "files": files_data
                })
        except GithubException as e:
            print(f"Error fetching commits for {repo_obj.full_name}: {e}")
            
        return results

class HINBuilder:
    def __init__(self, username: str):
        self.username = username
        self.fetcher = GitHubFetcher()
        self.graph = nx.DiGraph()
        self.tfidf = TFIDFCalculator()
        
    def build_raw_topology(self):
        """
        Phase 1 of construction: Fetch data and build nodes/edges without advanced weights.
        """
        print(f"--- Starting HIN Construction for {self.username} ---")
        
        # 1. Developer Node
        user_data = self.fetcher.get_user_data(self.username)
        self.graph.add_node(
            f"dev:{self.username}", 
            type="developer", 
            **user_data
        )
        
        all_commits_data = [] # Store for TF-IDF training

        # 2. Repo Nodes
        repos = self.fetcher.get_top_repos(self.username)
        for repo in repos:
            repo_node_id = f"repo:{repo['name']}"
            self.graph.add_node(
                repo_node_id, 
                type="repository",
                language=repo['language'],
                languages=repo.get('languages', {}),
                topics=repo.get('topics', []),
                description=repo.get('description', ''),
                stars=repo['stars']
            )
            self.graph.add_edge(f"dev:{self.username}", repo_node_id, type="contributes", weight=1.0)
            
            # 3. Commit Nodes
            commits = self.fetcher.get_commits(repo['object'], self.username)
            all_commits_data.extend(commits) # Collect raw data
            
            for commit in commits:
                commit_node_id = f"commit:{commit['sha'][:7]}"
                self.graph.add_node(
                    commit_node_id,
                    type="commit",
                    message=commit['message'],
                    date=commit['date']
                )
                self.graph.add_edge(repo_node_id, commit_node_id, type="contains", weight=1.0)
                
                # 4. File Nodes
                for f in commit['files']:
                    file_node_id = f"file:{f['filename']}"
                    # Add file node if not exists (files are shared across commits)
                    if not self.graph.has_node(file_node_id):
                        self.graph.add_node(file_node_id, type="file")
                    
                    # Edge: Commit -> File (modifies)
                    # We store the patch size here for later TF-IDF/Weight calc
                    self.graph.add_edge(
                        commit_node_id, 
                        file_node_id, 
                        type="modifies",
                        additions=f['additions'],
                        patch_content=f['patch'] # Raw patch stored on edge
                    )
        
        print(f"--- Toplogy Built. Nodes: {self.graph.number_of_nodes()} ---")
        
        # Phase 2: Compute TF-IDF Weights
        print("--- Computing TF-IDF Semantic Weights ---")
        self.tfidf.fit_corpus(all_commits_data)
        
        for u, v, data in self.graph.edges(data=True):
            if data.get('type') == 'modifies':
                patch = data.get('patch_content', '')
                weight = self.tfidf.compute_weight(patch)
                self.graph[u][v]['weight'] = weight
                
        print("--- Graph Construction Complete ---")
        return self.graph
