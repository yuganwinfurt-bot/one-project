"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useStaffAuth } from "@/components/AuthProvider";
import DemoAccounts from "@/components/DemoAccounts";
import ProjectMenu from "@/components/ProjectMenu";

export default function LoginPage() {
  const {login} = useStaffAuth();
  const router = useRouter();
  const [username,setUsername] = useState("");
  const [password,setPassword] = useState("");
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  async function submit(event: React.FormEvent) {
    event.preventDefault(); if (busy || !username.trim() || !password) return;
    setBusy(true); setError("");
    try {
      await login(username,password);
      const next = new URLSearchParams(window.location.search).get("next") || "/tickets";
      router.replace(/^\/(tickets(?:\/\d+)?|knowledge|analytics|agent|profile)(?:\?|$)/.test(next) ? next : "/tickets");
    } catch (e) { setError(e instanceof Error ? e.message : "登录失败"); }
    finally { setBusy(false); }
  }
  return <main className="flex min-h-dvh items-center justify-center bg-[#f0f2f5] p-6"><section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-sm"><div className="mb-6 flex items-center gap-3"><ProjectMenu /><h1 className="text-xl font-semibold text-slate-800">售后工单系统</h1></div><h2 className="mb-2 text-lg font-semibold">后台登录</h2><p className="mb-6 text-sm leading-6 text-slate-500">使用电商分析平台的管理员或运营账号和密码登录。</p><form onSubmit={submit} className="space-y-4"><label className="block text-sm text-slate-600">账号<input autoComplete="username" autoFocus required value={username} onChange={e=>setUsername(e.target.value)} className="mt-2 w-full rounded border border-slate-300 px-3 py-2.5 text-slate-800" placeholder="管理员或运营账号" /></label><label className="block text-sm text-slate-600">密码<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} className="mt-2 w-full rounded border border-slate-300 px-3 py-2.5 text-slate-800" placeholder="输入密码" /></label>{error && <p role="alert" className="text-sm text-red-600">{error}</p>}<button disabled={busy || !username.trim() || !password} className="w-full rounded bg-[#409eff] py-2.5 font-medium text-white disabled:opacity-50">{busy ? "正在登录…" : "登录"}</button></form><DemoAccounts onChoose={(name,secret)=>{setUsername(name);setPassword(secret);setError("");}} /></section></main>;
}
