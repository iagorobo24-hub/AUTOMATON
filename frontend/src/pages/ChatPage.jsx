import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Zap,
  Loader2,
  Sparkles,
  Copy,
  Check
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MessageBubble = ({ message, isUser }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? "bg-[#D97757]/10" : "bg-[#F5F3EF]"}`}>
        {isUser ? (
          <User className="w-4 h-4 text-[#D97757]" />
        ) : (
          <Bot className="w-4 h-4 text-[#86868b]" />
        )}
      </div>

      <div className={`group relative max-w-[75%] ${isUser ? "" : ""}`}>
        <div className={`px-4 py-3 text-[15px] leading-relaxed ${
          isUser
            ? "bg-[#D97757] text-white rounded-2xl rounded-br-md"
            : "bg-white text-[#1a1a1a] rounded-2xl rounded-bl-md border border-black/5 shadow-sm"
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>

        <div className={`flex items-center gap-2 mt-1.5 ${isUser ? "justify-end" : "justify-start"}`}>
          <span className="text-[11px] text-[#86868b]">
            {new Date(message.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
          </span>
          {!isUser && (
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full hover:bg-[#F5F3EF]"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-[#34C759]" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-[#86868b]" />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const SuggestedPrompt = ({ prompt, onClick }) => (
  <button
    onClick={() => onClick(prompt)}
    className="px-4 py-2.5 text-[14px] text-left rounded-full border border-black/10 text-[#1a1a1a] bg-white hover:border-[#D97757]/30 hover:bg-[#D97757]/5 transition-colors"
  >
    {prompt}
  </button>
);

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  const suggestedPrompts = [
    "Analiza el mercado cripto actual",
    "¿Qué agentes debería replicar?",
    "Detectar oportunidades de negocio",
    "Optimizar uso de tokens LLM",
    "Resumen del estado del sistema",
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (content) => {
    if (!content.trim()) return;

    const userMessage = {
      role: "user",
      content: content.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: content,
        session_id: sessionId
      });

      const assistantMessage = {
        role: "assistant",
        content: response.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Error al comunicarse con el orquestador");

      const errorMessage = {
        role: "assistant",
        content: "Error de conexión. El orquestador no está disponible temporalmente.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F3EF]" data-testid="chat-page">
      <div className="max-w-3xl mx-auto h-[calc(100vh-2rem)] flex flex-col">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-xl border-b border-black/5 px-6 py-4 shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#D97757]/10 flex items-center justify-center">
                <Zap className="w-5 h-5 text-[#D97757]" />
              </div>
              <div>
                <h2 className="text-[17px] font-semibold text-[#1a1a1a]">
                  Orquestador IA
                </h2>
                <p className="text-[13px] text-[#86868b] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#34C759]" />
                  En línea
                </p>
              </div>
            </div>

            {sessionId && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F5F3EF]">
                <span className="text-[12px] text-[#86868b] font-mono">
                  {sessionId.slice(0, 8)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-20">
              <div className="w-16 h-16 rounded-full bg-[#D97757]/10 flex items-center justify-center mb-6">
                <Sparkles className="w-8 h-8 text-[#D97757]" />
              </div>
              <h3 className="text-[22px] font-semibold text-[#1a1a1a] mb-2">
                Orquestador IA
              </h3>
              <p className="text-[15px] text-[#86868b] max-w-md mb-8 leading-relaxed">
                Tu asistente de IA para gestionar agentes auto-replicables,
                analizar mercados cripto y detectar oportunidades de negocio.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-lg">
                {suggestedPrompts.map((prompt, i) => (
                  <SuggestedPrompt
                    key={i}
                    prompt={prompt}
                    onClick={sendMessage}
                  />
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 py-6">
              {messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  message={msg}
                  isUser={msg.role === 'user'}
                />
              ))}

              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#F5F3EF] flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 text-[#86868b]" />
                  </div>
                  <div className="px-4 py-3 bg-white rounded-2xl rounded-bl-md border border-black/5 shadow-sm">
                    <div className="flex items-center gap-2 text-[14px] text-[#86868b]">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Pensando...
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="bg-white/80 backdrop-blur-xl border-t border-black/5 px-6 py-4 shrink-0">
          <form onSubmit={handleSubmit} className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  adjustTextareaHeight();
                }}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje..."
                rows={1}
                className="w-full px-4 py-3 rounded-2xl border border-black/10 text-[15px] text-[#1a1a1a] bg-[#F5F3EF] focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] transition-all resize-none placeholder:text-[#86868b]"
                disabled={loading}
                data-testid="chat-input"
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="w-11 h-11 rounded-full bg-[#D97757] text-white flex items-center justify-center hover:bg-[#D97757]/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0 shadow-sm shadow-[#D97757]/20"
              data-testid="send-message-btn"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
          <p className="text-[11px] text-[#86868b] mt-2 text-center">
            Shift + Enter para nueva línea • Enter para enviar
          </p>
        </div>
      </div>
    </div>
  );
}
