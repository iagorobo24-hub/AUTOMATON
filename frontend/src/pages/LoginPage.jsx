import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleEnter = () => {
    setIsLoading(true);
    setTimeout(() => {
      toast.success("Bienvenido a AUTOMATON");
      navigate("/dashboard");
    }, 800);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4 relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ opacity: [0.1, 0.2, 0.1] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ opacity: [0.05, 0.15, 0.05] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md text-center relative z-10"
      >
        {/* Logo */}
        <div className="mb-12">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 mb-8 glow-cyan"
          >
            <Zap className="w-8 h-8 text-cyan-400" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="font-heading text-5xl font-bold tracking-wider text-foreground uppercase mb-2 text-glow-cyan"
          >
            Automaton
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-lg text-muted-foreground font-mono"
          >
            Nexus-9 // Agent Orchestrator
          </motion.p>
        </div>

        {/* Divider */}
        <div className="w-16 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent mx-auto mb-12" />

        {/* Enter Button */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Button
            onClick={handleEnter}
            disabled={isLoading}
            className="evo-button-primary w-full text-base py-6 rounded-xl"
            data-testid="enter-system-btn"
            aria-label="Entrar al sistema"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                Inicializando...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                Entrar al Sistema
                <ArrowRight className="w-4 h-4" />
              </span>
            )}
          </Button>
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-12 text-xs text-muted-foreground font-mono"
        >
          v2.0.0 // QwenCLI
        </motion.p>
      </motion.div>
    </div>
  );
}
