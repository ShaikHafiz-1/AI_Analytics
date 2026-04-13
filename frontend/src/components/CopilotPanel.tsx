import React, { useState, useRef, useEffect, useCallback } from "react";
import { DashboardContext, DashboardResponse } from "../types/dashboard";
import { fetchExplain } from "../services/api";
import {
  buildSmartPrompts,
  buildEntityPrompts,
  selectDiversePrompts,
  buildFollowUps,
} from "../utils/promptGenerator";
import {
  buildGreeting,
  buildFallbackAnswer,
  filterDetailsByEntity,
  contextLabel,
} from "../utils/answerGenerator";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  followUps?: string[];
}

interface CopilotPanelProps {
  isOpen: boolean;
  onClose: () => void;
  context: DashboardContext;
  selectedEntity?: { type: string; item: string } | null;
  fullData?: DashboardResponse | null;
}

// ---------------------------------------------------------------------------
// Dynamic smart prompts — business-oriented, data-aware
// (Extracted to utils/promptGenerator.ts)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Follow-up suggestions
// (Extracted to utils/promptGenerator.ts)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Greeting
// (Extracted to utils/answerGenerator.ts)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Enhanced fallback answer engine
// (Extracted to utils/answerGenerator.ts)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export const CopilotPanel: React.FC<CopilotPanelProps> = ({ isOpen, onClose, context, selectedEntity }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const prevOpenRef = useRef(false);
  const prevEntityRef = useRef<string | null>(null);

  useEffect(() => {
    const entityKey = selectedEntity ? `${selectedEntity.type}:${selectedEntity.item}` : null;
    if (isOpen && (!prevOpenRef.current || entityKey !== prevEntityRef.current)) {
      const greeting: ChatMessage = { role: "assistant", content: buildGreeting(context, selectedEntity), timestamp: Date.now() };
      if (prevOpenRef.current && entityKey !== prevEntityRef.current) {
        setMessages((prev) => [...prev, greeting]);
      } else {
        setMessages([greeting]);
      }
      prevEntityRef.current = entityKey;
    }
    prevOpenRef.current = isOpen;
  }, [isOpen, context, selectedEntity]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
  useEffect(() => { if (isOpen) setTimeout(() => inputRef.current?.focus(), 100); }, [isOpen]);

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: question.trim(), timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const timeoutId = setTimeout(() => {
      setLoading(false);
      setInput(question.trim());
      setMessages((prev) => [...prev, { role: "assistant", content: "⏱ Request timed out. Your question has been preserved — please try again.", timestamp: Date.now() }]);
    }, 6000);

    try {
      const res = await fetchExplain({ question: question.trim(), context });
      clearTimeout(timeoutId);
      const answer = res.answer || res.aiInsight || buildFallbackAnswer(question, context, selectedEntity);
      const followUps = (res as any).followUpQuestions || buildFollowUps(question, context, selectedEntity);
      
      // Build comprehensive response with new fields
      let finalAnswer = answer;
      
      // Add supporting metrics if available
      const supportingMetrics = (res as any).supportingMetrics;
      if (supportingMetrics && answer) {
        finalAnswer = `${answer}\n\n📊 Supporting Metrics:\n• Changed: ${supportingMetrics.changedRecordCount}/${supportingMetrics.totalRecords}\n• Trend: ${supportingMetrics.trendDelta >= 0 ? "+" : ""}${supportingMetrics.trendDelta?.toLocaleString()}\n• Health: ${supportingMetrics.planningHealth}/100`;
      }
      
      // Add comparison metrics if available
      const comparisonMetrics = (res as any).comparisonMetrics;
      if (comparisonMetrics && comparisonMetrics.metrics) {
        finalAnswer += `\n\n📊 Comparison:\n${JSON.stringify(comparisonMetrics, null, 2)}`;
      }
      
      // Add supplier metrics if available
      const supplierMetrics = (res as any).supplierMetrics;
      if (supplierMetrics && supplierMetrics.suppliers) {
        finalAnswer += `\n\n🏭 Suppliers at ${supplierMetrics.location}:\n`;
        supplierMetrics.suppliers.forEach((s: any) => {
          finalAnswer += `• ${s.supplier}: ${s.affectedRecords} records, Forecast: ${s.forecastImpact >= 0 ? "+" : ""}${s.forecastImpact}, Design changes: ${s.designChanges}\n`;
        });
      }
      
      // Add record comparison if available
      const recordComparison = (res as any).recordComparison;
      if (recordComparison && recordComparison.materialId) {
        finalAnswer += `\n\n📋 Record Comparison: ${recordComparison.materialId}\n`;
        finalAnswer += `Current: Forecast ${recordComparison.current.forecast}, ROJ ${recordComparison.current.roj}\n`;
        finalAnswer += `Previous: Forecast ${recordComparison.previous.forecast}, ROJ ${recordComparison.previous.roj}\n`;
        finalAnswer += `Changes: Forecast ${recordComparison.changes.forecastDelta >= 0 ? "+" : ""}${recordComparison.changes.forecastDelta}`;
      }
      
      // Add explainability note if stale
      const expl = (res as any).explainability;
      if (expl?.isStale) {
        finalAnswer = `⚠️ Data is ${Math.round(expl.dataFreshnessMinutes / 60)}h old. Consider refreshing.\n\n${finalAnswer}`;
      }
      if (expl?.confidenceScore && expl.confidenceScore < 50) {
        finalAnswer += `\n\n⚠️ Confidence: ${expl.confidenceScore}% — limited data available.`;
      }
      
      setMessages((prev) => [...prev, { role: "assistant", content: finalAnswer, timestamp: Date.now(), followUps }]);
    } catch {
      clearTimeout(timeoutId);
      const answer = buildFallbackAnswer(question, context, selectedEntity);
      const followUps = buildFollowUps(question, context, selectedEntity);
      setMessages((prev) => [...prev, { role: "assistant", content: answer, timestamp: Date.now(), followUps }]);
    } finally {
      setLoading(false);
    }
  }, [loading, context, selectedEntity]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  if (!isOpen) return null;

  const starters = buildSmartPrompts(context, selectedEntity);

  return (
    <div className="fixed top-0 right-0 h-full w-[400px] bg-[#161b22] border-l border-[#21262d] flex flex-col z-40 shadow-2xl">
      {/* Header with context label */}
      <div className="flex flex-col border-b border-[#21262d]">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="text-blue-400 text-lg">✦</span>
            <span className="text-sm font-semibold text-white">Planning Copilot</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition text-lg leading-none" aria-label="Close">×</button>
        </div>
        <div className="px-4 pb-2">
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-900/30 border border-blue-500/20 text-blue-400">
            {contextLabel(selectedEntity)}
          </span>
          {context.dataMode === "mock" && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-yellow-900/30 border border-yellow-500/20 text-yellow-400 ml-2">Mock Data</span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3">
        {messages.map((msg, i) => (
          <div key={i}>
            <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs whitespace-pre-wrap leading-relaxed ${
                msg.role === "user" ? "bg-blue-900/40 text-blue-100 border border-blue-500/30" : "bg-[#0d1117] text-gray-300 border border-[#21262d]"
              }`}>
                {msg.content}
              </div>
            </div>
            {/* Follow-up suggestions - one at a time */}
            {msg.role === "assistant" && msg.followUps && msg.followUps.length > 0 && (
              <div className="flex flex-col gap-1.5 mt-2 ml-1">
                {msg.followUps.slice(0, 1).map((fu, j) => (
                  <button key={j} onClick={() => sendMessage(fu)}
                    className="text-[10px] px-2 py-0.5 rounded-lg bg-gray-800 border border-gray-700 text-gray-400 hover:text-blue-400 hover:border-blue-500/30 transition text-left">
                    {fu}
                  </button>
                ))}
              </div>
            )}
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
            <button key={i} onClick={() => sendMessage(prompt)}
              className="text-xs px-2 py-1 rounded-lg bg-blue-900/20 border border-blue-500/30 text-blue-400 hover:bg-blue-900/40 transition">
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t border-[#21262d] flex gap-2 items-end">
        <textarea ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
          placeholder="Ask about the planning data…" rows={2}
          className="flex-1 bg-[#0d1117] border border-[#21262d] rounded-lg px-3 py-2 text-xs text-gray-200 placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500/50"
          disabled={loading} />
        <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()}
          className="px-3 py-2 rounded-lg bg-blue-900/30 border border-blue-500/30 text-blue-400 text-xs font-medium hover:bg-blue-900/50 transition disabled:opacity-40 disabled:cursor-not-allowed">
          Send
        </button>
      </div>
    </div>
  );
};
