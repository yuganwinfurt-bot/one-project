"use client";

import { useState } from "react";
import { processAfterSale, shipExchange } from "@/lib/api";
import { AFTER_SALE_STATUSES, AFTER_SALE_TYPES } from "@/lib/after-sales";
import { TicketDetail } from "@/lib/types";

export default function AfterSalePanel({ ticket, onChange }: { ticket: TicketDetail; onChange: (value: TicketDetail) => void }) {
  const [note, setNote] = useState("");
  const [tracking, setTracking] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const data = ticket.ecommerce;
  if (!data || data.record_type === "consultation") return null;
  const closed = ["completed", "rejected"].includes(data.status);
  const disconnected = !ticket.integration?.connected;
  const canShip = data.service_type === "exchange" && data.status === "approved" && !data.exchange_tracking_no;
  const pendingReply = ticket.messages.some((m) => m.delivery_status === "pending");
  const run = async (action: string) => {
    if (action === "reject" && !note.trim()) { setError("请填写拒绝原因"); return; }
    if (action === "complete" && !window.confirm(data.service_type === "exchange" ? "确认买家已收到换货商品，结束售后？" : "确认已办理退款并结束售后？当前系统未接支付渠道，此操作仅记录处理结果，不会实际划款。")) return;
    setBusy(true); setError("");
    try {
      const updated = action === "ship" ? await shipExchange(ticket.id, tracking.trim()) : await processAfterSale(ticket.id, { action, ...(note.trim() ? { admin_note: note.trim() } : {}) });
      onChange(updated); setNote(""); setTracking("");
    } catch (e) { setError(e instanceof Error ? e.message : "售后操作失败"); }
    finally { setBusy(false); }
  };
  const button = "px-4 py-2 rounded-lg text-sm border disabled:opacity-40 disabled:cursor-not-allowed";
  return (
    <section className="bg-white border border-cyan-200 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between gap-3 mb-4">
        <h2 className="text-lg font-semibold text-gray-900">电商售后 · {AFTER_SALE_TYPES[data.service_type]}</h2>
        <span className="rounded-full bg-cyan-50 text-cyan-800 px-3 py-1 text-sm">{AFTER_SALE_STATUSES[data.status]}</span>
      </div>
      {disconnected && <p className="text-sm text-amber-800 bg-amber-50 p-3 rounded mb-4">{ticket.integration?.error || "正在连接电商服务"}。恢复连接后可处理售后。</p>}
      <dl className="grid sm:grid-cols-2 gap-3 text-sm text-gray-800 mb-4">
        <div><dt className="text-gray-500">订单号 / 售后编号</dt><dd>{data.order_no} / #{data.id}</dd></div>
        <div><dt className="text-gray-500">商品 / 规格</dt><dd>{data.product_name}{data.order?.variant_name ? ` · ${data.order.variant_name}` : ""}</dd></div>
        <div><dt className="text-gray-500">实付 / 数量</dt><dd>¥{data.order?.amount ?? "—"} / {data.order?.quantity ?? "—"} 件</dd></div>
        <div><dt className="text-gray-500">申请时间</dt><dd>{data.create_time}</dd></div>
        <div className="sm:col-span-2"><dt className="text-gray-500">申请原因与说明</dt><dd className="whitespace-pre-wrap">{data.reason}{data.description ? `\n${data.description}` : ""}</dd></div>
        <div><dt className="text-gray-500">买家退回物流</dt><dd>{data.return_tracking_no || (data.return_shipped ? "已寄出，待补单号" : "未寄回")}</dd></div>
        <div><dt className="text-gray-500">换货发货物流</dt><dd>{data.exchange_tracking_no || "暂无"}</dd></div>
        <div className="sm:col-span-2"><dt className="text-gray-500">收货地址</dt><dd>{data.exchange_shipping_address || data.order?.shipping_address || "未填写"}</dd></div>
        {data.admin_note && <div className="sm:col-span-2"><dt className="text-gray-500">处理说明</dt><dd className="whitespace-pre-wrap">{data.admin_note}</dd></div>}
        {data.service_rating != null && <div className="sm:col-span-2"><dt className="text-gray-500">买家服务评价</dt><dd>{data.service_rating} 分 · {data.service_feedback || "无文字评价"}</dd></div>}
      </dl>
      {!closed && <div className="border-t border-gray-100 pt-4 space-y-3">
        <label className="block text-sm text-gray-600">处理说明（拒绝时必填，买家可见）
          <textarea value={note} onChange={(e) => setNote(e.target.value)} maxLength={2000} rows={2} className="mt-1 w-full border border-gray-300 rounded-lg p-2" />
        </label>
        {pendingReply && <p className="text-sm text-amber-700">存在未送达的回复，恢复连接后会自动重试；回复送达后可继续处理。</p>}
        <div className="flex gap-2 flex-wrap">
          {data.status === "pending" && <>
            <button className={`${button} bg-blue-600 text-white`} disabled={busy || disconnected || pendingReply} onClick={() => run("approve")}>同意申请</button>
            <button className={`${button} border-red-200 text-red-600`} disabled={busy || disconnected || pendingReply} onClick={() => run("reject")}>拒绝申请</button>
          </>}
          {data.status === "approved" && <button className={`${button} bg-green-600 text-white`} disabled={busy || disconnected || pendingReply || !!data.completion_blocked_reason} onClick={() => run("complete")}>{data.service_type === "exchange" ? "完成换货售后" : "确认退款已完成"}</button>}
        </div>
        {canShip && <div className="flex gap-2 flex-wrap">
          <input aria-label="换货物流单号" value={tracking} onChange={(e) => setTracking(e.target.value)} maxLength={100} placeholder="填写换货发货物流单号" className="border border-gray-300 rounded-lg p-2 text-sm flex-1" />
          <button className={`${button} text-blue-700`} disabled={busy || disconnected || pendingReply || !tracking.trim() || !data.return_tracking_no || !data.return_shipped} onClick={() => run("ship")}>提交换货发货</button>
        </div>}
        {data.completion_blocked_reason && <p className="text-sm text-gray-500">当前进度：{data.completion_blocked_reason}</p>}
      </div>}
      {closed && <p className="text-sm text-gray-500 border-t border-gray-100 pt-3">售后已结束，申请与聊天记录已保留。</p>}
      {busy && <p className="text-sm text-blue-600 mt-3">正在提交…</p>}
      {error && <p role="alert" className="text-sm text-red-600 mt-3">{error}</p>}
    </section>
  );
}
