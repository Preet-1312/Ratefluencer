import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { 
  TrendingUp, 
  RotateCw, 
  ArrowUpRight, 
  Tv2, 
  Newspaper, 
  BarChart, 
  Flame 
} from "lucide-react";

export default function Trends() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const fetchTrends = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_URL}/trends/discover`);
      setTrends(res.data.trends || []);
    } catch (err) {
      setError("Failed to fetch trends. Ensure your backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  const handleCreateReel = (topic) => {
    navigate(`/dashboard?topic=${encodeURIComponent(topic)}`);
  };

  return (
    <div className="flex-1 bg-[#09090b] text-white p-8 overflow-y-auto">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Trends Explorer</h1>
          <p className="text-zinc-400 text-sm mt-1">
            Real-time popular topics across YouTube and News ranked by AI engagement scores.
          </p>
        </div>
        <button
          onClick={fetchTrends}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2.5 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 font-semibold rounded-xl text-sm transition-all duration-300 disabled:opacity-50"
        >
          <RotateCw size={16} className={loading ? "animate-spin" : ""} />
          Refresh Trends
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-zinc-950 border border-zinc-900 animate-pulse rounded-2xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Trends List (Col 2/3) */}
          <div className="lg:col-span-2 flex flex-col gap-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Flame className="text-orange-500" size={20} /> Ranked Live Trends
            </h2>

            {trends.length === 0 ? (
              <div className="bg-zinc-950 border border-zinc-900 p-12 text-center rounded-2xl text-zinc-500">
                No trends discovered. Try clicking Refresh.
              </div>
            ) : (
              trends.map((t, idx) => {
                const isYoutube = t.source === "youtube";
                const score = t.trend_score || 50;
                
                // Color mapping for scores
                let scoreColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
                if (score < 60) scoreColor = "text-amber-400 bg-amber-500/10 border-amber-500/20";
                if (score < 40) scoreColor = "text-zinc-400 bg-zinc-500/10 border-zinc-500/20";

                return (
                  <div
                    key={idx}
                    className="bg-zinc-950 border border-zinc-900 hover:border-zinc-800 p-5 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 transition-all duration-300 hover:translate-x-1"
                  >
                    <div className="flex gap-4 items-start flex-1">
                      <div className={`p-3 rounded-xl border bg-zinc-900 text-indigo-400`}>
                        {isYoutube ? <Tv2 size={18} /> : <Newspaper size={18} />}
                      </div>
                      <div className="flex flex-col gap-1">
                        <h3 className="font-semibold text-zinc-100 text-sm leading-snug max-w-md">
                          {t.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500 mt-1">
                          <span className="capitalize px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px]">
                            {t.source}
                          </span>
                          {t.score > 0 && (
                            <span>{(t.score / 1000).toFixed(0)}K views</span>
                          )}
                          <span>•</span>
                          <span className="text-zinc-400 italic">"{t.reason || 'Calculated trend analysis'}"</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 w-full sm:w-auto justify-between border-t border-zinc-900 pt-3 sm:pt-0 sm:border-0">
                      <div className={`px-3 py-1.5 rounded-lg border text-center font-bold text-xs ${scoreColor}`}>
                        Score: {score}
                      </div>

                      <button
                        onClick={() => handleCreateReel(t.title)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg text-xs transition-all duration-300"
                      >
                        Create
                        <ArrowUpRight size={14} />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Sidebar Analytics Visualizer (Col 1/3) */}
          <div className="flex flex-col gap-6">
            <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl">
              <h2 className="text-lg font-bold flex items-center gap-2 mb-6">
                <BarChart className="text-indigo-400" size={18} /> Score Distribution
              </h2>
              
              {/* Responsive SVG-based Bar Chart */}
              {trends.length === 0 ? (
                <div className="text-zinc-600 text-xs text-center py-8">No data to plot</div>
              ) : (
                <div className="space-y-4">
                  {trends.slice(0, 5).map((t, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-medium">
                        <span className="text-zinc-400 truncate max-w-[160px]">{t.title}</span>
                        <span className="text-indigo-400">{t.trend_score || 50}</span>
                      </div>
                      <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-1000"
                          style={{ width: `${t.trend_score || 50}%` }}
                        />
                      </div>
                    </div>
                  ))}
                  <p className="text-[10px] text-zinc-500 text-center mt-6">
                    Showing top 5 topics ranked by AI Growth Velocity.
                  </p>
                </div>
              )}
            </div>

            <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl flex flex-col gap-4">
              <h3 className="font-bold text-zinc-200">How Ranking Works</h3>
              <p className="text-zinc-400 text-xs leading-relaxed">
                The AI content engine pulls active topics across media channels. We calculate scores using:
              </p>
              <ul className="text-zinc-500 text-xs list-disc pl-4 space-y-2">
                <li><strong className="text-zinc-400">Growth Velocity</strong> - Rate of mentions in last 24 hours.</li>
                <li><strong className="text-zinc-400">Engagement Volume</strong> - Like & Comment ratios on YouTube.</li>
                <li><strong className="text-zinc-400">Groq Relevance Analysis</strong> - LLM scoring of tech virality vectors.</li>
              </ul>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
