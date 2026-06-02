import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import { 
  Sparkles, 
  Send, 
  Loader, 
  Copy, 
  Check, 
  Download, 
  Tv2, 
  Volume2, 
  Image as ImageIcon, 
  Calendar, 
  ChevronRight, 
  Eye, 
  TrendingUp, 
  Share2, 
  Plus, 
  FileAudio,
  PenTool,
  Clock,
  Sparkle
} from "lucide-react";

// Custom SVG Brand Icons since Lucide v1.x removed brand icons
function Instagram({ size = 24, className = "" }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
      <line x1="17.5" x2="17.51" y1="6.5" y2="6.5" />
    </svg>
  );
}

function Linkedin({ size = 24, className = "" }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
      <rect width="4" height="12" x="2" y="9" />
      <circle cx="4" cy="4" r="2" />
    </svg>
  );
}

function YouTubeClipsCard({ clips }) {
  const [activeVideoId, setActiveVideoId] = useState(null);
  const [activeStart, setActiveStart] = useState(0);
  const [activeEnd, setActiveEnd] = useState(10);

  if (!clips || clips.length === 0) return null;

  return (
    <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
      <h2 className="text-lg font-bold flex items-center gap-2 text-zinc-100">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-red-500 animate-pulse"
        >
          <path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17z" />
          <polygon points="10 15 15 12 10 9" />
        </svg>
        YouTube Reference Clips
      </h2>
      <p className="text-[11px] text-zinc-400 -mt-2 leading-relaxed">
        Real video clips fetched based on your topic. Use for visual reference or B-roll ideas.
      </p>

      <div className="space-y-6">
        {clips.map((clip) => {
          const isSelected = activeVideoId === clip.video_id;
          const bestTimestamp = clip.timestamps && clip.timestamps.length > 0 ? clip.timestamps[0] : { start: 0, end: 10 };
          const embedUrl = isSelected
            ? `https://www.youtube.com/embed/${clip.video_id}?start=${activeStart}&end=${activeEnd}&autoplay=1`
            : null;

          return (
            <div key={clip.video_id} className="border border-zinc-900 bg-zinc-900/30 rounded-xl overflow-hidden flex flex-col">
              {/* Video Player or Thumbnail */}
              <div className="relative aspect-video bg-zinc-950 flex items-center justify-center">
                {isSelected ? (
                  <iframe
                    src={embedUrl}
                    title={clip.title}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                    className="w-full h-full"
                  />
                ) : (
                  <div className="relative w-full h-full group cursor-pointer" onClick={() => {
                    setActiveVideoId(clip.video_id);
                    setActiveStart(bestTimestamp.start);
                    setActiveEnd(bestTimestamp.end);
                  }}>
                    <img
                      src={clip.thumbnail_url}
                      alt={clip.title}
                      className="w-full h-full object-cover opacity-75 group-hover:opacity-85 transition-opacity"
                    />
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center group-hover:bg-black/45 transition-colors">
                      <div className="w-12 h-12 rounded-full bg-red-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polygon points="6 3 20 12 6 21 6 3" />
                        </svg>
                      </div>
                    </div>
                    {/* Duration badge */}
                    <span className="absolute bottom-2 right-2 px-1.5 py-0.5 bg-black/85 text-[10px] font-bold rounded text-zinc-300">
                      {clip.duration}
                    </span>
                  </div>
                )}
              </div>

              {/* Clip Metadata */}
              <div className="p-4 flex flex-col gap-2.5">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] text-zinc-500 font-bold uppercase truncate max-w-[140px]">
                      {clip.channel_name}
                    </span>
                    {clip.is_creative_commons ? (
                      <span className="px-2 py-0.5 bg-emerald-950/80 border border-emerald-900/60 text-emerald-400 text-[9px] font-bold uppercase rounded">
                        Free to use (CC)
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-zinc-900 border border-zinc-800 text-zinc-400 text-[9px] font-bold uppercase rounded">
                        Reference only
                      </span>
                    )}
                  </div>
                  <h4 className="font-semibold text-zinc-200 text-xs mt-1 leading-normal line-clamp-2">
                    {clip.title}
                  </h4>
                </div>

                <div className="flex justify-between items-center text-[10px] text-zinc-500">
                  <span>{clip.view_count_formatted}</span>
                  <span className="flex items-center gap-1">
                    Score: <strong className="text-zinc-300">{clip.relevance_score}/100</strong>
                  </span>
                </div>

                {/* Suggested Timestamps */}
                {clip.timestamps && clip.timestamps.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-zinc-900">
                    <span className="text-[9px] font-bold uppercase tracking-wider text-zinc-500 block">
                      Suggested Clips
                    </span>
                    <div className="flex flex-col gap-1">
                      {clip.timestamps.map((t, idx) => {
                        const isCurrentActive = isSelected && activeStart === t.start && activeEnd === t.end;
                        return (
                          <button
                            key={idx}
                            onClick={() => {
                              setActiveVideoId(clip.video_id);
                              setActiveStart(t.start);
                              setActiveEnd(t.end);
                            }}
                            className={`w-full py-1.5 px-2.5 rounded-lg border text-left flex items-center justify-between text-[10px] transition-all duration-300 ${
                              isCurrentActive
                                ? "bg-red-950/20 border-red-900/60 text-red-400 font-medium"
                                : "bg-zinc-950 border-zinc-900 text-zinc-400 hover:border-zinc-800 hover:text-zinc-300"
                            }`}
                          >
                            <span className="font-semibold truncate max-w-[170px]">{t.reason}</span>
                            <span className="font-mono text-[9px]">
                              {t.start}s - {t.end}s
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* External link */}
                <a
                  href={clip.youtube_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-1.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-850 font-bold rounded-xl text-[10px] transition-all duration-300 mt-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  Open on YouTube
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState(60);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState("");
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  
  // Brand voice states
  const [voices, setVoices] = useState([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState("");
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [newVoice, setNewVoice] = useState({ name: "", tone: "professional", style_guide: "", hashtags: "" });

  // Tab views for secondary features
  const [activeFeatureTab, setActiveFeatureTab] = useState("preview"); // preview, repurpose, calendar, series, ab-hooks
  const [activeMediaTab, setActiveMediaTab] = useState("video"); // video, thumbnail
  
  // Subtitle timed overlay states
  const [videoPlayTime, setVideoPlayTime] = useState(0);
  const [activeSubtitle, setActiveSubtitle] = useState("");
  
  // Waveform state
  const [audioPlaying, setAudioPlaying] = useState(false);
  
  // Dynamic features results
  const [calendar, setCalendar] = useState(null);
  const [repurposed, setRepurposed] = useState(null);
  const [series, setSeries] = useState(null);
  const [abHooks, setAbHooks] = useState(null);
  const [loadingFeature, setLoadingFeature] = useState(false);

  // Copy status indicators
  const [copiedStates, setCopiedStates] = useState({});

  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const wsRef = useRef(null);

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  // Check for query parameters on load
  useEffect(() => {
    fetchBrandVoices();
    const queryTopic = searchParams.get("topic");
    const queryTaskId = searchParams.get("task_id");
    if (queryTopic) {
      setTopic(decodeURIComponent(queryTopic));
    }
    if (queryTaskId) {
      loadPastTask(queryTaskId);
    }
  }, [searchParams]);

  // Load active subtitle block based on video timestamp
  useEffect(() => {
    if (results && results.subtitles) {
      const active = results.subtitles.find(
        (sub) => videoPlayTime >= sub.start && videoPlayTime <= sub.end
      );
      setActiveSubtitle(active ? active.text : "");
    }
  }, [videoPlayTime, results]);

  const fetchBrandVoices = async () => {
    try {
      const res = await axios.get(`${API_URL}/pipeline/brand-voice`);
      setVoices(res.data || []);
      const active = res.data.find(v => v.is_active);
      if (active) setSelectedVoiceId(active.id);
    } catch (err) {
      console.error("Error loading brand voices", err);
    }
  };

  const loadPastTask = async (taskId) => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_URL}/pipeline/status/${taskId}`);
      if (res.data && res.data.status === "completed") {
        setResults(res.data.results);
        setTopic(res.data.topic);
        // Clear secondary features
        setCalendar(null);
        setRepurposed(null);
        setSeries(null);
        setAbHooks(null);
      } else {
        setError(`Requested task is currently ${res.data.status || 'not ready'}`);
      }
    } catch (err) {
      setError("Failed to load task. Verify the ID exists.");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVoice = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/pipeline/brand-voice`, newVoice);
      setVoices([...voices, res.data]);
      setSelectedVoiceId(res.data.id);
      setShowVoiceModal(false);
      setNewVoice({ name: "", tone: "professional", style_guide: "", hashtags: "" });
    } catch (err) {
      console.error("Error creating brand voice", err);
    }
  };

  const handleSelectVoice = async (id) => {
    setSelectedVoiceId(id);
    try {
      await axios.post(`${API_URL}/pipeline/brand-voice/${id}/activate`);
    } catch (err) {
      console.error("Error activating brand voice", err);
    }
  };

  // Start Content Generation Pipeline
  const runPipeline = async (auto = false) => {
    setLoading(true);
    setError("");
    setResults(null);
    setLogs([]);
    setProgress(0);
    
    // Clear secondary features
    setCalendar(null);
    setRepurposed(null);
    setSeries(null);
    setAbHooks(null);

    try {
      const payload = {
        topic: auto ? "" : topic,
        auto_trend: auto,
        duration: parseInt(duration),
        brand_voice_id: selectedVoiceId ? parseInt(selectedVoiceId) : null
      };

      const res = await axios.post(`${API_URL}/pipeline/run`, payload);
      const taskId = res.data.task_id;
      
      // Connect WebSocket
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = API_URL.replace(/^https?:\/\//, "");
      const wsUrl = `${wsProtocol}//${wsHost}/ws/progress/${taskId}`;
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProgress(data.progress);
        setCurrentStep(data.step);
        
        if (data.message) {
          setLogs((prev) => [...prev, `${new Date().toLocaleTimeString()} - ${data.message}`]);
        }

        if (data.status === "completed") {
          ws.close();
          loadPastTask(taskId);
        } else if (data.status === "failed") {
          ws.close();
          setError("Task failed. Check logs.");
          setLoading(false);
        }
      };

      ws.onerror = (err) => {
        console.error("WS error:", err);
        setError("WebSocket disconnect. Falling back to status checking...");
      };

    } catch (err) {
      setError("Failed to run pipeline. Verify connection.");
      setLoading(false);
    }
  };

  // Secondary Tab feature fetchers
  const loadContentCalendar = async () => {
    if (!results) return;
    setLoadingFeature(true);
    try {
      const res = await axios.post(`${API_URL}/pipeline/calendar`, {
        topic: results.topic,
        brand_voice: voices.find(v => v.id === selectedVoiceId)?.name || "Standard"
      });
      setCalendar(res.data.calendar);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFeature(false);
    }
  };

  const loadRepurposing = async () => {
    if (!results) return;
    setLoadingFeature(true);
    try {
      const res = await axios.post(`${API_URL}/pipeline/repurpose`, {
        topic: results.topic,
        script: results.script
      });
      setRepurposed(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFeature(false);
    }
  };

  const loadSeries = async () => {
    if (!results) return;
    setLoadingFeature(true);
    try {
      const res = await axios.get(`${API_URL}/pipeline/series?topic=${encodeURIComponent(results.topic)}`);
      setSeries(res.data.series);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFeature(false);
    }
  };

  const loadAbHooks = async () => {
    if (!results) return;
    setLoadingFeature(true);
    try {
      const res = await axios.post(`${API_URL}/pipeline/ab-hooks`, {
        topic: results.topic,
        brand_voice: voices.find(v => v.id === selectedVoiceId)?.name || "Standard"
      });
      setAbHooks(res.data.hooks);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFeature(false);
    }
  };

  useEffect(() => {
    if (results) {
      if (activeFeatureTab === "calendar" && !calendar) loadContentCalendar();
      if (activeFeatureTab === "repurpose" && !repurposed) loadRepurposing();
      if (activeFeatureTab === "series" && !series) loadSeries();
      if (activeFeatureTab === "ab-hooks" && !abHooks) loadAbHooks();
    }
  }, [activeFeatureTab, results]);

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedStates((prev) => ({ ...prev, [key]: true }));
    setTimeout(() => {
      setCopiedStates((prev) => ({ ...prev, [key]: false }));
    }, 2000);
  };

  const handleVideoTimeUpdate = () => {
    if (videoRef.current) {
      setVideoPlayTime(videoRef.current.currentTime);
    }
  };

  const toggleAudio = () => {
    if (audioRef.current) {
      if (audioPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setAudioPlaying(!audioPlaying);
    }
  };

  return (
    <div className="flex-1 bg-[#09090b] text-white p-8 overflow-y-auto">
      
      {/* Upper config row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        
        {/* Topic Input card */}
        <div className="md:col-span-2 bg-zinc-950 border border-zinc-900 p-6 rounded-2xl flex flex-col gap-4 shadow-xl">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Sparkles size={18} className="text-indigo-400" /> Start Content Run
          </h2>
          
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter keywords or topic (e.g. Artificial Intelligence productivity hacks)..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="flex-1 px-4 py-3 bg-zinc-900 border border-zinc-800 focus:border-indigo-500 text-zinc-100 rounded-xl outline-none transition-all duration-300"
            />
            <select
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 text-zinc-300 px-3 py-3 rounded-xl focus:border-indigo-500 outline-none cursor-pointer"
            >
              <option value={30}>30s</option>
              <option value={60}>60s</option>
              <option value={90}>90s</option>
            </select>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => runPipeline(false)}
              disabled={loading || !topic}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition-all duration-300 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {loading ? <Loader className="animate-spin" size={16} /> : <Send size={16} />}
              Generate Pack
            </button>
            <button
              onClick={() => runPipeline(true)}
              disabled={loading}
              className="px-6 py-3 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-bold rounded-xl transition-all duration-300"
            >
              ⚡ Auto Trend
            </button>
          </div>
        </div>

        {/* Brand Voice card */}
        <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold">Brand Voice</h2>
              <button
                onClick={() => setShowVoiceModal(true)}
                className="p-1.5 bg-zinc-900 hover:bg-zinc-850 rounded-lg text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition-all duration-300"
              >
                <Plus size={16} />
              </button>
            </div>
            
            <div className="flex flex-col gap-2">
              {voices.map((v) => (
                <div
                  key={v.id}
                  onClick={() => handleSelectVoice(v.id)}
                  className={`px-4 py-3 rounded-xl border text-sm font-semibold flex items-center justify-between cursor-pointer transition-all duration-300 ${
                    selectedVoiceId === v.id
                      ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                      : "bg-zinc-900 border-zinc-800/80 text-zinc-400 hover:bg-zinc-850"
                  }`}
                >
                  <span>{v.name}</span>
                  <span className="text-[10px] uppercase font-bold text-zinc-500">{v.tone}</span>
                </div>
              ))}
            </div>
          </div>
          <p className="text-[10px] text-zinc-500 mt-4 leading-normal">
            Your style guide automatically optimizes script tone constraints.
          </p>
        </div>

      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-6">
          {error}
        </div>
      )}

      {/* Real-time Loading websocket overlay */}
      {loading && !results && (
        <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl shadow-xl mb-8 flex flex-col gap-6 animate-fade-in">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <Loader size={20} className="animate-spin text-indigo-500" />
              <span className="font-bold text-zinc-200">Executing Content Pipeline...</span>
            </div>
            <span className="text-lg font-extrabold text-indigo-400">{progress}%</span>
          </div>

          {/* Progress Bar */}
          <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500 rounded-full transition-all duration-500 shadow-md shadow-indigo-500/20"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* WS Logs terminal */}
          <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl h-36 overflow-y-auto font-mono text-[11px] text-zinc-500 space-y-1">
            {logs.map((log, idx) => (
              <div key={idx} className="hover:text-zinc-300 transition-colors">
                &gt; {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated output section */}
      {results && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
          
          {/* Main Content Pane (Col 2/3) */}
          <div className="xl:col-span-2 space-y-8">
            
            {/* Summary Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              <div className="bg-zinc-950 border border-zinc-900 p-4 rounded-xl">
                <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Virality Score</span>
                <p className="text-lg font-extrabold text-indigo-400 mt-0.5">{results.summary.virality_score}/100</p>
              </div>
              <div className="bg-zinc-950 border border-zinc-900 p-4 rounded-xl">
                <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Trend Velocity</span>
                <p className="text-lg font-extrabold text-emerald-400 mt-0.5 capitalize">{results.virality.velocity_class}</p>
              </div>
              <div className="bg-zinc-950 border border-zinc-900 p-4 rounded-xl">
                <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Duration</span>
                <p className="text-lg font-extrabold text-zinc-300 mt-0.5">{results.summary.duration_sec}s</p>
              </div>
              <div className="bg-zinc-950 border border-zinc-900 p-4 rounded-xl">
                <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Category</span>
                <p className="text-lg font-extrabold text-zinc-300 mt-0.5 capitalize">{results.virality.category}</p>
              </div>
            </div>

            {/* Navigation Tabs for secondary features */}
            <div className="border-b border-zinc-900 flex gap-6 text-sm">
              {[
                { id: "preview", name: "Mockup Preview" },
                { id: "ab-hooks", name: "A/B Hook Test" },
                { id: "repurpose", name: "Repurpose" },
                { id: "calendar", name: "Content Calendar" },
                { id: "series", name: "5-Part Series" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveFeatureTab(tab.id)}
                  className={`pb-3 font-semibold transition-all duration-300 border-b-2 ${
                    activeFeatureTab === tab.id
                      ? "border-indigo-500 text-indigo-400"
                      : "border-transparent text-zinc-500 hover:text-zinc-300"
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </div>

            {/* Secondary features views */}
            <div className="min-h-[250px]">
              {loadingFeature ? (
                <div className="flex justify-center items-center py-16">
                  <Loader size={24} className="animate-spin text-indigo-500" />
                </div>
              ) : (
                <>
                  {/* Platform Mockup Previews */}
                  {activeFeatureTab === "preview" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      {/* Instagram Reels mock */}
                      <div className="bg-zinc-950 border border-zinc-900 rounded-3xl overflow-hidden shadow-2xl flex flex-col justify-between max-w-[340px] mx-auto w-full">
                        <div className="p-4 border-b border-zinc-900 flex justify-between items-center text-xs">
                          <span className="font-bold flex items-center gap-1.5"><Instagram size={14} className="text-pink-400" /> Instagram Reels</span>
                          <button
                            onClick={() => copyToClipboard(results.instagram.caption, "ig")}
                            className="text-zinc-500 hover:text-zinc-300 transition-colors"
                          >
                            {copiedStates["ig"] ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                          </button>
                        </div>
                        
                        <div className="relative aspect-[9/16] bg-zinc-900 flex items-center justify-center">
                          {results.thumbnail && results.thumbnail.image_base64 && (
                            <img
                              src={`data:image/jpeg;base64,${results.thumbnail.image_base64}`}
                              alt="Thumbnail"
                              className="absolute inset-0 w-full h-full object-cover opacity-60"
                            />
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/20" />
                          <div className="absolute bottom-4 left-4 right-4 text-xs space-y-2">
                            <span className="font-bold">@ratefluencer</span>
                            <p className="line-clamp-3 text-[11px] text-zinc-300 leading-normal">
                              {results.instagram.caption}
                            </p>
                            <div className="flex flex-wrap gap-1 text-[10px] text-indigo-300">
                              {results.instagram.hashtags.map((h, i) => (
                                <span key={i}>{h}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Instagram Feed Post Mock */}
                      <div className="bg-zinc-950 border border-zinc-900 rounded-3xl overflow-hidden shadow-2xl flex flex-col justify-between max-w-[340px] mx-auto w-full">
                        <div className="p-4 border-b border-zinc-900 flex justify-between items-center text-xs">
                          <span className="font-bold flex items-center gap-1.5">
                            <Instagram size={14} className="text-pink-400" /> Instagram Post
                          </span>
                          <button
                            onClick={() => copyToClipboard(results.instagram.caption, "ig-post")}
                            className="text-zinc-500 hover:text-zinc-300 transition-colors"
                          >
                            {copiedStates["ig-post"] ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                          </button>
                        </div>

                        {/* Header */}
                        <div className="p-3 flex items-center gap-2 border-b border-zinc-900/50 bg-zinc-950">
                          <div className="w-6 h-6 rounded-full bg-zinc-800 flex items-center justify-center text-[9px] font-bold">RF</div>
                          <span className="font-bold text-[11px] text-zinc-200">ratefluencer</span>
                        </div>

                        {/* Native Square Image */}
                        <div className="relative aspect-square bg-zinc-900 flex items-center justify-center">
                          {results.thumbnail && results.thumbnail.image_base64 ? (
                            <img
                              src={`data:image/jpeg;base64,${results.thumbnail.image_base64}`}
                              alt="Instagram Post"
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="text-zinc-650 text-[10px] text-center p-4">Thumbnail missing</div>
                          )}
                        </div>

                        {/* Action Bar */}
                        <div className="p-3 flex justify-between items-center bg-zinc-950">
                          <div className="flex gap-3 text-zinc-400">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="m22 2-7 20-4-9-9-4Z"/></svg>
                          </div>
                          <svg className="text-zinc-400" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
                        </div>

                        {/* Caption Section */}
                        <div className="px-3 pb-4 pt-1 text-[11px] leading-normal space-y-1 bg-zinc-950 border-t border-zinc-900/30">
                          <p className="text-zinc-300 line-clamp-3">
                            <strong className="text-zinc-100 mr-1.5">ratefluencer</strong>
                            {results.instagram.caption}
                          </p>
                          <div className="flex flex-wrap gap-1 text-[10px] text-indigo-400">
                            {results.instagram.hashtags.map((h, i) => (
                              <span key={i}>{h}</span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* LinkedIn Mock */}
                      <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-3xl shadow-2xl flex flex-col justify-between max-w-[380px] mx-auto w-full">
                        <div className="flex justify-between items-center border-b border-zinc-900 pb-3 mb-4 text-xs">
                          <span className="font-bold flex items-center gap-1.5"><Linkedin size={14} className="text-blue-400" /> LinkedIn Feed</span>
                          <button
                            onClick={() => copyToClipboard(results.linkedin.post_text, "li")}
                            className="text-zinc-500 hover:text-zinc-300 transition-colors"
                          >
                            {copiedStates["li"] ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                          </button>
                        </div>

                        <div className="space-y-4 text-xs leading-relaxed">
                          <div className="flex gap-2.5 items-center">
                            <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-[10px] font-bold">RA</div>
                            <div>
                              <span className="font-bold block text-zinc-100">Ratefluencer AI Agent</span>
                              <span className="text-[9px] text-zinc-500 block">Content Generation System</span>
                            </div>
                          </div>
                          
                          <p className="whitespace-pre-line text-zinc-300 text-[11px]">
                            {results.linkedin.post_text}
                          </p>

                          <div className="flex flex-wrap gap-1 text-[10px] text-blue-400">
                            {results.linkedin.hashtags.map((h, i) => (
                              <span key={i}>{h}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* A/B Hook test view */}
                  {activeFeatureTab === "ab-hooks" && abHooks && (
                    <div className="space-y-4">
                      {abHooks.map((h, i) => (
                        <div key={i} className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                          <div className="space-y-1">
                            <span className="px-2 py-0.5 bg-zinc-900 border border-zinc-800 text-[9px] font-bold uppercase rounded text-indigo-400">
                              {h.type}
                            </span>
                            <p className="font-semibold text-zinc-200 text-sm leading-normal">{h.hook}</p>
                            <div className="flex gap-4 text-[10px] text-zinc-500 mt-2">
                              <span>Readability: {h.readability}%</span>
                              <span>Sentiment: {h.sentiment}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-right">
                            <div>
                              <span className="text-[9px] text-zinc-500 block font-bold uppercase tracking-wider">Expected Virality</span>
                              <span className="font-extrabold text-sm text-indigo-400">{h.predicted_virality}/100</span>
                            </div>
                            <button
                              onClick={() => copyToClipboard(h.hook, `hook-${i}`)}
                              className="p-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-lg text-zinc-400 hover:text-zinc-200 transition-all duration-300"
                            >
                              {copiedStates[`hook-${i}`] ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Repurposed view */}
                  {activeFeatureTab === "repurpose" && repurposed && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Blog preview */}
                      <div className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex flex-col justify-between gap-4">
                        <div>
                          <h4 className="font-bold text-xs uppercase text-zinc-400 tracking-wider mb-3">Long-form Blog</h4>
                          <h3 className="font-bold text-zinc-100 text-sm mb-2">{repurposed.blog_post.title}</h3>
                          <div className="text-[10px] text-zinc-400 leading-relaxed max-h-48 overflow-y-auto whitespace-pre-line">
                            {repurposed.blog_post.content}
                          </div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(repurposed.blog_post.content, "blog")}
                          className="w-full flex items-center justify-center gap-1.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-semibold border border-zinc-850 rounded-xl text-xs transition-all duration-300"
                        >
                          {copiedStates["blog"] ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          Copy Article
                        </button>
                      </div>

                      {/* Twitter Thread */}
                      <div className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex flex-col justify-between gap-4">
                        <div>
                          <h4 className="font-bold text-xs uppercase text-zinc-400 tracking-wider mb-4">Twitter Thread</h4>
                          <div className="space-y-4 max-h-56 overflow-y-auto pr-1">
                            {repurposed.tweet_thread.map((tweet, i) => (
                              <div key={i} className="text-[10px] text-zinc-400 leading-relaxed border-l border-zinc-800 pl-3">
                                {tweet}
                              </div>
                            ))}
                          </div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(repurposed.tweet_thread.join("\n\n"), "tweets")}
                          className="w-full flex items-center justify-center gap-1.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-semibold border border-zinc-850 rounded-xl text-xs transition-all duration-300"
                        >
                          {copiedStates["tweets"] ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          Copy Thread
                        </button>
                      </div>

                      {/* Newsletter */}
                      <div className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex flex-col justify-between gap-4">
                        <div>
                          <h4 className="font-bold text-xs uppercase text-zinc-400 tracking-wider mb-3">Newsletter</h4>
                          <span className="font-bold text-zinc-200 text-xs block mb-1">Subj: {repurposed.newsletter.subject}</span>
                          <div className="text-[10px] text-zinc-400 leading-relaxed max-h-48 overflow-y-auto whitespace-pre-line mt-2">
                            {repurposed.newsletter.body}
                          </div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(repurposed.newsletter.body, "newsletter")}
                          className="w-full flex items-center justify-center gap-1.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-semibold border border-zinc-850 rounded-xl text-xs transition-all duration-300"
                        >
                          {copiedStates["newsletter"] ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                          Copy Mail
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Calendar view */}
                  {activeFeatureTab === "calendar" && calendar && (
                    <div className="space-y-4">
                      {calendar.map((day, idx) => (
                        <div key={idx} className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex justify-between items-start gap-4">
                          <div className="space-y-1">
                            <span className="px-2 py-0.5 bg-zinc-900 border border-zinc-800 text-[9px] font-bold uppercase rounded text-emerald-400">
                              {day.day}
                            </span>
                            <h4 className="font-bold text-zinc-200 text-sm mt-1">{day.title}</h4>
                            <p className="text-[10px] text-zinc-400 leading-relaxed">{day.angle}</p>
                            <p className="text-[10px] text-indigo-300 italic mt-1">"{day.hook}"</p>
                          </div>
                          <div className="text-right">
                            <span className="text-[9px] text-zinc-500 font-semibold uppercase block">Visual B-Roll</span>
                            <span className="text-[10px] text-zinc-400 block max-w-[180px] truncate leading-normal">
                              {day.visual}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 5-part Series view */}
                  {activeFeatureTab === "series" && series && (
                    <div className="space-y-4">
                      {series.map((ep, idx) => (
                        <div key={idx} className="bg-zinc-950 border border-zinc-900 p-5 rounded-2xl flex justify-between items-start gap-4">
                          <div className="space-y-1">
                            <span className="px-2 py-0.5 bg-zinc-900 border border-zinc-800 text-[9px] font-bold uppercase rounded text-purple-400">
                              Part {ep.part}
                            </span>
                            <h4 className="font-bold text-zinc-200 text-sm mt-1">{ep.title}</h4>
                            <p className="text-[10px] text-zinc-400 leading-relaxed">{ep.storyline}</p>
                            <p className="text-[10px] text-indigo-300 italic mt-1">"{ep.hook}"</p>
                          </div>
                          <div className="text-right">
                            <span className="text-[9px] text-zinc-500 font-semibold uppercase block">Call to Action</span>
                            <span className="text-[10px] text-emerald-400 block max-w-[180px] leading-normal font-semibold">
                              {ep.cta}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Script Text Editor */}
            <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <PenTool size={18} className="text-indigo-400" /> Interactive Script Editor
              </h2>

              <div className="space-y-4 text-xs">
                <div className="flex flex-col gap-1.5">
                  <span className="font-bold text-zinc-400">Hook Sentence</span>
                  <input
                    type="text"
                    value={results.script.hook}
                    onChange={(e) => setResults({
                      ...results,
                      script: { ...results.script, hook: e.target.value }
                    })}
                    className="px-4 py-2 bg-zinc-900 border border-zinc-850 rounded-xl outline-none focus:border-indigo-500 transition-colors text-zinc-100"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="font-bold text-zinc-400">Story Narration Outline</span>
                  <textarea
                    value={results.script.story}
                    rows={3}
                    onChange={(e) => setResults({
                      ...results,
                      script: { ...results.script, story: e.target.value }
                    })}
                    className="px-4 py-2 bg-zinc-900 border border-zinc-850 rounded-xl outline-none focus:border-indigo-500 transition-colors text-zinc-100 resize-none leading-relaxed"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <span className="font-bold text-zinc-400">Call to Action</span>
                  <input
                    type="text"
                    value={results.script.cta}
                    onChange={(e) => setResults({
                      ...results,
                      script: { ...results.script, cta: e.target.value }
                    })}
                    className="px-4 py-2 bg-zinc-900 border border-zinc-850 rounded-xl outline-none focus:border-indigo-500 transition-colors text-zinc-100"
                  />
                </div>
              </div>
            </div>

          </div>

          {/* Sidebar Visual Previewers Pane (Col 1/3) */}
          <div className="space-y-8">
            
            {/* Generated Media Studio */}
            <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
              <div className="flex justify-between items-center border-b border-zinc-900 pb-3">
                <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                  Generated Studio
                </h2>
                <div className="flex bg-zinc-900 p-0.5 rounded-lg border border-zinc-800 text-[10px] font-semibold">
                  <button
                    onClick={() => setActiveMediaTab("video")}
                    className={`px-3 py-1.5 rounded-md transition-all duration-300 flex items-center gap-1 ${
                      activeMediaTab === "video"
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                        : "text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    <Tv2 size={12} /> Video Reel
                  </button>
                  <button
                    onClick={() => setActiveMediaTab("thumbnail")}
                    className={`px-3 py-1.5 rounded-md transition-all duration-300 flex items-center gap-1 ${
                      activeMediaTab === "thumbnail"
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                        : "text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    <ImageIcon size={12} /> Thumbnail
                  </button>
                </div>
              </div>

              {/* Content View */}
              {activeMediaTab === "video" ? (
                <div className="space-y-4">
                  <div className="relative aspect-[9/16] bg-zinc-900 rounded-xl overflow-hidden flex items-center justify-center shadow-lg border border-zinc-900/60">
                    {results.video && results.video.video_base64 ? (
                      <video
                        ref={videoRef}
                        src={`data:video/mp4;base64,${results.video.video_base64}`}
                        controls
                        className="w-full h-full object-cover"
                        onTimeUpdate={handleVideoTimeUpdate}
                      />
                    ) : (
                      <div className="text-zinc-500 text-xs text-center p-8 leading-normal flex flex-col gap-2 items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-zinc-650"><path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2" ry="2"/></svg>
                        <span>Video asset not ready or failed. Try standard audio playback below.</span>
                      </div>
                    )}
                    {/* Active Subtitle overlay */}
                    {activeSubtitle && (
                      <div className="absolute bottom-16 left-4 right-4 bg-black/75 backdrop-blur-md py-2.5 px-3.5 rounded-xl border border-white/10 text-center font-bold text-xs text-yellow-400 select-none pointer-events-none shadow-xl">
                        {activeSubtitle}
                      </div>
                    )}
                  </div>

                  {results.video && results.video.video_base64 && (
                    <button
                      onClick={() => {
                        const a = document.createElement("a");
                        a.href = `data:video/mp4;base64,${results.video.video_base64}`;
                        a.download = `video_${results.topic.substring(0, 12)}.mp4`;
                        a.click();
                      }}
                      className="w-full flex items-center justify-center gap-1.5 py-3 bg-zinc-900 hover:bg-zinc-850 text-zinc-200 border border-zinc-800 font-bold rounded-xl text-xs transition-all duration-300"
                    >
                      <Download size={14} /> Download Reel MP4
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="aspect-square bg-zinc-900 rounded-xl overflow-hidden shadow-lg border border-zinc-900/60 max-w-[280px] mx-auto w-full">
                    {results.thumbnail && results.thumbnail.image_base64 ? (
                      <img
                        src={`data:image/jpeg;base64,${results.thumbnail.image_base64}`}
                        alt="Thumbnail Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-zinc-500 text-xs text-center py-10 leading-normal flex flex-col gap-2 items-center h-full justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-zinc-650"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                        <span>Thumbnail asset missing or failed generation.</span>
                      </div>
                    )}
                  </div>
                  {results.thumbnail && results.thumbnail.image_base64 && (
                    <button
                      onClick={() => {
                        const a = document.createElement("a");
                        a.href = `data:image/jpeg;base64,${results.thumbnail.image_base64}`;
                        a.download = `thumbnail_${results.topic.substring(0, 12)}.jpg`;
                        a.click();
                      }}
                      className="w-full flex items-center justify-center gap-1.5 py-3 bg-zinc-900 hover:bg-zinc-850 text-zinc-200 border border-zinc-800 font-bold rounded-xl text-xs transition-colors duration-300"
                    >
                      <Download size={14} /> Download Thumbnail
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Audio Voiceover Waveform Player */}
            <div className="bg-zinc-950 border border-zinc-900 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <Volume2 size={18} className="text-indigo-400" /> Waveform Voiceover
              </h2>

              {results.voiceover && results.voiceover.audio_base64 ? (
                <div className="space-y-4">
                  <audio
                    ref={audioRef}
                    src={`data:audio/mp3;base64,${results.voiceover.audio_base64}`}
                    onEnded={() => setAudioPlaying(false)}
                    className="hidden"
                  />

                  {/* Animated Waveform Visualizer bars */}
                  <div className="h-16 flex items-center justify-center gap-[3px] bg-zinc-900/60 rounded-xl px-4 border border-zinc-900">
                    {Array.from({ length: 28 }).map((_, i) => {
                      const height = [40, 60, 20, 80, 50, 90, 30, 70, 40, 60, 20, 85, 30, 70, 50, 90, 40, 60, 30, 80, 20, 60, 40, 75, 20, 50, 30, 60][i];
                      return (
                        <div
                          key={i}
                          className={`w-[4px] rounded-full transition-all duration-300 ${
                            audioPlaying ? "bg-indigo-500 animate-pulse" : "bg-zinc-700"
                          }`}
                          style={{ 
                            height: audioPlaying ? `${height}%` : "15%",
                            animationDelay: `${i * 35}ms`
                          }}
                        />
                      );
                    })}
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={toggleAudio}
                      className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 font-bold rounded-xl text-xs transition-colors duration-300 flex items-center justify-center gap-1.5"
                    >
                      <Volume2 size={14} />
                      {audioPlaying ? "Pause Playback" : "Play Audio Track"}
                    </button>
                    
                    <button
                      onClick={() => {
                        const a = document.createElement("a");
                        a.href = `data:audio/mp3;base64,${results.voiceover.audio_base64}`;
                        a.download = `voiceover_${results.topic.substring(0, 12)}.mp3`;
                        a.click();
                      }}
                      className="px-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-850 rounded-xl flex items-center justify-center text-zinc-300 transition-colors"
                    >
                      <Download size={14} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-zinc-650 text-xs text-center py-6">Voiceover asset missing.</div>
              )}
            </div>

            {/* YouTube Clips Fetcher Card */}
            {results && results.youtube_clips && results.youtube_clips.length > 0 && (
              <YouTubeClipsCard clips={results.youtube_clips} />
            )}

          </div>

        </div>
      )}

      {/* Brand Voice Create Modal */}
      {showVoiceModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-zinc-950 border border-zinc-800/80 p-6 rounded-2xl max-w-md w-full flex flex-col gap-5 shadow-2xl">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-lg text-zinc-100">Add Brand Voice</h3>
              <button 
                onClick={() => setShowVoiceModal(false)} 
                className="text-zinc-500 hover:text-zinc-350 text-xs font-bold uppercase transition-colors"
              >
                Close
              </button>
            </div>
            
            <form onSubmit={handleCreateVoice} className="flex flex-col gap-4 text-xs">
              <div className="flex flex-col gap-1.5">
                <span className="font-bold text-zinc-400">Profile Name</span>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tech Bro, Formal Corporate..."
                  value={newVoice.name}
                  onChange={(e) => setNewVoice({ ...newVoice, name: e.target.value })}
                  className="px-4 py-2.5 bg-zinc-900 border border-zinc-850 focus:border-indigo-500 text-zinc-200 outline-none rounded-xl"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <span className="font-bold text-zinc-400">Persona Tone</span>
                <select
                  value={newVoice.tone}
                  onChange={(e) => setNewVoice({ ...newVoice, tone: e.target.value })}
                  className="px-4 py-2.5 bg-zinc-900 border border-zinc-850 focus:border-indigo-500 text-zinc-300 outline-none rounded-xl cursor-pointer"
                >
                  <option value="professional">Professional / Expert</option>
                  <option value="casual">Casual / Conversational</option>
                  <option value="bold">Bold / Hype</option>
                  <option value="witty">Witty / Sarcastic</option>
                  <option value="techy">Developer / Technical</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <span className="font-bold text-zinc-400">Style Instructions</span>
                <textarea
                  required
                  rows={4}
                  placeholder="e.g. Always start with a shocking metric. Use simple analogies. Break sections into bullets. Avoid generic words..."
                  value={newVoice.style_guide}
                  onChange={(e) => setNewVoice({ ...newVoice, style_guide: e.target.value })}
                  className="px-4 py-2.5 bg-zinc-900 border border-zinc-850 focus:border-indigo-500 text-zinc-200 outline-none rounded-xl resize-none leading-relaxed"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <span className="font-bold text-zinc-400">Default Hashtags (comma-separated)</span>
                <input
                  type="text"
                  placeholder="e.g. ai, coding, codinghacks..."
                  value={newVoice.hashtags}
                  onChange={(e) => setNewVoice({ ...newVoice, hashtags: e.target.value })}
                  className="px-4 py-2.5 bg-zinc-900 border border-zinc-850 focus:border-indigo-500 text-zinc-200 outline-none rounded-xl"
                />
              </div>

              <button
                type="submit"
                className="py-3 bg-indigo-600 hover:bg-indigo-500 font-bold rounded-xl text-white transition-colors duration-300 mt-2"
              >
                Create and Select Voice
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
