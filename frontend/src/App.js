import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
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

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="crypto" element={<CryptoPage />} />
          <Route path="wallet" element={<WalletPage />} />
          <Route path="activity" element={<ActivityPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
      <Toaster 
        position="bottom-right" 
        toastOptions={{
          style: {
            background: '#fff',
            border: '1px solid rgba(0,0,0,0.08)',
            color: '#1a1a1a',
            borderRadius: '14px',
            boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
            fontSize: '14px',
            fontWeight: '500',
          },
        }}
      />
    </BrowserRouter>
  );
}

export default App;
