"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { batchRunAgent, fetchBatchQueue, type BatchQueueItem, fetchTickets, runAgentWorkflow, streamAgentReply, chatWithAgent } from "@/lib/api";
import { getActiveAgentModel, getAgentModelSettingsUrl } from "@/lib/agentModel";
import type { AgentRunResult, TicketListItem, ToolCallData } from "@/lib/types";
import {
  CATEGORY_LABELS,
  PRIORITY_COLORS,
  PRIORITY_LABELS,
  STATUS_COLORS,
  STATUS_LABELS,
} from "@/lib/constants";

type ChatLine = {
  id: string;
  role: "user" | "assistant";
  content: string;
  ticketId?: number;
  phase?: string;
  modelName?: string;
  result?: AgentRunResult;
  results?: AgentRunResult[];
};

const welcomeMessage: ChatLine = {
  id: "welcome",
  role: "assistant",
  content: "你好，我是售后工单助手。可以直接向我提问，也可以选择右侧工单查看问题、整理回复或执行工单处理。模型跟随Agent控制台当前选择。",
  phase: "模型跟随Agent控制台",
};

function newId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function AgentPage() {
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [chatting, setChatting] = useState(false);
  const [modelLabel, setModelLabel] = useState("正在连接Agent控制台…");
  const [settingsUrl, setSettingsUrl] = useState("http://127.0.0.1:8020/?view=settings");
  useEffect(() => {
    let active = true;
    setSettingsUrl(getAgentModelSettingsUrl());
    const update = () => getActiveAgentModel().then((profile) => { if (active) setModelLabel(profile.name || profile.model); }).catch(() => { if (active) setModelLabel("模型未连接，请前往设置"); });
    update();
    window.addEventListener("focus", update);
    return () => { active = false; window.removeEventListener("focus", update); };
  }, []);

  const [results, setResults] = useState<AgentRunResult[]>([]);
  const [messages, setMessages] = useState<ChatLine[]>([welcomeMessage]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [batchQueue, setBatchQueue] = useState<BatchQueueItem[]>([]);
  const batchCount = batchQueue.filter(item=>item.eligible).length;
  const [batchRunning, setBatchRunning] = useState(false);
  const [streamingId, setStreamingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [data, queue] = await Promise.all([fetchTickets(),fetchBatchQueue()]);
      setBatchQueue(queue);
      setTickets(data.filter((ticket: TicketListItem) =>
        ["pending", "ai_processing", "waiting_user", "escalated"].includes(ticket.status)
      ));
    } catch {
      setError("加载工单队列失败，请确认后端服务已启动。");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTickets();
    const timer=setInterval(()=>{if(!document.hidden) void loadTickets();},15000);
    return ()=>clearInterval(timer);
  }, [loadTickets]);

  const append = (line: ChatLine) => setMessages((current) => [...current, line]);
  const updateLine = (id: string, update: (line: ChatLine) => ChatLine) => {
    setMessages((current) => current.map((line) => line.id === id ? update(line) : line));
  };

  const handleStreamTicket = async (ticket: TicketListItem, requestText: string) => {
    const assistantId = newId();
    setSelectedId(ticket.id);
    setError("");
    append({ id: newId(), role: "user", content: requestText });
    append({ id: assistantId, role: "assistant", content: "", ticketId: ticket.id, phase: "正在分析工单" });
    setStreamingId(ticket.id);
    let failed = "";

    await streamAgentReply(
      ticket.id,
      ({ event, data }) => {
        if (event === "analysis_start") {
          updateLine(assistantId, (line) => ({ ...line, phase: "正在分析工单内容" }));
        } else if (event === "analysis_done") {
          updateLine(assistantId, (line) => ({ ...line, phase: "分析完成，正在检索知识库" }));
        } else if (event === "kb_search_done") {
          updateLine(assistantId, (line) => ({ ...line, phase: "知识库检索完成，正在生成建议回复" }));
        } else if (event === "reply_chunk") {
          const chunk = (data as { content: string }).content;
          updateLine(assistantId, (line) => ({ ...line, content: line.content + chunk }));
        } else if (event === "done") {
          const doneData = data as { model_name?: string; reply: string; tool_calls: ToolCallData[]; kb_sources: string[]; need_human: boolean };
          const result: AgentRunResult = {
            ticket_id: ticket.id,
            model_name: doneData.model_name,
            status: doneData.need_human ? "escalated" : "waiting_user",
            action: doneData.need_human ? "escalated" : "replied",
            need_human: doneData.need_human,
            kb_hit: doneData.kb_sources.length > 0,
            kb_sources: doneData.kb_sources,
            summary_id: null,
            steps: ["分析工单", "知识库检索", "工具调用", "生成回复"],
            tool_calls: doneData.tool_calls,
          };
          updateLine(assistantId, (line) => ({ ...line, content: line.content || doneData.reply, phase: "处理完成", modelName: result.model_name, result }));
          setResults((current) => [result, ...current.filter((item) => item.ticket_id !== ticket.id)]);
        }
      },
      (streamError) => {
        failed = streamError.message;
        setError(streamError.message);
        updateLine(assistantId, (line) => ({ ...line, content: line.content || "这次没有成功完成工单处理。", phase: "处理失败" }));
      },
      () => undefined,
    );

    setStreamingId(null);
    if (failed) {
      updateLine(assistantId, (line) => ({ ...line, content: line.content || `处理失败：${failed}`, phase: "处理失败" }));
    } else {
      await loadTickets();
    }
  };

  const handleQuickRun = async (ticket: TicketListItem) => {
    const assistantId = newId();
    setSelectedId(ticket.id);
    setError("");
    append({ id: newId(), role: "user", content: `快速处理工单 #${ticket.id}：${ticket.title}` });
    append({ id: assistantId, role: "assistant", content: "正在执行工单分析与自动处理…", ticketId: ticket.id, phase: "正在处理" });
    setRunningId(ticket.id);
    try {
      const result = await runAgentWorkflow(ticket.id);
      setResults((current) => [result, ...current.filter((item) => item.ticket_id !== ticket.id)]);
      updateLine(assistantId, (line) => ({ ...line, content: `工单 #${ticket.id} 已完成自动处理。${result.need_human ? "该工单需要人工跟进。" : "处理结果已写入工单。"}`, phase: "处理完成", modelName: result.model_name, result }));
      await loadTickets();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Agent 运行失败";
      setError(message);
      updateLine(assistantId, (line) => ({ ...line, content: `处理失败：${message}`, phase: "处理失败" }));
    } finally {
      setRunningId(null);
    }
  };

  const handleBatchRun = async (requestText = "批量处理当前待处理工单") => {
    if (batchCount === 0) {
      append({ id: newId(), role: "user", content: requestText });
      append({ id: newId(), role: "assistant", content: "当前没有未回复且允许AI处理的买家问题。已回复的工单等待买家新消息，转人工的工单请人工接待。", phase: "队列为空" });
      return;
    }
    setBatchRunning(true);
    setError("");
    append({ id: newId(), role: "user", content: requestText });
    const assistantId = newId();
    append({ id: assistantId, role: "assistant", content: "正在批量处理待处理工单…", phase: "批量处理中" });
    try {
      const response = await batchRunAgent(5, (done,total,id,failure)=>{
        updateLine(assistantId,line=>({...line,content:`批量进度 ${done}/${total}，工单 #${id}${failure ? `：${failure}` : done < total ? "，正在处理…" : "，本张处理结束"}`,phase:`批量处理中 ${done}/${total}`}));
      });
      setResults((current) => [...response.results, ...current]);
      updateLine(assistantId, (line) => ({
        ...line,
        content: [response.processed ? `成功回复 ${response.processed} 张工单。` : "本次没有发送回复。",
          ...response.failures.map(item=>`工单 #${item.ticket_id} 未完成：${item.reason}`),
          response.skipped.length ? `已跳过 ${response.skipped.length} 张无需自动回复的工单：` : "",
          ...response.skipped.map(item=>`#${item.ticket_id}：${item.reason}`)].filter(Boolean).join("\n"),
        phase: response.failures.length ? "批量处理结束，部分未完成" : response.processed ? "批量处理完成" : "无需自动回复",
        results: response.results,
      }));
      await loadTickets();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "批量运行失败";
      setError(message);
      updateLine(assistantId, (line) => ({ ...line, content: `批量处理失败：${message}`, phase: "处理失败" }));
    } finally {
      setBatchRunning(false);
    }
  };

  const handleSend = async () => {
    const requestText = draft.trim();
    if (!requestText || chatting || batchRunning || runningId !== null || streamingId !== null) return;
    setDraft("");

    if (/批量.*处理|处理.*全部|处理.*所有待处理/.test(requestText)) {
      await handleBatchRun(requestText);
      return;
    }

    const idMatch = requestText.match(/#\s*(\d+)|工单\s*#?\s*(\d+)/i);
    const explicitId = idMatch ? Number(idMatch[1] || idMatch[2]) : null;
    const titleMatch = tickets.find((ticket) => requestText.includes(ticket.title));
    const ticket = explicitId ? tickets.find((item) => item.id === explicitId)
      : titleMatch || tickets.find((item) => item.id === selectedId);

    if (!ticket || !/(?:处理|回复|运行|执行)(?:这张|当前|该|这条|工单|\s*#)/.test(requestText)) {
      append({ id: newId(), role: "user", content: requestText });
      const assistantId = newId();
      append({ id: assistantId, role: "assistant", content: "", phase: "正在调用Agent当前模型" });
      setChatting(true);
      try {
        const profile = await getActiveAgentModel();
        setModelLabel(profile.name || profile.model);
        const reply = await chatWithAgent(requestText, messages.filter((m) => m.id !== "welcome").map((m) => ({role: m.role, content: m.content})), ticket?.id);
        updateLine(assistantId, (line) => ({...line, content: reply, phase: "回答完成", modelName: profile.name || profile.model}));
      } catch (error) {
        updateLine(assistantId, (line) => ({...line, content: error instanceof Error ? error.message : "模型连接失败，请前往设置", phase: "回答失败"}));
      } finally { setChatting(false); }
      return;
    }
    await handleStreamTicket(ticket, requestText);
  };

  const busy = chatting || batchRunning || runningId !== null || streamingId !== null;
  const selectedTicket = tickets.find((ticket) => ticket.id === selectedId);

  return (
    <div className="flex h-[calc(100dvh-104px)] min-h-[590px] flex-col p-3 sm:p-5">
      <div className="mb-4 flex shrink-0 items-center justify-between gap-3">
        <div>
          <p className="text-xs text-slate-400">客服工作台　/　智能客服</p>
          <h1 className="mt-1 text-xl font-semibold text-slate-800 sm:text-[22px]">智能客服助手</h1>
        </div>
        <button onClick={() => handleBatchRun()} disabled={busy || loading || batchCount === 0} className="shrink-0 rounded-md bg-blue-600 px-3 py-2 text-xs font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:px-4 sm:text-sm">
          {batchRunning ? "批量处理中…" : batchCount ? `批量处理 ${Math.min(5, batchCount)} 张工单` : "暂无待回复工单"}
        </button>
      </div>

      {error && <div role="alert" className="mb-3 shrink-0 rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-700">{error}</div>}

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_310px]">
        <section className="flex min-h-[510px] min-w-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex h-[58px] shrink-0 items-center justify-between border-b border-slate-100 px-4 sm:px-5">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-500 text-[11px] font-bold text-white">AI</span>
              <div><h2 className="text-sm font-semibold text-slate-800">客服工单处理 Agent</h2><p className="mt-0.5 text-[11px] text-slate-400">Agent当前模型 · 真实工单 · 知识库检索</p></div>
            </div>
            <div className="hidden items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-[11px] text-emerald-700 sm:flex"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />{modelLabel}</div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto bg-[#fafbfd] px-3 py-4 sm:px-5 sm:py-5">
            {messages.map((message) => message.role === "user" ? (
              <div key={message.id} className="flex justify-end">
                <div className="max-w-[85%] rounded-xl rounded-br-sm border border-blue-100 bg-[#edf5ff] px-4 py-3 text-sm leading-6 text-slate-700 shadow-[0_1px_2px_rgba(15,23,42,.03)] sm:max-w-[76%]">{message.content}</div>
              </div>
            ) : (
              <div key={message.id} className="flex items-start gap-2.5 sm:gap-3">
                <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-[10px] font-bold text-white">AI</span>
                <article className="min-w-0 max-w-[96%] flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3.5 shadow-[0_1px_2px_rgba(15,23,42,.03)] sm:max-w-[92%] sm:px-5">
                  <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-medium text-slate-500">助手</span>
                    {message.phase && <span className={`rounded-full px-2 py-0.5 text-[11px] ${message.phase.includes("失败") ? "bg-red-50 text-red-600" : message.phase.includes("完成") ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>{message.phase}</span>}
                  </div>
                  {message.content ? <p className="whitespace-pre-wrap break-words text-[14px] leading-7 text-slate-700">{message.content}</p> : <span className="inline-block h-4 w-1.5 animate-pulse rounded bg-blue-500 align-middle" />}
                  {message.modelName && <p className="mt-2 text-xs text-slate-400">Agent 模型：{message.modelName}</p>}
                  {(message.result || (message.results && message.results.length > 0)) && (
                    <div className="mt-4 border-t border-slate-100 pt-3">
                      {message.result && <ResultDetails result={message.result} />}
                      {message.results && <div className="space-y-2">{message.results.map((result, index) => <ResultRow key={`${result.ticket_id}-${index}`} result={result} />)}</div>}
                      <p className="mt-3 text-[11px] text-slate-400">Agent 模型：{message.modelName || modelLabel}</p>
                    </div>
                  )}
                </article>
              </div>
            ))}
            {loading && tickets.length === 0 && <p className="py-6 text-center text-xs text-slate-400">正在加载工单队列…</p>}
          </div>

          <div className="shrink-0 border-t border-slate-200 bg-white p-3 sm:p-4">
            {selectedTicket && <div className="mb-2 flex items-center gap-2 text-xs text-slate-500"><span className="text-slate-400">当前工单</span><span className="max-w-[55vw] truncate rounded bg-slate-100 px-2 py-1">#{selectedTicket.id} · {selectedTicket.title}</span><button onClick={() => setSelectedId(null)} className="text-slate-400 hover:text-slate-700" aria-label="取消选择">×</button></div>}
            <div className="rounded-lg border border-slate-200 bg-white shadow-[0_1px_4px_rgba(15,23,42,.05)] focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
              <textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void handleSend(); } }} placeholder="直接提问，或选择工单后输入“处理这张工单”…" rows={2} className="max-h-36 min-h-[68px] w-full resize-y border-0 bg-transparent px-3 py-3 text-sm leading-6 text-slate-700 outline-none placeholder:text-slate-400 sm:px-4" />
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 px-3 py-2 sm:px-4">
                <a href={settingsUrl} target="_blank" rel="noreferrer" className="rounded border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50">⚙ 前往设置模型 ↗</a>
                <span className="text-[11px] text-slate-400">Enter 发送 · Shift + Enter 换行{selectedTicket ? ` · 已选择工单 #${selectedTicket.id}` : ""}</span>
                <div className="flex items-center gap-2">
                  <button onClick={() => setDraft("")} className="rounded-md border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50">清空</button>
                  <button onClick={() => void handleSend()} disabled={!draft.trim() || busy} className="rounded-md bg-blue-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-45">{busy ? "处理中…" : "发送"}</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside className="flex min-h-[350px] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex shrink-0 items-center justify-between border-b border-slate-100 px-4 py-3.5">
            <div><h2 className="text-sm font-semibold text-slate-800">未结工单</h2><p className="mt-1 text-[11px] text-slate-400">可自动回复 {batchCount} 张；其他工单可查看详情</p></div>
            <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">{tickets.length}</span>
          </div>
          <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
            {loading && <p className="py-8 text-center text-xs text-slate-400">加载中…</p>}
            {!loading && tickets.length === 0 && <p className="py-8 text-center text-xs text-slate-400">当前没有需要 Agent 处理的工单</p>}
            {tickets.map((ticket) => (
              <button key={ticket.id} onClick={() => setSelectedId(ticket.id)} className={`block w-full rounded-lg border px-3 py-3 text-left transition ${selectedId === ticket.id ? "border-blue-300 bg-blue-50/70 ring-1 ring-blue-100" : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"}`}>
                <div className="mb-1.5 flex items-center justify-between gap-2"><span className="font-mono text-[11px] text-slate-400">TKT-{String(ticket.id).padStart(3, "0")}</span><span className={`rounded-full px-2 py-0.5 text-[10px] ${PRIORITY_COLORS[ticket.priority] || "bg-slate-100 text-slate-500"}`}>{PRIORITY_LABELS[ticket.priority] || ticket.priority}</span></div>
                <p className="line-clamp-2 text-[13px] font-medium leading-5 text-slate-700">{ticket.title}</p><p className="mt-1 text-[11px] text-slate-500">{batchQueue.find(item=>item.ticket_id===ticket.id)?.reason || "买家问题待回复"}</p>
                <div className="mt-2 flex items-center justify-between gap-2 text-[11px] text-slate-400"><span className="truncate">{ticket.customer_name} · {CATEGORY_LABELS[ticket.category] || ticket.category}</span><span className={`shrink-0 rounded-full px-1.5 py-0.5 ${STATUS_COLORS[ticket.status] || "bg-slate-100 text-slate-500"}`}>{STATUS_LABELS[ticket.status] || ticket.status}</span></div>
              </button>
            ))}
          </div>
          {selectedTicket && <div className="shrink-0 border-t border-slate-100 p-3">
            <div className="mb-2 truncate text-xs text-slate-500">已选择：{selectedTicket.title}</div>
            <div className="flex gap-2">
              <button onClick={() => void handleQuickRun(selectedTicket)} disabled={busy || !batchQueue.some(item=>item.ticket_id===selectedTicket.id && item.eligible)} className="flex-1 rounded-md border border-slate-200 px-2 py-2 text-xs text-slate-600 hover:bg-slate-50 disabled:opacity-50">快速处理</button>
              <Link href={`/tickets/${selectedTicket.id}`} className="flex-1 rounded-md bg-[#30465c] px-2 py-2 text-center text-xs text-white hover:bg-[#263b50]">查看工单</Link>
            </div>
          </div>}
          <div className="shrink-0 border-t border-slate-100 px-4 py-3">
            <div className="mb-2 flex items-center justify-between"><h3 className="text-xs font-semibold text-slate-600">最近运行</h3><span className="text-[10px] text-slate-400">{results.length} 条</span></div>
            {results.length === 0 ? <p className="text-[11px] text-slate-400">暂无运行记录</p> : <div className="space-y-1.5">{results.slice(0, 3).map((result, index) => <ResultRow key={`${result.ticket_id}-${index}`} result={result} compact />)}</div>}
          </div>
        </aside>
      </div>
    </div>
  );
}

function ResultDetails({ result }: { result: AgentRunResult }) {
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded bg-slate-100 px-2 py-1 font-mono text-slate-600">工单 #{result.ticket_id}</span>
        <span className={`rounded-full px-2 py-1 ${STATUS_COLORS[result.status] || "bg-slate-100 text-slate-600"}`}>{STATUS_LABELS[result.status] || result.status}</span>
        {result.need_human && <span className="rounded-full bg-amber-50 px-2 py-1 text-amber-700">需要人工跟进</span>}
      </div>
      <p className="mt-2 text-xs text-slate-600">{result.kb_hit ? `知识库引用：${result.kb_sources.join("、")}` : "未命中知识库内容"}</p>
      <div className="mt-2 flex flex-wrap gap-1.5">{result.steps.map((step) => <span key={step} className="rounded bg-slate-100 px-2 py-1 text-[10px] text-slate-500">{step}</span>)}</div>
      {result.tool_calls?.length > 0 && <p className="mt-2 text-[11px] text-slate-500">已调用：{result.tool_calls.map((call) => call.tool).join("、")}</p>}
      <Link href={`/tickets/${result.ticket_id}`} className="mt-3 inline-flex text-xs font-medium text-blue-600 hover:text-blue-700">查看工单详情 →</Link>
    </div>
  );
}

function ResultRow({ result, compact = false }: { result: AgentRunResult; compact?: boolean }) {
  return (
    <div className={`flex items-center justify-between gap-2 rounded-md ${compact ? "bg-slate-50 px-2.5 py-2" : "border border-slate-100 px-3 py-2.5"}`}>
      <Link href={`/tickets/${result.ticket_id}`} className="truncate text-xs font-medium text-slate-700 hover:text-blue-600">工单 #{result.ticket_id} · {result.action === "escalated" ? "已转人工" : "已生成回复"}</Link>
      <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] ${STATUS_COLORS[result.status] || "bg-slate-100 text-slate-500"}`}>{STATUS_LABELS[result.status] || result.status}</span>
    </div>
  );
}
