import React from "react";
import { Link } from "react-router-dom";
import { 
  Sparkles, 
  TrendingUp, 
  FileText, 
  BarChart3, 
  Video, 
  Share2, 
  Layers, 
  ArrowRight 
} from "lucide-react";

export default function Home() {
  const features = [
    {
      title: "Real-time Trend Discovery",
      desc: "Scrape top trends across News & YouTube APIs automatically ranked by scikit-learn.",
      icon: TrendingUp,
      color: "from-blue-500 to-indigo-500",
    },
    {
      title: "AI Script Generator",
      desc: "Draft professional, engaging 30-60s scripts optimized for high retention hooks.",
      icon: FileText,
      color: "from-indigo-500 to-purple-500",
    },
    {
      title: "ML Virality Forecaster",
      desc: "Foresee Instagram and LinkedIn views, saves, and likes using Ridge regression models.",
      icon: BarChart3,
      color: "from-purple-500 to-pink-500",
    },
    {
      title: "Automated Video assembly",
      desc: "Integrate B-roll, gTTS audio, and subtitles dynamically into an MP4 file with MoviePy.",
      icon: Video,
      color: "from-pink-500 to-rose-500",
    },
    {
      title: "Platform Repurposing",
      desc: "Instantly spin scripts into complete SEO blog posts, Twitter threads, and newsletters.",
      icon: Share2,
      color: "from-rose-500 to-orange-500",
    },
    {
      title: "Brand Voice Manager",
      desc: "Save custom tone and personality guidelines to tailor prompt generation contexts.",
      icon: Layers,
      color: "from-orange-500 to-amber-500",
    },
  ];

  return (
    <div className="flex-1 min-h-screen bg-[#09090b] text-white flex flex-col justify-center relative overflow-hidden px-8 py-16">
      
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-3xl -z-10" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-3xl -z-10" />

      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center flex flex-col items-center gap-6">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide uppercase animate-pulse">
          <Sparkles size={14} /> AI-Powered Content Engine
        </div>
        
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-none bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-transparent">
          Automate Your Entire <br/>
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
            Reel Content Pipeline
          </span>
        </h1>

        <p className="text-zinc-400 text-lg md:text-xl max-w-2xl leading-relaxed">
          From trends scraping and script writing to AI voiceover, subtitle rendering, and MoviePy assembly. Powered by Groq LLaMA 3.3 & scikit-learn models.
        </p>

        <div className="flex gap-4 mt-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-indigo-600/30 hover:shadow-indigo-500/40 hover:-translate-y-0.5 group"
          >
            Launch Workspace
            <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            to="/trends"
            className="px-8 py-4 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-semibold rounded-xl border border-zinc-800 hover:border-zinc-700 transition-all duration-300"
          >
            Explore Trends
          </Link>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="max-w-6xl mx-auto mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((f, idx) => {
          const Icon = f.icon;
          return (
            <div
              key={idx}
              className="bg-zinc-950 border border-zinc-800/80 p-8 rounded-2xl flex flex-col gap-4 hover:border-zinc-700/60 transition-all duration-300 hover:scale-[1.02] shadow-xl group"
            >
              <div className={`p-3 w-fit rounded-xl bg-gradient-to-tr ${f.color} text-white shadow-md shadow-indigo-500/5`}>
                <Icon size={20} className="group-hover:rotate-12 transition-transform duration-300" />
              </div>
              <h3 className="text-zinc-100 font-bold text-lg">{f.title}</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
