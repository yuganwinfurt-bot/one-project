"use client";
import { useRef, useState } from "react";
import { takeOverTicket, fetchTicket, endHumanTicket } from "@/lib/api";
import { TicketDetail } from "@/lib/types";

export default function HumanHandoffPanel({ ticket, onChange, compact = false }: { ticket: TicketDetail; onChange: (value: TicketDetail) => void; compact?: boolean }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("问题已解决");
  const dialog = useRef<HTMLDialogElement>(null);
  const source = ticket.ecommerce;
  if (!source || source.conversation_closed) return null;
  const requested = source.handling_mode === "human_requested";
  const human = source.handling_mode === "human";
  const claim = async () => {
    setBusy(true); setError("");
    try { await takeOverTicket(ticket.id); onChange(await fetchTicket(ticket.id)); }
    catch (e) { setError(e instanceof Error ? e.message : "接待失败"); }
    finally { setBusy(false); }
  };
  const endSession = async (event: React.FormEvent) => {
    event.preventDefault(); if (busy || !reason.trim()) return;
    setBusy(true); setError("");
    try { const updated = await endHumanTicket(ticket.id, reason.trim()); dialog.current?.close(); onChange(updated); }
    catch (e) { setError(e instanceof Error ? e.message : "结束人工服务失败"); }
    finally { setBusy(false); }
  };
  return <section className={`${compact ? "shrink-0 border-b px-4 py-2" : "rounded-xl border p-4 mb-6"} ${requested ? "border-amber-300 bg-amber-50" : "border-cyan-200 bg-cyan-50"}`}>
    <div className="flex flex-wrap items-center justify-between gap-3"><div className="min-w-0 flex-1"><h2 className={`${compact ? "text-xs font-medium" : "font-semibold"} text-slate-800`}>{requested ? "买家申请人工接待" : human ? "人工客服已接入" : "AI 客服接待中"}</h2><p className={`${compact ? "mt-0.5 line-clamp-2 break-words text-[11px]" : "mt-1 text-sm"} text-slate-600`}>{requested ? source.human_reason || "买家希望人工协助，AI自动回复已停止。" : human ? "可直接在聊天框发送人工回复。" : "买家的咨询默认由Agent控制台当前模型回答。"}</p></div>
      {requested && <button onClick={claim} disabled={busy} className={`${compact ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm"} rounded bg-blue-600 text-white disabled:opacity-50`}>{busy ? "正在接入…" : "接入人工接待"}</button>}
      {(requested || human) && <button disabled={busy} onClick={() => { setError(""); setReason("问题已解决"); dialog.current?.showModal(); }} className="rounded border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-600 disabled:opacity-50">结束人工服务</button>}
    </div>{error && <p className="text-sm text-red-600 mt-2">{error}</p>}
    <dialog ref={dialog} onCancel={event => { if (busy) event.preventDefault(); }} className="m-auto w-[min(430px,92vw)] rounded-xl border border-slate-200 bg-white p-6 text-slate-700 shadow-xl backdrop:bg-black/30"><form onSubmit={endSession}><h2 className="text-lg font-semibold">结束本次人工服务</h2><p className="my-3 text-sm leading-6 text-slate-500">结束后双方都不能继续在本次会话中发送消息，聊天记录会保留。未完成的退款、换货仍按原流程处理。</p><label className="block text-sm">结束原因（买家可见）<textarea required maxLength={1000} value={reason} onChange={event => setReason(event.target.value)} rows={3} className="mt-2 w-full rounded-lg border border-slate-300 p-3 text-sm" /></label>{error && <p role="alert" className="mt-3 text-sm text-red-600">{error}</p>}<div className="mt-5 flex justify-end gap-2"><button type="button" disabled={busy} onClick={() => dialog.current?.close()} className="rounded border px-4 py-2 text-sm">继续沟通</button><button type="submit" disabled={busy || !reason.trim()} className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">{busy ? "正在结束…" : "结束服务"}</button></div></form></dialog>
  </section>;
}
