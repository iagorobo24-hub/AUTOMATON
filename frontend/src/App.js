import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import "@/App.css";

// Pages
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import AgentsPage from "@/pages/AgentsPage";
import CryptoPage from "@/pages/CryptoPage";
import WalletPage from "@/pages/WalletPage";
import ChatPage from "@/pages/ChatPage";
import ActivityPage from "@/pages/ActivityPage";
import SettingsPage from "@/pages/SettingsPage";

// Layout
import DashboardLayout from "@/components/layout/DashboardLayout";

function App() {
  return (
    <div className="noise">
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
      </BrowserRouter>
      <Toaster 
        position="bottom-right" 
        toastOptions={{
          style: {
            background: 'rgba(10, 10, 10, 0.95)',
            border: '1px solid rgba(0, 243, 255, 0.3)',
            color: '#FAFAFA',
          },
        }}
      />
    </div>
  );
}

export default App;
