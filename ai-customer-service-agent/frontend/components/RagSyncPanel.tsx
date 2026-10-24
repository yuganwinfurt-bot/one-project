"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchRagSync, startRagSync, type RagSyncJob } from "@/lib/api";

const names: Record<string, string> = {support_knowledge: "知识条目", support_overview: "统计概况", support_category: "问题分类", support_keyword: "高频问题", support_gap: "知识缺口", support_escalation: "人工升级原因", support_rules: "功能规则"};

export default function RagSyncPanel() {
  const [job, setJob] = useState<RagSyncJob | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [ragUrl, setRagUrl] = useState("http://127.0.0.1:4173/rag/?manage=knowledge&knowledge_base_name=售后工单系统");
  const alive = useRef(true);
  const refreshing = useRef(false);
  const active = job?.status === "queued" || job?.status === "running";
  const load = useCallback(async () => {
    if (refreshing.current) return;
    refreshing.current = true;
    try { const result = await fetchRagSync(); if (alive.current) { setJob(result); setError(""); } }
    catch (e) { if (alive.current) setError(e instanceof Error ? e.message : "读取同步进度失败"); }
    finally { refreshing.current = false; }
  }, []);
  useEffect(() => {
    alive.current = true;
    const url = new URL("/rag/", window.location.href);
    if (["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)) url.port = "4173";
    url.searchParams.set("manage", "knowledge");
    url.searchParams.set("knowledge_base_name", "售后工单系统");
    setRagUrl(url.href);
    void load();
    return () => { alive.current = false; };
  }, [load]);
  useEffect(() => {
    if (!active) return;
    const timer = window.setInterval(() => { void load(); }, 2000);
    return () => window.clearInterval(timer);
  }, [active, load]);
  async function sync() {
    if (submitting || active) return;
    setSubmitting(true); setError("");
    try { const result = await startRagSync(); if (alive.current) setJob(result); }
    catch (e) { if (alive.current) setError(e instanceof Error ? e.message : "同步失败"); }
    finally { if (alive.current) setSubmitting(false); }
  }
  const progress = job?.total_chunks ? Math.min(100, Math.round(job.processed_chunks / job.total_chunks * 100)) : 0;
  const result = job?.status === "succeeded" ? job.result : null;
  return <section className="mb-6 rounded-xl border border-slate-200 bg-white p-4 text-sm" aria-label="RAG知识库同步">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div><h2 className="font-semibold text-slate-800">RAG 知识库 · 售后工单系统</h2><p className="mt-1 text-xs text-slate-500">同步启用的知识条目和数据分析；首次同步自动创建知识库，之后只为变化内容计算向量。</p></div>
      <div className="flex flex-wrap gap-2">
        <button type="button" disabled={submitting || active} onClick={() => void sync()} className="rounded border border-blue-200 px-3 py-2 text-blue-600 hover:bg-blue-50 disabled:cursor-wait disabled:opacity-60">{submitting ? "正在提交…" : active ? "正在同步后台数据…" : "同步后台数据到 RAG"}</button>
        <a href={ragUrl} target="_blank" rel="noopener noreferrer" className="rounded border border-slate-200 px-3 py-2 text-slate-600 hover:bg-slate-50">打开 RAG 知识库 ↗</a>
      </div>
    </div>
    {active && <div className="mt-4"><div className="mb-2 flex justify-between text-xs text-slate-500"><span>{job?.status === "queued" ? "已排队，等待开始" : job?.stage === "writing" ? "正在保存索引" : "正在生成资料向量"} · {job?.processed_chunks || 0}/{job?.total_chunks || "待计算"} 分片</span><button onClick={() => void load()} className="text-blue-600">刷新进度</button></div><div className="h-2 overflow-hidden rounded bg-slate-100" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}><div className="h-full bg-blue-500 transition-all" style={{width: `${progress}%`}} /></div></div>}
    {(error || job?.error) && <div className="mt-3 text-red-600" role="alert">{error || job?.error} <button onClick={() => void load()} className="underline">刷新进度</button></div>}
    {result && <div className="mt-3 border-t border-slate-100 pt-3 text-xs text-slate-600"><p>同步完成：{result.record_count} 条记录 · {result.chunk_count} 个分片；新增 {result.added_records || 0}、更新 {result.updated_records || 0}、删除 {result.deleted_records || 0}、未变化 {result.unchanged_records || 0}。本次计算 {result.embedded_chunks || 0} 个向量。</p><div className="mt-2 flex flex-wrap gap-2">{Object.entries(result.by_type || {}).map(([kind,count]) => <span key={kind} className="rounded bg-slate-100 px-2 py-1">{names[kind] || kind} {count}</span>)}</div>{result.cleanup_warning && <p className="mt-2 text-amber-600">新快照已保存，部分旧分片清理失败，可重试同步。</p>}</div>}
  </section>;
}
