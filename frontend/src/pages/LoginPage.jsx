import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleEnter = () => {
    setIsLoading(true);
    setTimeout(() => {
      toast.success("Welcome to Automaton");
      navigate("/dashboard");
    }, 800);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#F5F3EF] px-4">
      <div className="w-full max-w-md text-center">
        {/* Logo */}
        <div className="mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#D97757]/10 mb-6">
            <svg
              width="32"
              height="32"
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="16" cy="16" r="12" stroke="#D97757" strokeWidth="2" />
              <circle cx="16" cy="16" r="4" fill="#D97757" />
            </svg>
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-gray-900 mb-2">
            Automaton
          </h1>
          <p className="text-lg text-gray-500 font-light">
            AI Agent Orchestrator
          </p>
        </div>

        {/* Divider */}
        <div className="w-12 h-px bg-gray-200 mx-auto mb-10" />

        {/* Enter Button */}
        <Button
          onClick={handleEnter}
          disabled={isLoading}
          className="w-full bg-[#D97757] hover:bg-[#C46A4C] text-white font-medium text-base py-6 rounded-2xl shadow-sm transition-all duration-200 hover:shadow-md disabled:opacity-80"
          data-testid="enter-system-btn"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Loading...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              Continue
              <ArrowRight className="w-4 h-4" />
            </span>
          )}
        </Button>

        {/* Footer */}
        <p className="mt-10 text-xs text-gray-400">
          v1.0.0
        </p>
      </div>
    </div>
  );
}
