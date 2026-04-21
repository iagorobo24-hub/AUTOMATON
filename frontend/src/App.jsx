import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';

import Dashboard from './pages/Dashboard.jsx';
import Agents from './pages/Agents.jsx';
import Trades from './pages/Trades.jsx';

function Sidebar() {
  return (
    <nav style={styles.sidebar}>
      <div style={styles.logo}>AUTOMATON</div>
      <NavLink to="/" style={({ isActive }) => ({ ...styles.link, ...(isActive ? styles.active : {}) })} end>
        Dashboard
      </NavLink>
      <NavLink to="/agents" style={({ isActive }) => ({ ...styles.link, ...(isActive ? styles.active : {}) })}>
        Agentes
      </NavLink>
      <NavLink to="/trades" style={({ isActive }) => ({ ...styles.link, ...(isActive ? styles.active : {}) })}>
        Trades
      </NavLink>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div style={styles.app}>
        <Sidebar />
        <main style={styles.main}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/trades" element={<Trades />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

const styles = {
  app: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#050505',
  },
  sidebar: {
    width: '200px',
    backgroundColor: '#0a0a0a',
    borderRight: '1px solid #222',
    padding: '24px 0',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'JetBrains Mono, monospace',
  },
  logo: {
    padding: '0 24px 24px',
    fontSize: '18px',
    fontWeight: '700',
    color: '#00ff88',
    borderBottom: '1px solid #222',
    marginBottom: '16px',
  },
  link: {
    padding: '12px 24px',
    color: '#888',
    textDecoration: 'none',
    fontSize: '14px',
    transition: 'color 0.2s',
  },
  active: {
    color: '#00ff88',
    backgroundColor: '#00ff8811',
  },
  main: {
    flex: 1,
    overflow: 'auto',
  },
};

export default App;
