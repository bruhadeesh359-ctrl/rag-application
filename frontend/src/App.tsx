import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, Search, Activity, FileText, Settings, Microscope, FlaskConical } from 'lucide-react';
import Overview from './pages/Overview';
import Playground from './pages/Playground';
import Traces from './pages/Traces';
import Documents from './pages/Documents';
import Experiments from './pages/Experiments';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-[var(--color-background)] text-[var(--color-text-main)] font-sans overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r border-[var(--color-border)] bg-[var(--color-surface)] flex flex-col">
          <div className="p-4 border-b border-[var(--color-border)] flex items-center gap-2">
            <Microscope className="w-6 h-6 text-[var(--color-primary)]" />
            <h1 className="font-semibold text-sm tracking-wide text-white">RAG Observability</h1>
          </div>
          
          <nav className="flex-1 p-2 space-y-1 mt-4">
            <SidebarItem to="/" icon={<LayoutDashboard size={18}/>} label="Overview" />
            <SidebarItem to="/rag" icon={<Search size={18}/>} label="RAG Playground" />
            <SidebarItem to="/observability/traces" icon={<Activity size={18}/>} label="Traces & Latency" />
            <SidebarItem to="/documents" icon={<FileText size={18}/>} label="Documents" />
            <SidebarItem to="/experiments" icon={<FlaskConical size={18}/>} label="Experiments" />
          </nav>
          
          <div className="p-4 border-t border-[var(--color-border)]">
            <SidebarItem to="/system" icon={<Settings size={18}/>} label="System" />
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto bg-[var(--color-background)]">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/rag" element={<Playground />} />
            <Route path="/observability/traces" element={<Traces />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/experiments" element={<Experiments />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function SidebarItem({ icon, label, to }: { icon: React.ReactNode, label: string, to: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => 
        `w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors ${
          isActive 
            ? 'bg-[var(--color-border)] text-white font-medium' 
            : 'text-[var(--color-text-muted)] hover:text-white hover:bg-[#232730]'
        }`
      }
    >
      {icon}
      {label}
    </NavLink>
  );
}

export default App;
