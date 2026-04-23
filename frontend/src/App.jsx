import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

import DashboardPro from './pages/DashboardPro.jsx';
import CryptoPro from './pages/CryptoPro.jsx';
import OpsMonitorPro from './pages/OpsMonitorPro.jsx';
import AgentsPage from './pages/AgentsPage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-background text-white font-geist">
        {/* Simple Pro Sidebar */}
        <nav className="w-64 border-r border-border-pro p-6 space-y-8">
          <div className="text-emerald-pro font-bold tracking-tighter text-xl mb-10">AUTOMATON_PRO</div>
          <ul className="space-y-4 text-sm font-mono">
            <li><Link to="/" className="hover:text-emerald-pro transition-colors">>> DASHBOARD</Link></li>
            <li><Link to="/crypto" className="hover:text-emerald-pro transition-colors">>> CRYPTO_TERMINAL</Link></li>
            <li><Link to="/monitor" className="hover:text-emerald-pro transition-colors">>> OPS_MONITOR</Link></li>
            <li><Link to="/agents" className="hover:text-emerald-pro transition-colors">>> AGENT_GENETICS</Link></li>
            <li><Link to="/settings" className="hover:text-emerald-pro transition-colors">>> SYS_CONFIG</Link></li>
          </ul>
        </nav>

        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<DashboardPro />} />
            <Route path="/crypto" element={<CryptoPro />} />
            <Route path="/monitor" element={<OpsMonitorPro />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
