import { useState, useRef, useEffect } from "react";
import { 
  Send, 
  Bot, 
  User,
  Zap,
  Loader2,
  Sparkles,
  Terminal,
  Copy,
  Check
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
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
    <div className={cn(
      "flex gap-3 animate-slide-up",
      isUser ? "flex-row-reverse" : ""
    )}>
      <div className={cn(
        "w-8 h-8 rounded-sm flex items-center justify-center shrink-0",
        isUser ? "bg-secondary/20" : "bg-primary/20"
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-secondary" />
        ) : (
          <Bot className="w-4 h-4 text-primary" />
        )}
      </div>
      
      <div className={cn(
        "max-w-[80%] p-4 rounded-sm border relative group",
        isUser 
          ? "bg-secondary/10 border-secondary/30" 
          : "bg-white/5 border-white/10"
      )}>
        <div className="text-sm whitespace-pre-wrap">
          {message.content}
        </div>
        
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/10">
          <span className="text-[10px] text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
          
          <button
            onClick={handleCopy}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white/10 rounded"
          >
            {copied ? (
              <Check className="w-3 h-3 text-cyber-green" />
            ) : (
              <Copy className="w-3 h-3 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

const SuggestedPrompt = ({ prompt, onClick }) => (
  <button
    onClick={() => onClick(prompt)}
    className="px-3 py-2 text-xs text-left rounded-sm border border-white/10 hover:border-primary/50 hover:bg-primary/5 transition-colors"
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

  const suggestedPrompts = [
    "Analiza el mercado crypto actual",
    "¿Qué agentes debería replicar?",
    "Detecta oportunidades de negocio",
    "Optimiza el uso de tokens LLM",
    "Estado del sistema de agentes",
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

  return (
    <div className="h-[calc(100vh-8rem)]" data-testid="chat-page">
      <Card className="glass border-white/10 h-full flex flex-col">
        {/* Header */}
        <CardHeader className="pb-2 border-b border-white/10 shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-sm bg-primary/20 flex items-center justify-center glow-cyan">
                <Zap className="w-5 h-5 text-primary" />
              </div>
              <div>
                <CardTitle className="font-heading text-lg tracking-wider uppercase">
                  Orchestrator AI
                </CardTitle>
                <p className="text-xs text-muted-foreground flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyber-green animate-pulse" />
                  Online • GPT-4o
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-muted-foreground" />
              <span className="text-xs font-mono text-muted-foreground">
                SESSION: {sessionId?.slice(0, 8) || 'NEW'}
              </span>
            </div>
          </div>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 overflow-hidden p-0">
          <ScrollArea className="h-full p-6" ref={scrollRef}>
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-sm bg-primary/10 flex items-center justify-center mb-6 glow-cyan">
                  <Sparkles className="w-8 h-8 text-primary" />
                </div>
                <h3 className="font-heading text-xl mb-2">
                  Bienvenido al Orquestador
                </h3>
                <p className="text-sm text-muted-foreground max-w-md mb-8">
                  Soy tu asistente AI para gestionar agentes autoreplicantes, 
                  analizar mercados crypto y detectar oportunidades de negocio.
                </p>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
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
              <div className="space-y-6">
                {messages.map((msg, i) => (
                  <MessageBubble 
                    key={i} 
                    message={msg} 
                    isUser={msg.role === 'user'} 
                  />
                ))}
                
                {loading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-sm bg-primary/20 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                    <div className="p-4 rounded-sm bg-white/5 border border-white/10">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Procesando...
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t border-white/10 shrink-0">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu mensaje..."
              className="min-h-[44px] max-h-32 bg-black/50 border-white/10 resize-none"
              disabled={loading}
              data-testid="chat-input"
            />
            <Button 
              type="submit"
              disabled={!input.trim() || loading}
              className="bg-primary text-black hover:bg-primary/90 px-4 shrink-0"
              data-testid="send-message-btn"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </form>
          <p className="text-[10px] text-muted-foreground mt-2 text-center">
            Shift + Enter para nueva línea • Enter para enviar
          </p>
        </div>
      </Card>
    </div>
  );
}
