import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { 
  FolderDown, 
  ArrowUpRight, 
  Search, 
  SlidersHorizontal,
  Loader,
  XCircle,
  CheckCircle,
  HelpCircle
} from "lucide-react";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("date"); // date, score
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const fetchHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_URL}/pipeline/history`);
      setHistory(res.data || []);
    } catch (err) {
      setError("Failed to load content history. Ensure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDownloadZip = (taskId) => {
    window.open(`${API_URL}/pipeline/export/${taskId}`, "_blank");
  };

  const handleOpenWorkspace = (taskId) => {
    navigate(`/dashboard?task_id=${taskId}`);
  };

  // Filter and Sort
  const filtered = history.filter((item) => 
    item.topic.toLowerCase().includes(search.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "score") {
      return b.virality_score - a.virality_score;
    }
    return new Date(b.created_at) - new Date(a.created_at);
  });

  return (
    <div className="flex-1 bg-[#09090b] text-white p-8 overflow-y-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Generation History</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Access and download your past AI content packs and predicted performance records.
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-6">
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 text-zinc-500" size={18} />
          <input
            type="text"
            placeholder="Search past topics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 bg-zinc-950 border border-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm rounded-xl text-zinc-200 outline-none transition-all duration-300"
          />
        </div>

        <div className="flex items-center gap-2">
          <SlidersHorizontal size={16} className="text-zinc-400" />
          <span className="text-xs text-zinc-400">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs px-3 py-2 rounded-xl outline-none focus:border-indigo-500 transition-all duration-300 cursor-pointer"
          >
            <option value="date">Latest Created</option>
            <option value="score">Virality Score</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader size={36} className="animate-spin text-indigo-500" />
        </div>
      ) : sorted.length === 0 ? (
        <div className="bg-zinc-950 border border-zinc-900 p-16 text-center rounded-2xl text-zinc-500">
          No generated items found. Go to Workspace to start your first run!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {sorted.map((item) => {
            
            // Status Icon styling
            let statusBadge = (
              <span className="flex items-center gap-1.5 text-xs text-amber-500 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full font-medium">
                <Loader size={12} className="animate-spin" /> {item.progress}%
              </span>
            );
            if (item.status === "completed") {
              statusBadge = (
                <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full font-medium">
                  <CheckCircle size={12} /> Complete
                </span>
              );
            } else if (item.status === "failed") {
              statusBadge = (
                <span className="flex items-center gap-1.5 text-xs text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1 rounded-full font-medium">
                  <XCircle size={12} /> Failed
                </span>
              );
            }

            const formattedDate = new Date(item.created_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit"
            });

            return (
              <div
                key={item.task_id}
                className="bg-zinc-950 border border-zinc-900 hover:border-zinc-800 p-6 rounded-2xl flex flex-col justify-between gap-6 transition-all duration-300 hover:-translate-y-0.5 shadow-xl group"
              >
                
                {/* Meta details */}
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">
                      {formattedDate}
                    </span>
                    {statusBadge}
                  </div>

                  <h3 className="font-bold text-zinc-100 text-base leading-snug group-hover:text-white transition-colors duration-300 line-clamp-2">
                    {item.topic}
                  </h3>

                  <div className="flex gap-4 mt-1">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">Virality</span>
                      <span className="text-sm font-extrabold text-indigo-400">
                        {item.virality_score > 0 ? `${item.virality_score}/100` : "--"}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">Duration</span>
                      <span className="text-sm font-semibold text-zinc-300">
                        {item.duration_sec > 0 ? `${item.duration_sec}s` : "--"}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">B-Roll</span>
                      <span className="text-sm font-semibold text-zinc-300">
                        {item.broll_scenes > 0 ? `${item.broll_scenes} scenes` : "--"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 border-t border-zinc-900 pt-4 mt-2">
                  <button
                    onClick={() => handleOpenWorkspace(item.task_id)}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 hover:border-zinc-700 font-semibold rounded-xl text-xs transition-all duration-300"
                  >
                    Open Workspace
                    <ArrowUpRight size={14} />
                  </button>

                  <button
                    onClick={() => handleDownloadZip(item.task_id)}
                    disabled={item.status !== "completed"}
                    className="flex items-center justify-center gap-1.5 px-4 py-2 bg-indigo-600/10 hover:bg-indigo-600/20 disabled:bg-zinc-900/20 text-indigo-400 disabled:text-zinc-600 border border-indigo-500/20 disabled:border-transparent font-semibold rounded-xl text-xs transition-all duration-300"
                  >
                    <FolderDown size={14} />
                    Download ZIP
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
