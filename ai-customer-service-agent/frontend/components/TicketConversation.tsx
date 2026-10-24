"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import AfterSalePanel from "@/components/AfterSalePanel";
import HumanHandoffPanel from "@/components/HumanHandoffPanel";
import { fetchTicket, updateTicketStatus, addMessage, analyzeTicket, autoReply, generateSummary, fetchTicketSummary, runAgentWorkflow, streamAgentReply } from "@/lib/api";
import type { AgentRunResult, MessageItem, TicketDetail, TicketSummary, ToolCallData } from "@/lib/types";
import { STATUS_LABELS, STATUS_COLORS, PRIORITY_LABELS, PRIORITY_COLORS, CATEGORY_LABELS, SENTIMENT_LABELS, SENTIMENT_COLORS } from "@/lib/constants";
import styles from "./TicketConversation.module.css";

const STATUS_FLOW: Record<string, string[]> = {
  pending: ["ai_processing", "escalated", "resolved"],
  ai_processing: ["waiting_user", "escalated", "resolved"],
  waiting_user: ["ai_processing", "escalated", "resolved"],
  resolved: [],
  escalated: ["pending", "ai_processing", "resolved"],
};

function timeLabel(value: string) {
  const date = new Date(value + (/Z$|[+-]\d\d:\d\d$/.test(value) ? "" : "Z"));
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN", { hour12: false });
}

export default function TicketConversation({ ticketId }: { ticketId: number }) {
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [autoReplying, setAutoReplying] = useState(false);
  const [summary, setSummary] = useState<TicketSummary | null>(null);
  const [summarizing, setSummarizing] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);
  const [statusChanging, setStatusChanging] = useState(false);
  const [agentResult, setAgentResult] = useState<AgentRunResult | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [streamState, setStreamState] = useState<"idle" | "analyzing" | "searching" | "replying" | "done">("idle");
  const [streamedReply, setStreamedReply] = useState("");
  const [streamToolCalls, setStreamToolCalls] = useState<ToolCallData[]>([]);
  const [streamKbSources, setStreamKbSources] = useState<string[]>([]);
  const [streamError, setStreamError] = useState("");
  const [expandedTools, setExpandedTools] = useState<Set<number>>(new Set());
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [detailTab, setDetailTab] = useState<"ticket" | "analysis" | "activity">("ticket");
  const [pinned, setPinned] = useState(true);
  const [unseenCount, setUnseenCount] = useState(0);

  const alive = useRef(true);
  const requestVersion = useRef(0);
  const mutating = useRef(false);
  const scrollArea = useRef<HTMLDivElement>(null);
  const messageContent = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLFormElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const nearBottom = useRef(true);
  const forceBottom = useRef(false);
  const seenIds = useRef<Set<number> | null>(null);
  const busy = sending || analyzing || autoReplying || summarizing || agentRunning || streaming || statusChanging;

  const applyTicket = useCallback((updated: TicketDetail) => {
    if (!alive.current || updated.id !== ticketId) return;
    requestVersion.current += 1;
    setTicket(updated);
  }, [ticketId]);

  // Refresh the data in place; the conversation and composer remain mounted.
  const loadTicket = useCallback(async (quiet = false) => {
    const version = ++requestVersion.current;
    if (!quiet) setRefreshing(true);
    try {
      const data: TicketDetail = await fetchTicket(ticketId);
      if (!alive.current || version !== requestVersion.current) return;
      setTicket(data);
      setLoadError("");
    } catch (error) {
      if (alive.current && version === requestVersion.current) {
        setLoadError(error instanceof Error ? error.message : "会话同步失败，请重试");
      }
    } finally {
      if (alive.current && version === requestVersion.current) {
        setLoading(false);
      }
      if (alive.current && !quiet) setRefreshing(false);
    }
  }, [ticketId]);

  useEffect(() => {
    alive.current = true;
    void loadTicket();
    let summaryActive = true;
    fetchTicketSummary(ticketId).then(value => { if (summaryActive) setSummary(value); }).catch(() => {});
    const refresh = () => { if (!document.hidden && !mutating.current) void loadTicket(true); };
    const timer = setInterval(refresh, 5000);
    window.addEventListener("focus", refresh);
    return () => {
      alive.current = false;
      summaryActive = false;
      requestVersion.current += 1;
      clearInterval(timer);
      window.removeEventListener("focus", refresh);
    };
  }, [ticketId, loadTicket]);

  const scrollToLatest = useCallback(() => {
    const area = scrollArea.current;
    if (!area) return;
    area.scrollTop = area.scrollHeight;
    nearBottom.current = true;
    setPinned(true);
    setUnseenCount(0);
  }, []);

  useLayoutEffect(() => {
    if (!ticket || !scrollArea.current) return;
    const ids = new Set(ticket.messages.map(message => message.id));
    const previous = seenIds.current;
    const added = previous ? ticket.messages.filter(message => !previous.has(message.id)).length : 0;
    if (!previous || forceBottom.current || nearBottom.current) {
      scrollToLatest();
    } else if (added) {
      setUnseenCount(count => count + added);
    }
    forceBottom.current = false;
    seenIds.current = ids;
  }, [ticket?.messages, scrollToLatest, ticket]);

  useEffect(() => {
    const content = messageContent.current;
    if (!content) return;
    const observer = new ResizeObserver(() => {
      if (nearBottom.current && scrollArea.current) scrollArea.current.scrollTop = scrollArea.current.scrollHeight;
    });
    observer.observe(content);
    if (scrollArea.current) observer.observe(scrollArea.current);
    return () => observer.disconnect();
  }, [!!ticket]);

  function trackScroll() {
    const area = scrollArea.current;
    if (!area) return;
    const atBottom = area.scrollHeight - area.scrollTop - area.clientHeight < 64;
    nearBottom.current = atBottom;
    setPinned(atBottom);
    if (atBottom) setUnseenCount(0);
  }

  function beginAction() {
    if (mutating.current) return false;
    mutating.current = true;
    requestVersion.current += 1; // Older polling responses must not overwrite a new reply.
    setActionError("");
    return true;
  }

  const handleSendReply = async () => {
    const content = replyText.trim();
    if (!content || ticket?.ecommerce?.conversation_closed || !beginAction()) return;
    setSending(true);
    try {
      const sent: MessageItem = await addMessage(ticketId, { role: "agent", content });
      if (!alive.current) return;
      forceBottom.current = true;
      nearBottom.current = true;
      setTicket(current => current ? { ...current, messages: current.messages.some(message => message.id === sent.id) ? current.messages : [...current.messages, sent] } : current);
      setReplyText(current => current.trim() === content ? "" : current);
      await loadTicket(true);
      if (composer.current?.contains(document.activeElement)) input.current?.focus({ preventScroll: true });
    } catch (error) {
      if (alive.current) setActionError(error instanceof Error ? error.message : "发送失败，请重试");
    } finally {
      mutating.current = false;
      if (alive.current) setSending(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!beginAction()) return;
    setStatusChanging(true);
    try { applyTicket(await updateTicketStatus(ticketId, newStatus)); }
    catch (error) { if (alive.current) setActionError(error instanceof Error ? error.message : "状态更新失败"); }
    finally { mutating.current = false; if (alive.current) setStatusChanging(false); }
  };

  const handleAnalyze = async () => {
    if (!beginAction()) return;
    setAnalyzing(true);
    try { applyTicket(await analyzeTicket(ticketId)); }
    catch (error) { if (alive.current) setActionError(error instanceof Error ? error.message : "分析失败，请重试"); }
    finally { mutating.current = false; if (alive.current) setAnalyzing(false); }
  };

  const handleGenerateSummary = async () => {
    if (!beginAction()) return;
    setSummarizing(true);
    try { const value = await generateSummary(ticketId); if (alive.current) setSummary(value); }
    catch (error) { if (alive.current) setActionError(error instanceof Error ? error.message : "生成总结失败"); }
    finally { mutating.current = false; if (alive.current) setSummarizing(false); }
  };

  const handleAutoReply = async () => {
    if (!beginAction()) return;
    setAutoReplying(true);
    try {
      const updated = await autoReply(ticketId);
      if (alive.current) { forceBottom.current = true; applyTicket(updated); }
    } catch (error) { if (alive.current) setActionError(error instanceof Error ? error.message : "自动回复失败"); }
    finally { mutating.current = false; if (alive.current) setAutoReplying(false); }
  };

  const handleRunAgent = async () => {
    if (!beginAction()) return;
    setAgentRunning(true);
    try {
      const result = await runAgentWorkflow(ticketId);
      if (!alive.current) return;
      forceBottom.current = true;
      setAgentResult(result);
      await loadTicket(true);
      const value = await fetchTicketSummary(ticketId);
      if (alive.current) setSummary(value);
    } catch (error) { if (alive.current) setActionError(error instanceof Error ? error.message : "Agent 处理失败"); }
    finally { mutating.current = false; if (alive.current) setAgentRunning(false); }
  };

  const handleStreamReply = async () => {
    if (!beginAction()) return;
    setStreaming(true); setStreamState("analyzing"); setStreamedReply("");
    setStreamToolCalls([]); setStreamKbSources([]); setExpandedTools(new Set()); setStreamError("");
    await streamAgentReply(ticketId, ({event,data}) => {
      if (!alive.current) return;
      if (event === "analysis_start") setStreamState("analyzing");
      if (event === "analysis_done") setStreamState("searching");
      if (event === "kb_search_done") { setStreamKbSources((data as {sources:string[]}).sources || []); setStreamState("replying"); }
      if (event === "reply_chunk") setStreamedReply(value => value + (data as {content:string}).content);
      if (event === "tool_call") setStreamToolCalls(value => [...value,data as ToolCallData]);
      if (event === "done") { setStreamState("done"); forceBottom.current = true; }
    }, error => {
      if (alive.current) { setStreamState("done"); setStreamError(error.message); setActionError(error.message); }
    }, () => {});
    if (alive.current) { await loadTicket(true); setStreaming(false); }
    mutating.current = false;
  };

  if (loading && !ticket) return <div className={styles.empty}>正在加载会话…</div>;
  if (!ticket) return <div className={styles.empty}><p role="alert">{loadError || "工单不存在"}</p><button onClick={() => void loadTicket()}>重新加载</button><Link href="/tickets">返回工单列表</Link></div>;

  const closed = !!ticket.ecommerce?.conversation_closed;
  const human = ["human", "human_requested"].includes(ticket.ecommerce?.handling_mode || "") || ticket.need_human;
  const canAutoReply = !closed && !human && ticket.status !== "resolved" && ticket.status !== "escalated" && [...ticket.messages].reverse().find(message => message.role !== "system")?.role === "user";
  const availableStatuses = (STATUS_FLOW[ticket.status] || []).filter(status => !ticket.ecommerce || ticket.ecommerce.record_type === "consultation" || status !== "resolved");
  const hasAnalysis = ticket.analysis_status === "completed";

  return <div className={styles.workspace}>
    <header className={styles.workspaceHeader}>
      <div className={styles.heading}><Link href="/tickets" className={styles.back} aria-label="返回工单列表">‹</Link><div><h1>#{ticket.id} {ticket.title}</h1><p>客服工作台 / 工单会话</p></div></div>
      <div className={styles.headerActions}><span className={`${styles.badge} ${STATUS_COLORS[ticket.status]}`}>{STATUS_LABELS[ticket.status] || ticket.status}</span><button type="button" disabled={busy || refreshing} onClick={() => void loadTicket()}>{refreshing ? "同步中…" : "刷新"}</button><button type="button" className={styles.detailsTrigger} onClick={() => setDetailsOpen(value => !value)} aria-expanded={detailsOpen} aria-controls="ticket-details">{detailsOpen ? "收起资料" : "工单资料"}</button></div>
    </header>
    <div className={styles.layout}>
      <section className={styles.chat} aria-label="客服聊天">
        <header className={styles.chatHeader}><div className={styles.customerAvatar}>{ticket.customer_name.slice(0, 1) || "客"}</div><div><h2>{ticket.customer_name}</h2><p>{closed ? "会话已结束 · 可查看完整记录" : ticket.ecommerce?.handling_mode === "human_requested" ? "等待人工接待" : ticket.ecommerce?.handling_mode === "human" ? "人工客服接待中" : "客服会话"} · {ticket.messages.length} 条消息</p></div><span className={`${styles.badge} ${PRIORITY_COLORS[ticket.priority]}`}>{PRIORITY_LABELS[ticket.priority] || ticket.priority}</span></header>
        <HumanHandoffPanel ticket={ticket} onChange={applyTicket} compact />
        {loadError && <div role="status" className={styles.syncError}>消息同步暂时失败，当前会话已保留。<button type="button" disabled={busy} onClick={() => void loadTicket()}>重试</button></div>}
        <div className={styles.messagesWrap}>
          <div ref={scrollArea} className={styles.messages} onScroll={trackScroll} role="log" aria-label="聊天记录" aria-live="polite" aria-relevant="additions text" tabIndex={0}>
            <div ref={messageContent} className={styles.messageContent}>
              <p className={styles.historyStart}>工单 #{ticket.id} · 会话开始于 {timeLabel(ticket.created_at)}</p>
              {ticket.messages.map(message => message.role === "system" ? <article key={message.id} className={styles.systemMessage}><time dateTime={message.created_at}>{timeLabel(message.created_at)}</time><p>{message.content}</p></article> : <article key={message.id} className={`${styles.message} ${message.role === "agent" ? styles.outgoing : ""}`}>
                <div aria-hidden="true" className={styles.messageAvatar}>{message.role === "agent" ? "服" : ticket.customer_name.slice(0, 1) || "客"}</div>
                <div className={styles.messageBody}><div className={styles.sender}>{message.role === "agent" ? "客服" : ticket.customer_name}<time dateTime={message.created_at}>{timeLabel(message.created_at)}</time></div><div className={styles.bubble}><p>{message.content}</p></div>
                  {message.role === "agent" && message.delivery_status && <p className={`${styles.delivery} ${message.delivery_status !== "sent" ? styles.deliveryPending : ""}`}>{message.delivery_status === "sent" ? "已送达买家" : message.delivery_status === "cancelled" ? "本条回复已取消发送" : "待送达 · 系统会自动重试"}</p>}
                  {message.delivery_error && <p className={styles.deliveryPending}>{message.delivery_error}</p>}
                </div>
              </article>)}
              {!ticket.messages.length && <div className={styles.noMessages}>暂无消息，可以在下方开始回复。</div>}
            </div>
          </div>
          {!pinned && <button type="button" className={styles.latest} onClick={scrollToLatest}>{unseenCount ? `${unseenCount} 条新消息 · ` : ""}回到最新 ↓</button>}
        </div>
        {closed ? <div className={styles.closed}>会话已结束，聊天记录已保留。</div> : <form ref={composer} className={styles.composer} onSubmit={event => { event.preventDefault(); void handleSendReply(); }}>
          <div className={styles.composerToolbar}><strong>人工回复</strong><button type="button" onClick={() => void handleAutoReply()} disabled={busy || !canAutoReply} title={human ? "当前为人工接待，自动回复已停止" : !canAutoReply ? "等待买家新问题后可使用" : "使用 Agent 当前模型生成并发送回复"}>{autoReplying ? "AI 回复中…" : "AI 自动回复"}</button></div>
          <textarea ref={input} aria-label="人工回复内容" value={replyText} onChange={event => setReplyText(event.target.value)} onKeyDown={event => {
            if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) { event.preventDefault(); void handleSendReply(); }
          }} placeholder="输入回复，Enter 发送，Shift + Enter 换行" rows={3} maxLength={20000} />
          {actionError && <div role="alert" className={styles.actionError}>{actionError}<button type="button" onClick={() => setActionError("")} aria-label="关闭错误提示">×</button></div>}
          <div className={styles.composerFooter}><span>Enter 发送 · Shift + Enter 换行</span><div><button type="button" onClick={() => setReplyText("")} disabled={!replyText}>清空</button><button type="submit" disabled={busy || !replyText.trim()} className={styles.send}>{sending ? "发送中…" : "发送回复"}</button></div></div>
        </form>}
        {closed && actionError && <p role="alert" className={styles.actionError}>{actionError}</p>}
      </section>
      <aside id="ticket-details" aria-label="工单资料" className={`${styles.sidebar} ${detailsOpen ? styles.sidebarOpen : ""}`}>
        <header className={styles.sidebarHeading}><h2>工单资料</h2><button type="button" className={styles.detailsTrigger} onClick={() => setDetailsOpen(false)} aria-label="收起工单资料">×</button></header>
        <nav className={styles.detailTabs} aria-label="工单资料分类">{([["ticket", "工单信息"], ["analysis", "AI 分析"], ["activity", "处理记录"]] as const).map(([key, label]) => <button type="button" key={key} aria-pressed={detailTab === key} className={detailTab === key ? styles.tabActive : ""} onClick={() => setDetailTab(key)}>{label}</button>)}</nav>
        <div className={styles.sidebarContent}>
          <div hidden={detailTab !== "ticket"}>
            <section className={styles.infoCard}><h3>基本信息</h3><dl><div><dt>工单编号</dt><dd>#{ticket.id}</dd></div><div><dt>客户</dt><dd>{ticket.customer_name}</dd></div>{ticket.customer_email && <div><dt>邮箱</dt><dd>{ticket.customer_email}</dd></div>}<div><dt>问题分类</dt><dd>{CATEGORY_LABELS[ticket.category] || ticket.category}</dd></div><div><dt>创建时间</dt><dd>{timeLabel(ticket.created_at)}</dd></div><div><dt>更新时间</dt><dd>{timeLabel(ticket.updated_at)}</dd></div></dl>{availableStatuses.length > 0 && <div className={styles.statusActions}><p>变更状态</p>{availableStatuses.map(status => <button type="button" key={status} disabled={busy} onClick={() => void handleStatusChange(status)}>{STATUS_LABELS[status]}</button>)}</div>}</section>
            <AfterSalePanel ticket={ticket} onChange={applyTicket} />
          </div>
          <div hidden={detailTab !== "analysis"}>
                  {/* AI Analysis Panel */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-900">AI 分析结果</h2>
          <button
            onClick={handleAnalyze}
            disabled={busy}
            className="px-3 py-1 text-xs text-blue-600 border border-blue-200 rounded-full hover:bg-blue-50 disabled:opacity-50"
          >
            {analyzing ? "分析中..." : "重新分析"}
          </button>
        </div>

        {hasAnalysis ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-xs text-gray-400">情绪</span>
                <div>
                  <span
                    className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${
                      SENTIMENT_COLORS[ticket.sentiment || ""] || "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {SENTIMENT_LABELS[ticket.sentiment || ""] || ticket.sentiment || "-"}
                  </span>
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">AI 分类</span>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {CATEGORY_LABELS[ticket.ai_category || ""] || ticket.ai_category || "-"}
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">AI 优先级</span>
                <div>
                  <span
                    className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${
                      PRIORITY_COLORS[ticket.ai_priority || ""] || ""
                    }`}
                  >
                    {PRIORITY_LABELS[ticket.ai_priority || ""] || ticket.ai_priority || "-"}
                  </span>
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">人工介入</span>
                <div>
                  <span
                    className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${
                      ticket.need_human
                        ? "bg-red-100 text-red-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {ticket.need_human ? "需要" : "不需要"}
                  </span>
                </div>
              </div>
            </div>
            {ticket.analysis_reason && (
              <div className="pt-3 border-t border-gray-100">
                <span className="text-xs text-gray-400">分析理由</span>
                <p className="mt-1 text-sm text-gray-700">{ticket.analysis_reason}</p>
              </div>
            )}
            <div className="text-xs text-gray-400">
              分析时间:{" "}
              {ticket.analyzed_at
                ? new Date(ticket.analyzed_at).toLocaleString("zh-CN")
                : "-"}
            </div>
          </div>
        ) : (
          <div className="text-center py-6">
            <p className="text-sm text-gray-400">
              {ticket.analysis_status === "failed"
                ? "分析失败，请点击重新分析"
                : "尚未分析，可点击“重新分析”读取当前工单。"}
            </p>
          </div>
        )}
      </div>


          </div>
          <div hidden={detailTab !== "activity"}>
                  {/* Ticket Summary Panel */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-900">工单总结</h2>
          <button
            onClick={handleGenerateSummary}
            disabled={busy}
            className="px-3 py-1 text-xs text-indigo-600 border border-indigo-200 rounded-full hover:bg-indigo-50 disabled:opacity-50"
          >
            {summarizing ? "生成中..." : summary ? "重新生成总结" : "生成总结"}
          </button>
        </div>

        {summary ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-xs text-gray-400">问题类型</span>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {CATEGORY_LABELS[summary.category] || summary.category}
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">用户情绪</span>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {SENTIMENT_LABELS[summary.sentiment] || summary.sentiment}
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">知识库</span>
                <div className="mt-1">
                  <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${
                    summary.knowledge_used
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}>
                    {summary.knowledge_used ? "已使用" : "未使用"}
                  </span>
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-400">人工介入</span>
                <div className="mt-1">
                  <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${
                    summary.need_human
                      ? "bg-red-100 text-red-700"
                      : "bg-gray-100 text-gray-600"
                  }`}>
                    {summary.need_human ? "需要" : "不需要"}
                  </span>
                </div>
              </div>
            </div>
            {summary.escalation_reason && (
              <div>
                <span className="text-xs text-gray-400">升级原因</span>
                <p className="mt-1 text-sm text-gray-700">{summary.escalation_reason}</p>
              </div>
            )}
            <div className="pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400">完整总结</span>
              <pre className="mt-1 text-sm text-gray-700 whitespace-pre-wrap font-sans bg-gray-50 rounded-lg p-3">
                {summary.summary_text}
              </pre>
            </div>
            <div className="text-xs text-gray-400">
              生成时间: {new Date(summary.created_at).toLocaleString("zh-CN")}
            </div>
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-sm text-gray-400">尚未生成总结，点击上方按钮生成</p>
          </div>
        )}
      </div>


                  {/* Agent Workflow Panel */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-900">Agent 工作流</h2>
          <div className="flex gap-2">
            <button
              onClick={handleStreamReply}
              disabled={busy || !canAutoReply}
              className="px-3 py-1 text-xs bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50"
            >
              {streaming ? "处理中..." : "流式处理"}
            </button>
            <button
              onClick={handleRunAgent}
              disabled={busy || !canAutoReply}
              className="px-3 py-1 text-xs text-gray-900 border border-gray-300 rounded-full hover:bg-gray-50 disabled:opacity-50"
            >
              {agentRunning ? "运行中..." : "快速流程"}
            </button>
          </div>
        </div>

        {/* Streaming progress */}
        {(streaming || streamState !== "idle") && (
          <div className="space-y-3">
            {/* Step indicator */}
            <div className="flex items-center gap-3">
              {["analyzing", "searching", "replying"].map((step, i) => {
                const stepLabels = ["分析中", "检索中", "回复中"];
                const isActive = streamState === step;
                const isDone =
                  (step === "analyzing" && ["searching", "replying", "done"].includes(streamState)) ||
                  (step === "searching" && ["replying", "done"].includes(streamState)) ||
                  (step === "replying" && streamState === "done");
                return (
                  <div key={step} className="flex items-center gap-1">
                    <span
                      className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold ${
                        isDone
                          ? "bg-green-100 text-green-700"
                          : isActive
                          ? "bg-blue-100 text-blue-700 animate-pulse"
                          : "bg-gray-100 text-gray-400"
                      }`}
                    >
                      {isDone ? "✓" : i + 1}
                    </span>
                    <span className={`text-xs ${isDone ? "text-green-600" : isActive ? "text-blue-600" : "text-gray-400"}`}>
                      {stepLabels[i]}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Tool call cards */}
            {streamToolCalls.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs text-gray-400 font-medium">工具调用</span>
                {streamToolCalls.map((tc, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => {
                        const next = new Set(expandedTools);
                        expandedTools.has(idx) ? next.delete(idx) : next.add(idx);
                        setExpandedTools(next);
                      }}
                      className="w-full flex items-center justify-between px-3 py-2 text-xs bg-gray-50 hover:bg-gray-100"
                    >
                      <span className="font-medium text-gray-700">
                        🔧 {tc.tool}
                      </span>
                      <span className="text-gray-400">{expandedTools.has(idx) ? "▲" : "▼"}</span>
                    </button>
                    {expandedTools.has(idx) && (
                      <div className="px-3 py-2 space-y-1 text-xs">
                        <div>
                          <span className="text-gray-400">Input: </span>
                          <code className="text-gray-700">{JSON.stringify(tc.input)}</code>
                        </div>
                        <div>
                          <span className="text-gray-400">Output: </span>
                          <code className="text-gray-700">{JSON.stringify(tc.output)}</code>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Streaming reply */}
            {streamedReply && (
              <div className="border border-green-200 bg-green-50 rounded-lg p-3">
                <span className="text-xs text-green-600 font-medium block mb-1">AI 回复</span>
                <p className="text-sm text-gray-800 whitespace-pre-wrap">
                  {streamedReply}
                  {streamState === "replying" && (
                    <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-0.5 align-middle" />
                  )}
                </p>
              </div>
            )}

            {/* KB sources */}
            {streamKbSources.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">引用知识库:</span>
                {streamKbSources.map((s) => (
                  <span key={s} className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs">
                    {s}
                  </span>
                ))}
              </div>
            )}

            {streamState === "done" && (
              <p className="text-xs text-green-600">{streamError ? "本次处理未完成" : "处理结束"}</p>
            )}
          </div>
        )}

        {/* Show previous agent result if exists and not streaming */}
        {!streaming && streamState === "idle" && agentResult && (
          <div className="space-y-2 mt-3">
            <div className="flex flex-wrap gap-2">
              {agentResult.steps.map((step) => (
                <span key={step} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                  {step}
                </span>
              ))}
            </div>
            {agentResult.tool_calls && agentResult.tool_calls.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {agentResult.tool_calls.map((tc, i) => (
                  <span key={i} className="px-2 py-0.5 bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-full text-xs">
                    已调: {tc.tool}
                  </span>
                ))}
              </div>
            )}
            <p className="text-sm text-gray-600">
              {agentResult.kb_hit
                ? `已引用知识库：${agentResult.kb_sources.join("、")}`
                : "未命中知识库，请结合处理结果查看是否需要人工跟进。"}
            </p>
          </div>
        )}

        {!streaming && streamState === "idle" && !agentResult && (
          <p className="text-sm text-gray-400">
            点击「流式处理」实时查看 Agent 分析、检索、工具调用和回复生成过程。
          </p>
        )}
      </div>


          </div>
        </div>
      </aside>
    </div>
  </div>;
}
