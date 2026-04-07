import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Toaster } from "@/components/ui/sonner";
import "@/App.css";

import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import AgentsPage from "@/pages/AgentsPage";
import CryptoPage from "@/pages/CryptoPage";
import WalletPage from "@/pages/WalletPage";
import ChatPage from "@/pages/ChatPage";
import ActivityPage from "@/pages/ActivityPage";
import SettingsPage from "@/pages/SettingsPage";

import DashboardLayout from "@/components/layout/DashboardLayout";

// ── Page transition wrapper ──
function AnimatedOutlet({ children }) {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<AnimatedOutlet><DashboardPage /></AnimatedOutlet>} />
          <Route path="agents" element={<AnimatedOutlet><AgentsPage /></AnimatedOutlet>} />
          <Route path="crypto" element={<AnimatedOutlet><CryptoPage /></AnimatedOutlet>} />
          <Route path="wallet" element={<AnimatedOutlet><WalletPage /></AnimatedOutlet>} />
          <Route path="activity" element={<AnimatedOutlet><ActivityPage /></AnimatedOutlet>} />
          <Route path="chat" element={<AnimatedOutlet><ChatPage /></AnimatedOutlet>} />
          <Route path="settings" element={<AnimatedOutlet><SettingsPage /></AnimatedOutlet>} />
        </Route>
      </Routes>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'hsl(240 10% 8%)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'hsl(0 0% 98%)',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            fontSize: '14px',
            fontWeight: '500',
          },
        }}
      />
    </BrowserRouter>
  );
}

export default App;
