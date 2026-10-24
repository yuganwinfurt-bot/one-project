"use client";
import { useEffect, useState } from "react";
import { SUPPORT_API_BASE } from "@/lib/auth";
type Account = {id:number;label:string;username:string;password:string|null;role:string};
export default function DemoAccounts({onChoose}:{onChoose:(username:string,password:string)=>void}) {
  const [accounts,setAccounts]=useState<Account[]>([]);
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(true);
  useEffect(()=>{
    let active=true, running=false;
    async function load() {
      if(running) return; running=true;
      try {
        const response=await fetch(`${SUPPORT_API_BASE}/api/auth/demo-accounts`,{cache:"no-store",credentials:"include"});
        const data=await response.json();
        if(!response.ok) throw new Error(data.detail || "读取演示账号失败");
        if(active) { setAccounts(data.accounts || []); setError(""); }
      } catch(e) { if(active) setError(e instanceof Error ? e.message : "演示账号暂时无法读取"); }
      finally { running=false; if(active) setLoading(false); }
    }
    const refresh=()=>{ if(!document.hidden) void load(); };
    void load(); const timer=setInterval(refresh,15000); window.addEventListener("focus",refresh);
    return ()=>{active=false;clearInterval(timer);window.removeEventListener("focus",refresh);};
  },[]);
  return <section className="mt-6 border-t border-slate-100 pt-4"><h3 className="mb-3 text-sm font-semibold text-slate-700">演示账号 · 点击填入</h3>{loading && <p className="text-xs text-slate-500">正在读取电商演示账号…</p>}{error && <p role="alert" className="text-xs text-red-600">{error}</p>}<div className="space-y-2">{accounts.map(account=><button key={account.id} type="button" disabled={!account.password} onClick={()=>account.password && onChoose(account.username,account.password)} className="flex w-full items-center justify-between rounded border border-slate-200 p-3 text-left text-sm hover:border-blue-300 disabled:opacity-50"><span><b className="font-medium">{account.label}</b><span className="ml-2 text-slate-500">{account.username}</span></span><span className="text-xs text-blue-500">{account.password ? "填入" : "请手动输入密码"}</span></button>)}</div>{!loading && !error && !accounts.length && <p className="text-xs text-slate-500">暂无可用演示账号</p>}<p className="mt-3 text-xs leading-5 text-slate-400">与电商分析平台共用演示账号，账号变更会自动更新。</p></section>;
}
