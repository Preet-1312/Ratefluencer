import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Trends from "./pages/Trends";
import History from "./pages/History";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-zinc-950 text-zinc-100 selection:bg-indigo-500/30 selection:text-indigo-200">
        
        {/* Sidebar Navigation */}
        <Navbar />

        {/* Main Content View Switcher */}
        <main className="flex-1 flex flex-col min-w-0">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/history" element={<History />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
        
      </div>
    </Router>
  );
}