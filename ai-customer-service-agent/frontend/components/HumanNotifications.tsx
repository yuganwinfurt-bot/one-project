"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { fetchHumanNotifications } from "@/lib/api";

export default function HumanNotifications() {
  const [data, setData] = useState<Awaited<ReturnType<typeof fetchHumanNotifications>>>({ count: 0, items: [] });
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let active = true;
    const load = () => fetchHumanNotifications().then((value) => { if (active) setData(value); }).catch(() => {});
    load();
    const timer = setInterval(() => { if (!document.hidden) load(); }, 8000);
    const outside = (event: PointerEvent) => { if (!ref.current?.contains(event.target as Node)) setOpen(false); };
    document.addEventListener("pointerdown", outside);
    return () => { active = false; clearInterval(timer); document.removeEventListener("pointerdown", outside); };
  }, []);
  return <div ref={ref} className="relative">
    <button className="relative flex h-8 w-8 items-center justify-center text-slate-500" aria-label={`人工接待提醒：${data.count} 条`} aria-expanded={open} onClick={() => setOpen(!open)}>
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>
      {data.count > 0 && <span className="absolute -top-1 -right-1 rounded-full bg-red-500 px-1.5 text-[10px] text-white">{data.count}</span>}
    </button>
    {open && <div className="absolute right-0 top-full z-50 mt-2 w-80 max-w-[85vw] rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
      <h3 className="mb-2 text-sm font-semibold text-slate-800">买家申请人工接待</h3>
      {!data.count && <p className="py-3 text-xs text-slate-500">暂无待接待请求</p>}
      {data.items.slice(0, 8).map((item) => <Link onClick={() => setOpen(false)} href={`/tickets/${item.ticket_id}`} key={item.ticket_id} className="block rounded-lg px-2 py-3 hover:bg-slate-50"><strong className="text-sm text-slate-700">{item.customer_name} · 工单 #{item.ticket_id}</strong><p className="mt-1 text-xs text-slate-500">{item.reason}</p></Link>)}
    </div>}
  </div>;
}
