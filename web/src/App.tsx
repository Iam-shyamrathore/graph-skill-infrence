import { useEffect, useState, useRef } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Search, ChevronRight, Activity, Cpu, Shield, ArrowUpRight } from 'lucide-react';
import { InteractiveRobotSpline } from '@/components/blocks/interactive-3d-robot';
import './index.css';

// Types
interface Skill {
  name: string;
  metrics: {
    belief: number;
    plausibility: number;
    uncertainty: number;
    path_count: number;
  };
}

interface Profile {
  developer: string;
  skills: Skill[];
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const GITHUB_SCENE_URL = "https://prod.spline.design/PyzDhpQ9E5f1E3MT/scene.splinecode";

function App() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('gh_token'));
  const [searchUser, setSearchUser] = useState('');
  const [currentView, setCurrentView] = useState<'landing' | 'dashboard' | 'docs'>(token ? 'dashboard' : 'landing');
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null);
  const fgRef = useRef<any>(null);

  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const urlUser = params.get('user');
    
    if (urlToken) {
        localStorage.setItem('gh_token', urlToken);
        setToken(urlToken);
        if (urlUser) localStorage.setItem('gh_user', urlUser);
        setCurrentView('dashboard');
        window.history.replaceState({}, document.title, "/");
    }
  }, []);

  const fetchData = async (user: string) => {
    setLoading(true);
    try {
      const profileRes = await axios.get(`${API_URL}/profile/${user}`);
      
      // Handle background processing
      if (profileRes.data.status === 'accepted' || profileRes.data.status === 'processing') {
          setStatusMessage(profileRes.data.message);
          // Retry after 5 seconds
          setTimeout(() => fetchData(user), 5000);
          return;
      }

      const graphRes = await axios.get(`${API_URL}/graph/${user}`);
      setProfile(profileRes.data);
      setGraphData(graphRes.data);
      setStatusMessage(null);
    } catch (e) {
      console.error("Failed to fetch data:", e);
      setStatusMessage("Error connecting to Inference Engine.");
    } finally {
      if (!statusMessage) setLoading(false);
    }
  };

  useEffect(() => {
    if (token && currentView === 'dashboard') {
        const savedUser = localStorage.getItem('gh_user') || 'Kaos599';
        fetchData(savedUser);
    }
  }, [token, currentView]);

  const handleLogin = () => {
      window.location.href = `${API_URL}/auth/github`;
  };

  const handleLogout = () => {
      localStorage.removeItem('gh_token');
      setToken(null);
      setCurrentView('landing');
      setProfile(null);
  };

  const onSearch = (e: React.FormEvent) => {
      e.preventDefault();
      if (searchUser) fetchData(searchUser);
  };

  return (
    <div className="relative w-screen h-screen bg-black text-white overflow-hidden font-sans selection:bg-primary/30 subtle-grid">
      <div className="hero-glow" />
      
      <AnimatePresence mode="wait">
        {/* LANDING VIEW */}
        {currentView === 'landing' && (
          <motion.div 
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative w-full h-full flex flex-col items-center justify-center p-8 px-12 sm:px-24"
          >
            <InteractiveRobotSpline 
                scene={GITHUB_SCENE_URL}
                className="absolute right-[-15%] top-1/2 -translate-y-1/2 w-[700px] h-[700px] z-0 opacity-40 mix-blend-screen pointer-events-none"
            />
            
            {/* Minimal Nav */}
            <nav className="fixed top-0 left-0 w-full p-8 px-12 sm:px-24 flex justify-between items-center z-50">
                <div className="flex items-center gap-2 group cursor-pointer transition-transform hover:scale-105" onClick={() => setCurrentView('landing')}>
                    <Brain className="w-5 h-5 text-primary" />
                    <span className="text-[11px] font-bold tracking-[0.2em] uppercase opacity-60">SIIN</span>
                </div>
                <div className="flex gap-12 items-center">
                    <button onClick={() => setCurrentView('docs')} className="text-[10px] font-bold tracking-[0.2em] text-white/30 hover:text-white transition-colors uppercase">Documentation</button>
                    <button 
                        onClick={handleLogin}
                        className="px-6 py-2 border border-white/10 rounded-full text-[10px] font-bold tracking-widest uppercase hover:bg-white hover:text-black transition-all duration-300 active:scale-95"
                    >
                        Connect
                    </button>
                </div>
            </nav>

            <div className="relative z-10 w-full flex flex-col items-start pt-20">
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                >
                    <div className="flex items-center gap-3 mb-12 opacity-30">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-subtle-pulse shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                        <span className="text-[9px] font-bold uppercase tracking-[0.5em]">Research Prototype v0.4.2</span>
                    </div>
                    
                    <h1 className="text-[80px] sm:text-[120px] font-bold leading-[0.85] tracking-tight mb-8 text-gradient">
                       Latent<br/>Skill <span className="opacity-20 translate-x-2 inline-block">Inference</span>
                    </h1>
                    
                    <p className="text-base sm:text-lg text-white/30 max-w-lg mb-12 font-medium leading-relaxed">
                       Mapping technical expertise through meta-path exploration on heterogeneous knowledge manifolds.
                    </p>
                    
                    <div className="flex gap-8 items-center">
                        <button 
                            onClick={handleLogin}
                            className="group flex items-center gap-4 px-10 py-5 bg-white text-black rounded-full font-bold text-[11px] tracking-widest uppercase hover:scale-105 active:scale-95 transition-all duration-500 shadow-[0_0_50px_rgba(255,255,255,0.1)]"
                        >
                            Execute Inference <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button 
                            onClick={() => setCurrentView('docs')}
                            className="group flex items-center gap-3 text-[10px] font-bold tracking-widest uppercase text-white/20 hover:text-white transition-colors"
                        >
                            Read Paper <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                        </button>
                    </div>
                </motion.div>
            </div>
            
            {/* Minimal Footer */}
            <div className="fixed bottom-12 left-12 sm:left-24 flex gap-12 opacity-20 hover:opacity-100 transition-opacity">
                <div className="flex flex-col gap-1">
                    <span className="text-[8px] font-bold uppercase tracking-widest">Latency</span>
                    <span className="text-[10px] font-mono tracking-tighter italic">24ms peak</span>
                </div>
                <div className="w-px h-6 bg-white/10 self-center" />
                <div className="flex flex-col gap-1">
                    <span className="text-[8px] font-bold uppercase tracking-widest">Precision</span>
                    <span className="text-[10px] font-mono tracking-tighter italic">δ=0.0042</span>
                </div>
            </div>
          </motion.div>
        )}

        {/* DOCS VIEW */}
        {currentView === 'docs' && (
          <motion.div 
            key="docs"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full bg-black flex flex-col overflow-y-auto subtle-grid"
          >
             <nav className="fixed top-0 left-0 w-full p-8 px-12 sm:px-24 flex justify-between items-center z-50 bg-black/50 backdrop-blur-xl border-b border-white/5">
                 <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setCurrentView('landing')}>
                    <Shield className="w-5 h-5 text-primary transition-transform group-hover:scale-110" />
                    <span className="text-[11px] font-bold tracking-widest uppercase opacity-60">System Protocols</span>
                </div>
                <button onClick={() => setCurrentView('landing')} className="text-[9px] font-bold uppercase tracking-[0.3em] opacity-30 hover:opacity-100 transition-opacity">Back</button>
            </nav>
            
            <div className="max-w-4xl mx-auto pt-48 pb-32 px-8">
                <AnimatePresence mode="wait">
                    {selectedDoc === null ? (
                        <motion.div 
                            key="docs-list"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                        >
                            <div className="mb-24">
                                <div className="flex items-center gap-3 mb-6 opacity-30">
                                    <span className="w-8 h-px bg-white" />
                                    <span className="text-[9px] font-bold uppercase tracking-[0.3em]">Theoretical Basis</span>
                                </div>
                                <h2 className="text-6xl sm:text-8xl font-bold tracking-tight mb-8 text-gradient">Mission <br/> Critical <br/> Logic</h2>
                            </div>
                            
                            <div className="grid grid-cols-1 gap-2">
                                {[
                                    { icon: Activity, title: "HIN Ingestion", desc: "Multi-hop mapping of GitHub event telemetry into high-fidelity knowledge manifolds." },
                                    { icon: Cpu, title: "DeepPath MCTS", desc: "Agentic exploration of graph topology to verify latent expertise clusters." },
                                    { icon: Shield, title: "Trust Fusion", desc: "Synthesizing evidentiary conflict via Subjective Logic for robust inference." }
                                ].map((step, i) => (
                                    <motion.div 
                                        key={i} 
                                        initial={{ x: -20, opacity: 0 }}
                                        animate={{ x: 0, opacity: 1 }}
                                        transition={{ delay: 0.2 + i * 0.1 }}
                                        onClick={() => setSelectedDoc(i)}
                                        className="group p-10 rounded-3xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.05] hover:border-primary/30 hover:shadow-[0_0_30px_rgba(59,130,246,0.1)] transition-all duration-500 flex items-center justify-between cursor-pointer active:scale-[0.99]"
                                    >
                                        <div className="flex items-center gap-8">
                                            <div className="w-14 h-14 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center transition-transform group-hover:scale-110 group-hover:bg-primary/20">
                                                <step.icon className="w-6 h-6 text-primary shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
                                            </div>
                                            <div className="max-w-md">
                                                <h3 className="text-xl font-bold mb-2 opacity-90 group-hover:text-white transition-colors">{step.title}</h3>
                                                <p className="text-sm text-white/30 font-medium leading-relaxed group-hover:text-white/50 transition-colors">{step.desc}</p>
                                            </div>
                                        </div>
                                        <ArrowUpRight className="w-5 h-5 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div 
                            key="doc-detail"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="bg-white/[0.02] border border-white/5 rounded-[40px] p-12 sm:p-20"
                        >
                            <button 
                                onClick={() => setSelectedDoc(null)}
                                className="mb-12 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-primary hover:text-white transition-colors"
                            >
                                <ChevronRight className="w-4 h-4 rotate-180" /> Back to Protocols
                            </button>
                            
                            {selectedDoc === 0 && (
                                <div className="space-y-12">
                                    <h3 className="text-5xl font-bold tracking-tight">HIN Ingestion</h3>
                                    <div className="prose prose-invert max-w-none text-white/40 leading-relaxed space-y-8 text-sm">
                                        <p>The core of the system is a **Heterogeneous Information Network (HIN)**. Unlike a simple social graph, a HIN preserves the multi-typed semantics of software development.</p>
                                        
                                        <div className="grid grid-cols-2 gap-8 py-8 border-y border-white/5">
                                            <div>
                                                <h4 className="text-white text-[10px] font-bold uppercase tracking-widest mb-4">Node Dictionary</h4>
                                                <ul className="space-y-2 font-mono text-[10px]">
                                                    <li>Developer: dev:{"{user}"}</li>
                                                    <li>Repo: repo:{"{org/name}"}</li>
                                                    <li>Commit: commit:{"{hash}"}</li>
                                                    <li>Skill: skill:{"{name}"}</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <h4 className="text-white text-[10px] font-bold uppercase tracking-widest mb-4">Edge Weighting</h4>
                                                <p className="text-[10px]">Repositories: {"1 + ln(commits)"}. <br/> Commits: TF-IDF Semantics.</p>
                                            </div>
                                        </div>

                                        <h4 className="text-white font-bold opacity-80 pt-4">Semantic Filtering (TF-IDF)</h4>
                                        <p>We treat code patches as technical documents. Term Frequency (TF) measures keyword density, while Inverse Document Frequency (IDF) penalizes boilerplate. This isolates "signal" like <code className="text-primary">transformers</code> or <code className="text-primary">fastapi</code> from "noise" like <code className="text-white/20">if</code> or <code className="text-white/20">import</code>.</p>
                                    </div>
                                </div>
                            )}

                            {selectedDoc === 1 && (
                                <div className="space-y-12">
                                    <h3 className="text-5xl font-bold tracking-tight">DeepPath MCTS</h3>
                                    <div className="prose prose-invert max-w-none text-white/40 leading-relaxed space-y-8 text-sm">
                                        <p>Our Neural-guided Monte Carlo Tree Search (MCTS) performs guided exploration over the sparse HIN topology to find latent "expertise paths".</p>
                                        
                                        <div className="bg-black/80 p-10 rounded-3xl border border-white/10 font-mono text-[11px] leading-relaxed text-blue-300 shadow-2xl">
                                            v(s, a) = Q(s, a) + C_puct * P(s, a) * (sqrt(sum N) / (1 + n))
                                        </div>

                                        <div className="space-y-4">
                                            <h4 className="text-white font-bold opacity-80">Search Components:</h4>
                                            <ul className="list-disc pl-5 space-y-2">
                                                <li><strong>Prior P(s, a):</strong> Heuristic bias towards high-star repos and matching language tags.</li>
                                                <li><strong>PUCT Selection:</strong> Dynamic balance between exploring new repos and exploiting known expertise.</li>
                                                <li><strong>Multi-Faceted Reward:</strong> Combines Accuracy (LLM confidence), Efficiency (path length), and Diversity (new skill discovery).</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {selectedDoc === 2 && (
                                <div className="space-y-12">
                                    <h3 className="text-5xl font-bold tracking-tight">Trust Fusion</h3>
                                    <div className="prose prose-invert max-w-none text-white/40 leading-relaxed space-y-8 text-sm">
                                        <p>Evidence chains are mapped to **Subjective Logic Opinions** {"\u03c9 = (b, d, u, a)"}. We use Yager's Rule of Combination to synthesize conflicting technical signals.</p>
                                        
                                        <div className="p-10 border-l-4 border-primary bg-white/[0.01] rounded-r-3xl">
                                            <h4 className="text-white font-bold mb-4">Conflict Resolution (Yager)</h4>
                                            <p className="italic">"Conflict is explicitly reallocated to Ignorance. If two repositories provide contradictory evidence about a skill, the system's overall confidence decreases proportionally to the degree of conflict (K)."</p>
                                        </div>

                                        <p>This approach ensures that high-confidence inferences require consistent evidence across multiple repositories, preventing "one-hit wonder" expertise inflation.</p>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* DASHBOARD VIEW */}
        {currentView === 'dashboard' && (
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full bg-black flex overflow-hidden"
          >
            {/* Left Control Panel */}
            <div className="w-[360px] min-w-[320px] h-full flex flex-col bg-black/40 backdrop-blur-3xl border-r border-white/5 z-50">
                <header className="px-6 py-5 border-b border-white/5 flex justify-between items-center bg-black/20">
                    <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                            <Brain className="w-4 h-4 text-primary" />
                        </div>
                        <span className="text-[10px] font-bold tracking-[0.3em] uppercase opacity-40">Command Unit</span>
                    </div>
                    <button onClick={handleLogout} className="text-[9px] font-black uppercase tracking-[0.3em] text-white/20 hover:text-red-500 transition-colors">Logout</button>
                </header>

                <div className="p-6 pb-0 flex-none">
                    <div className="mb-10">
                        <div className="flex items-center gap-6 mb-4">
                             <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary to-blue-400 p-0.5 shadow-[0_0_40px_rgba(59,130,246,0.2)]">
                                <div className="w-full h-full rounded-[22px] bg-black flex items-center justify-center font-bold text-lg text-primary">
                                    {profile?.developer?.charAt(0) || 'Ø'}
                                </div>
                             </div>
                             <div>
                                <h2 className="text-2xl font-bold tracking-tight mb-1">{profile?.developer || 'Initializing...'}</h2>
                                <div className="flex items-center gap-2 px-0.5">
                                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                                    <span className="text-[8px] font-bold uppercase tracking-[0.2em] text-white/30">Inference Engine Live</span>
                                </div>
                             </div>
                        </div>
                    </div>

                    <form onSubmit={onSearch} className="mb-8 relative group">
                        <input 
                            type="text" 
                            placeholder="Search GitHub Identifier" 
                            value={searchUser}
                            onChange={(e) => setSearchUser(e.target.value)}
                            className="w-full bg-white/[0.06] border border-white/20 rounded-2xl px-12 py-4 text-sm font-semibold focus:border-primary/60 focus:bg-white/[0.1] outline-none transition-all placeholder:text-white/40 text-white shadow-inner"
                        />
                        <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60 group-focus-within:text-primary transition-colors" />
                    </form>

                    <div className="mb-8 px-4 py-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-[8px] font-bold uppercase tracking-[0.3em] opacity-40">Logic Reference</span>
                            <Activity className="w-3 h-3 text-primary opacity-40" />
                        </div>
                        <div className="space-y-3">
                            <div>
                                <span className="text-[10px] font-bold text-white/80 block mb-1">Facticity (%)</span>
                                <p className="text-[9px] text-white/30 leading-relaxed font-medium">Confidence score based on cross-repository evidence paths.</p>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <span className="text-[10px] font-bold text-white/80 block mb-1 underline decoration-primary/30">Belief</span>
                                    <p className="text-[8px] text-white/20 leading-tight">Direct proof from code.</p>
                                </div>
                                <div>
                                    <span className="text-[10px] font-bold text-white/80 block mb-1 underline decoration-primary/30">Uncert</span>
                                    <p className="text-[8px] text-white/20 leading-tight">Gap in data frequency.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto px-6 pb-8 custom-scrollbar">
                    {loading ? (
                        <div className="h-full flex flex-col items-center justify-center py-20 opacity-30 border border-dashed border-white/10 rounded-3xl bg-white/[0.01]">
                            <Cpu className="w-10 h-10 animate-spin mb-6 text-primary" />
                            <span className="text-[9px] font-bold uppercase tracking-[0.4em] text-center px-8 leading-loose italic">
                                {statusMessage || "Decoding Manifold..."}
                            </span>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {profile?.skills.map((skill, i) => (
                                <motion.div 
                                    key={skill.name}
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.04 }}
                                    className="p-6 rounded-[32px] border border-white/[0.03] bg-white/[0.01] hover:bg-white/[0.02] hover:border-white/[0.08] transition-all group"
                                >
                                    <div className="flex justify-between items-end mb-4">
                                        <div>
                                            <span className="text-[8px] font-bold uppercase tracking-widest text-white/20 mb-1 block">Inference Target</span>
                                            <h4 className="text-sm font-bold tracking-wide group-hover:text-primary transition-colors">{skill.name}</h4>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-2xl font-bold tracking-tighter italic text-gradient">{(skill.metrics.belief * 100).toFixed(1)}%</span>
                                            <span className="block text-[8px] font-bold uppercase tracking-widest opacity-20">Facticity</span>
                                        </div>
                                    </div>
                                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mb-4">
                                        <motion.div 
                                            initial={{ width: 0 }}
                                            animate={{ width: `${Math.min(100, skill.metrics.belief * 100)}%` }}
                                            className="h-full bg-primary shadow-[0_0_10px_rgba(59,130,246,0.6)]"
                                        />
                                    </div>
                                    <div className="grid grid-cols-3 gap-6 opacity-20 group-hover:opacity-60 transition-all duration-500">
                                        <div><span className="text-[7px] font-bold uppercase block mb-0.5 opacity-50">Belief</span><span className="text-[10px] font-mono leading-none">{skill.metrics.belief.toFixed(3)}</span></div>
                                        <div><span className="text-[7px] font-bold uppercase block mb-0.5 opacity-50">Plaus</span><span className="text-[10px] font-mono leading-none">{skill.metrics.plausibility.toFixed(3)}</span></div>
                                        <div><span className="text-[7px] font-bold uppercase block mb-0.5 opacity-50">Uncert</span><span className="text-[10px] font-mono leading-none">{skill.metrics.uncertainty.toFixed(3)}</span></div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Right Visualization Area */}
            <div className="flex-1 relative bg-black">
                <ForceGraph3D
                    ref={fgRef}
                    graphData={graphData}
                    nodeLabel="label"
                    nodeColor={(node: any) => {
                        switch(node.group) {
                            case 'dev': return '#ffffff';    // White
                            case 'repo': return '#777777';   // Silver/Bright Gray
                            case 'skill': return '#3b82f6';  // Electric Blue
                            case 'commit': return '#10b981'; // Emerald Green (Evidence)
                            default: return '#666666';
                        }
                    }}
                    nodeVal={(node: any) => {
                        if (node.group === 'dev') return 45;
                        if (node.group === 'repo') return 18;
                        if (node.group === 'skill') return 25;
                        return 8;
                    }}
                    d3AlphaDecay={0.02}
                    d3VelocityDecay={0.3}
                    cooldownTicks={100}
                    onEngineStop={() => fgRef.current.zoomToFit(400, 150)}
                    linkOpacity={0.3}
                    linkWidth={2}
                    linkColor={() => '#ffffff'}
                    backgroundColor="rgba(0,0,0,0)"
                    showNavInfo={false}
                />
                
                {/* Minimal Overlay Grid */}
                <div className="absolute top-12 left-12 opacity-20 pointer-events-none">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                        <span className="text-[9px] font-bold tracking-widest uppercase italic">Inference Plane Alpha</span>
                    </div>
                </div>

                {/* Legend Overlay */}
                <div className="absolute bottom-10 right-10 flex gap-6 items-center bg-white/[0.04] border border-white/10 rounded-full px-6 py-3 backdrop-blur-3xl shadow-2xl">
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.4)]" />
                        <span className="text-[10px] font-bold tracking-widest uppercase text-white/50">Dev</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full bg-[#777777] border border-white/10" />
                        <span className="text-[10px] font-bold tracking-widest uppercase text-white/50">Repo</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full bg-[#3b82f6] shadow-[0_0_12px_rgba(59,130,246,0.6)]" />
                        <span className="text-[10px] font-bold tracking-widest uppercase text-white/50">Skill</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-2.5 h-2.5 rounded-full bg-[#10b981] shadow-[0_0_12px_rgba(16,185,129,0.4)]" />
                        <span className="text-[10px] font-bold tracking-widest uppercase text-white/50">Evidence</span>
                    </div>
                </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
