import React from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Home, 
  LayoutDashboard, 
  TrendingUp, 
  History, 
  BarChart3, 
  Sparkles 
} from "lucide-react";

export default function Navbar() {
  const location = useLocation();

  const menuItems = [
    { name: "Home", path: "/", icon: Home },
    { name: "Workspace", path: "/dashboard", icon: LayoutDashboard },
    { name: "Trends", path: "/trends", icon: TrendingUp },
    { name: "History", path: "/history", icon: History },
    { name: "Analytics", path: "/analytics", icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col justify-between h-screen sticky top-0">
      <div className="flex flex-col gap-6 p-6">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 px-2 py-1">
          <div className="bg-gradient-to-tr from-indigo-600 to-violet-600 p-2 rounded-xl text-white shadow-lg shadow-indigo-500/20">
            <Sparkles size={20} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-200 to-white bg-clip-text text-transparent">
              Ratefluencer
            </h1>
            <span className="text-[10px] text-indigo-400 font-semibold tracking-widest uppercase">
              Viral Agent
            </span>
          </div>
        </Link>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1.5 mt-8">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 group ${
                  isActive
                    ? "bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 border border-transparent"
                }`}
              >
                <Icon
                  size={18}
                  className={`transition-transform duration-300 group-hover:scale-110 ${
                    isActive ? "text-indigo-400" : "text-zinc-400 group-hover:text-zinc-300"
                  }`}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Branding */}
      <div className="p-6 border-t border-zinc-900">
        <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800/40 text-center">
          <p className="text-xs text-zinc-500 font-medium">Ratefluencer v2.0</p>
          <p className="text-[10px] text-zinc-600 mt-0.5">Hackathon Build</p>
        </div>
      </div>
    </aside>
  );
}
