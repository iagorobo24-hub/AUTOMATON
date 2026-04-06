import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Bot, User, Zap, Loader2, Sparkles, Copy, Check } from "lucide-react";
import { toast } from "sonner";
import { chatAPI } from "@/lib/api";

const MessageBubble = ({ message, isUser }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${isUser ? "bg-cyan-500/10" : "bg-white/5"}`}>
        {isUser ? <User className="w-4 h-4 text-cyan-400" /> : <Bot className="w-4 h-4 text-muted-foreground" />}
      </div>
      <div className="group relative max-w-[75%]">
        <div className={`px-4 py-3 text-sm leading-relaxed rounded-xl ${isUser ? "bg-cyan-500 text-black rounded-br-md" : "glass-card rounded-bl-md"}`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
        <div className={`flex items-center gap-2 mt-1.5 ${isUser ? "justify-end" : "justify-start"}`}>
          <span className="text-[11px] text-muted-foreground font-mono">
            {new Date(message.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
          </span>
          {!isUser && (
            <button onClick={handleCopy} className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-white/5" aria-label="Copiar mensaje">
              {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5 text-muted-foreground" />}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

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

  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [messages]);

  const sendMessage = async (content) => {
    if (!content.trim()) return;
    const userMessage = { role: "user", content: content.trim(), timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await chatAPI.send(content, sessionId || 'default');
      const assistantMessage = { role: "assistant", content: response.data.response, timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, assistantMessage]);
      if (!sessionId) setSessionId(response.data.session_id);
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Error al comunicarse con el orquestador");
      setMessages(prev => [...prev, { role: "assistant", content: "Error de conexión. El orquestador no está disponible.", timestamp: new Date().toISOString() }]);
    } finally { setLoading(false); }
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(input); };
  const handleKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); } };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) { textarea.style.height = 'auto'; textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'; }
  };

  return (
    <div className="min-h-screen bg-background" data-testid="chat-page">
      <div className="max-w-3xl mx-auto h-[calc(100vh-2rem)] flex flex-col">
        {/* Header */}
        <div className="glass-card rounded-t-xl border-b border-white/5 px-6 py-4 shrink-0 rounded-none">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <Zap className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-foreground">Orquestador IA</h2>
                <p className="text-xs text-muted-foreground flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" /> En línea
                </p>
              </div>
            </div>
            {sessionId && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5">
                <span className="text-[12px] text-muted-foreground font-mono">{sessionId.slice(0, 8)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center py-20">
              <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.4 }}
                className="w-16 h-16 rounded-xl bg-cyan-500/10 flex items-center justify-center mb-6">
                <Sparkles className="w-8 h-8 text-cyan-400" />
              </motion.div>
              <h3 className="text-xl font-semibold text-foreground mb-2">Orquestador IA</h3>
              <p className="text-sm text-muted-foreground max-w-md mb-8 leading-relaxed">
                Tu asistente de IA para gestionar agentes auto-replicables, analizar mercados cripto y detectar oportunidades.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-lg">
                {suggestedPrompts.map((prompt, i) => (
                  <motion.button key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                    onClick={() => sendMessage(prompt)}
                    className="px-4 py-2.5 text-sm text-left rounded-lg glass-card border border-white/5 text-foreground hover:border-cyan-500/30 hover:bg-cyan-500/5 transition-all">
                    {prompt}
                  </motion.button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 py-4">
              {messages.map((msg, i) => (
                <MessageBubble key={i} message={msg} isUser={msg.role === 'user'} />
              ))}
              {loading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0"><Bot className="w-4 h-4 text-muted-foreground" /></div>
                  <div className="px-4 py-3 glass-card rounded-xl">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="w-4 h-4 animate-spin" /> Pensando...
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="glass-card border-t border-white/5 px-6 py-4 shrink-0 rounded-b-xl rounded-none">
          <form onSubmit={handleSubmit} className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea ref={textareaRef} value={input} onChange={(e) => { setInput(e.target.value); adjustTextareaHeight(); }} onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje..." rows={1} className="evo-input rounded-xl resize-none" disabled={loading} data-testid="chat-input" />
            </div>
            <button type="submit" disabled={!input.trim() || loading}
              className="w-11 h-11 rounded-lg bg-cyan-500 text-black flex items-center justify-center hover:bg-cyan-400 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              data-testid="send-message-btn" aria-label="Enviar mensaje">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
          <p className="text-[11px] text-muted-foreground mt-2 text-center">Shift + Enter para nueva línea • Enter para enviar</p>
        </div>
      </div>
    </div>
  );
}
