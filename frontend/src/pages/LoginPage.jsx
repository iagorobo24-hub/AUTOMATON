import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Zap, ArrowRight, Bot, TrendingUp, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleEnter = () => {
    setIsLoading(true);
    setTimeout(() => {
      toast.success("System initialized");
      navigate("/dashboard");
    }, 800);
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url('https://images.unsplash.com/photo-1746470427657-eb0b0115455f?q=80&w=2000&auto=format&fit=crop')"
        }}
      />
      
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/85 backdrop-blur-sm" />
      
      {/* Hero glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-hero-glow opacity-50" />
      
      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        {/* Logo */}
        <div className="mb-12 text-center animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-sm bg-primary/10 border border-primary/30 mb-6 glow-cyan-intense">
            <Zap className="w-10 h-10 text-primary" />
          </div>
          <h1 className="font-display font-black text-5xl md:text-7xl tracking-tighter text-white mb-4">
            AUTOMATON
          </h1>
          <p className="font-heading text-xl text-muted-foreground tracking-wide">
            SELF-REPLICATING AI AGENT ORCHESTRATOR
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mb-12 animate-slide-up stagger-2">
          <div className="glass p-6 rounded-sm border border-white/10 card-hover">
            <Bot className="w-8 h-8 text-primary mb-4" />
            <h3 className="font-heading font-bold text-lg mb-2">AUTONOMOUS AGENTS</h3>
            <p className="text-sm text-muted-foreground">
              Self-replicating agents that evolve based on performance
            </p>
          </div>
          <div className="glass p-6 rounded-sm border border-white/10 card-hover">
            <TrendingUp className="w-8 h-8 text-cyber-green mb-4" />
            <h3 className="font-heading font-bold text-lg mb-2">CRYPTO ANALYSIS</h3>
            <p className="text-sm text-muted-foreground">
              Real-time market data and opportunity detection
            </p>
          </div>
          <div className="glass p-6 rounded-sm border border-white/10 card-hover">
            <Shield className="w-8 h-8 text-secondary mb-4" />
            <h3 className="font-heading font-bold text-lg mb-2">REAL MONETIZATION</h3>
            <p className="text-sm text-muted-foreground">
              Stripe + Crypto payments for agent funding
            </p>
          </div>
        </div>

        {/* Enter Button */}
        <Button
          onClick={handleEnter}
          disabled={isLoading}
          className="bg-primary text-black hover:bg-primary/90 font-bold uppercase tracking-widest text-sm py-6 px-12 rounded-sm shadow-[0_0_30px_rgba(0,243,255,0.4)] hover:shadow-[0_0_50px_rgba(0,243,255,0.6)] transition-shadow"
          data-testid="enter-system-btn"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              INITIALIZING...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              ENTER SYSTEM
              <ArrowRight className="w-5 h-5" />
            </span>
          )}
        </Button>

        {/* Version */}
        <p className="mt-8 text-xs font-mono text-muted-foreground/50">
          v1.0.0 // ORCHESTRATOR ONLINE
        </p>
      </div>
    </div>
  );
}
