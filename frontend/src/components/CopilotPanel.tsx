import React, { useState, useRef, useEffect, useCallback } from "react";
import { DashboardContext } from "../types/dashboard";
import { fetchExplain } from "../services/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface CopilotPanelProps {
  isOpen: boolean;
  onClose: () => void;
  context: DashboardContext;
}

function buildStarterPrompts(ctx: DashboardContext): string[] {
  const prompts = [
    `Why is planning health ${ctx.status?.toLowerCase() ?? "low"}?`,
    "What changed most this cycle?",
    "What should the planner do next?",
  ];
  if (ctx.drivers?.location) {
    prompts.push(`Why is ${ctx.drivers.location} driving the most changes?`);
  }
  return prompts;
}

function buildGreeting(ctx: DashboardContext): string {
  const insight = ctx.aiInsight ? ctx.aiInsight.slice(0, 120) + (ctx.aiInsight.length > 120 ? "…" : "") : "N/A";
  return (
    `I've loaded the current planning analysis context.\n\n` +
    `📊 Planning Health: ${ctx.planningHealth}/100 (${ctx.status})\n` +
    `📦 Changed Records: ${ctx.changedRecordCount} of ${ctx.totalRecords}\n` +
    `⚠️ Risk Level: ${ctx.riskSummary?.level ?? "N/A"}\n\n` +
    `AI Insight: ${insight}\n\n` +
    `You can ask why planning health is low, which drivers caused the risk, what changed, or what actions are recommended.`
  );
}

function buildFallbackAnswer(question: string, ctx: DashboardContext): string {
  return (
    `Based on the current dashboard context (backend unavailable):\n\n` +
    `${ctx.aiInsight ?? ""}\n\n` +
    `Root Cause: ${ctx.rootCause ?? "N/A"}\n\n` +
    `Recommended Actions:\n${(ctx.recommendedActions ?? []).map((a) => `• ${a}`).join("\n")}`
  );
}

export const CopilotPanel: React.FC<CopilotPanelProps> = ({ isOpen, onClose, context }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const prevOpenRef = useRef(false);

  // Initialize greeting when panel opens
  useEffect(() => {
    if (isOpen && !prevOpenRef.current) {
      setMessages([
        { role: "assistant", content: buildGreeting(context), timestamp: Date.now() },
      ]);
    }
    prevOpenRef.current = isOpen;
  }, [isOpen, context]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 100);
  }, [isOpen]);

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: question.trim(), timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const timeoutId = setTimeout(() => {
      setLoading(false);
      setInput(question.trim());
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⏱ Request timed out. Your question has been preserved — please try again.",
          timestamp: Date.now(),
        },
      ]);
    }, 6000);

    try {
      const res = await fetchExplain({
        question: question.trim(),
        mode: "cached",
        context,
      });
      clearTimeout(timeoutId);
      const answer = res.answer || res.aiInsight || buildFallbackAnswer(question, context);
      setMessages((prev) => [...prev, { role: "assistant", content: answer, timestamp: Date.now() }]);
    } catch {
      clearTimeout(timeoutId);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: buildFallbackAnswer(question, context), timestamp: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  }, [loading, context]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  if (!isOpen) return null;

  const starters = buildStarterPrompts(context);

  return (
    <div className="fixed top-0 right-0 h-full w-[400px] bg-[#161b22] border-l border-[#21262d] flex flex-col z-40 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#21262d]">
        <div className="flex items-center gap-2">
          <span className="text-blue-400 text-lg">✦</span>
          <span className="text-sm font-semibold text-white">Planning Copilot</span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition text-lg leading-none"
          aria-label="Close Copilot panel"
        >
          ×
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-xl px-3 py-2 text-xs whitespace-pre-wrap leading-relaxed ${
                msg.role === "user"
                  ? "bg-blue-900/40 text-blue-100 border border-blue-500/30"
                  : "bg-[#0d1117] text-gray-300 border border-[#21262d]"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#0d1117] border border-[#21262d] rounded-xl px-3 py-2 text-xs text-gray-400">
              <span className="animate-pulse">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Starter prompts */}
      {messages.length <= 1 && !loading && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {starters.map((prompt, i) => (
            <button
              key={i}
              onClick={() => sendMessage(prompt)}
              className="text-xs px-2 py-1 rounded-lg bg-blue-900/20 border border-blue-500/30 text-blue-400 hover:bg-blue-900/40 transition"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t border-[#21262d] flex gap-2 items-end">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the planning data…"
          rows={2}
          className="flex-1 bg-[#0d1117] border border-[#21262d] rounded-lg px-3 py-2 text-xs text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500/50"
          disabled={loading}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="px-3 py-2 rounded-lg bg-blue-900/30 border border-blue-500/30 text-blue-400 text-xs font-medium hover:bg-blue-900/50 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
};
