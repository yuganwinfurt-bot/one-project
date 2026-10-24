"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useStaffAuth } from "@/components/AuthProvider";
import styles from "./AppShell.module.css";
import { usePathname, useRouter } from "next/navigation";
import ProjectMenu from "@/components/ProjectMenu";
import HumanNotifications from "@/components/HumanNotifications";
import AgentModelStatus from "@/components/AgentModelStatus";

const navigation = [
  { href: "/tickets", label: "工单列表", icon: "tickets" },
  { href: "/knowledge", label: "知识库管理", icon: "knowledge" },
  { href: "/analytics", label: "数据分析", icon: "analytics" },
  { href: "/agent", label: "智能客服助手", icon: "agent" },
] as const;

function NavIcon({ name }: { name: (typeof navigation)[number]["icon"] }) {
  const paths = {
    tickets: <><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v11a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 17.5z" /><path d="M8 9h8M8 13h8M8 17h4" /></>,
    knowledge: <><path d="M5 4.8A2.8 2.8 0 0 1 7.8 2H19v17H7.8A2.8 2.8 0 0 0 5 21z" /><path d="M5 5v16M9 7h6M9 11h6" /></>,
    analytics: <><path d="M4 19V5M4 19h17" /><path d="m7 15 4-4 3 2 6-7" /><path d="M17 6h3v3" /></>,
    agent: <><path d="M12 3a8 8 0 0 0-8 8v3a3 3 0 0 0 3 3h1v-6H7a5 5 0 0 1 10 0h-1v6h1a3 3 0 0 0 3-3v-3a8 8 0 0 0-8-8Z" /><path d="M9 20h4" /></>,
  };

  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" className="h-[19px] w-[19px] shrink-0">
      {paths[name]}
    </svg>
  );
}

function pageLabel(pathname: string) {
  if (pathname.startsWith("/profile")) return "个人资料";
  if (pathname.startsWith("/knowledge")) return "知识库管理";
  if (pathname.startsWith("/analytics")) return "数据分析";
  if (pathname.startsWith("/agent")) return "智能客服助手";
  if (pathname.startsWith("/tickets/")) return "工单详情";
  return "工单列表";
}

function AccountMenu() {
  const {user,logout} = useStaffAuth();
  const router = useRouter();
  const [open,setOpen] = useState(false);
  const [busy,setBusy] = useState(false);
  const menu = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const outside = (e: PointerEvent) => { if (!menu.current?.contains(e.target as Node)) setOpen(false); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("pointerdown",outside); document.addEventListener("keydown",key);
    return () => { document.removeEventListener("pointerdown",outside); document.removeEventListener("keydown",key); };
  },[open]);
  async function signOut() {
    if (busy) return; setBusy(true);
    try { await logout(); router.replace("/login"); }
    catch (e) { window.alert(e instanceof Error ? e.message : "退出失败"); }
    finally { setBusy(false); }
  }
  const name = user?.name || user?.username || "";
  return <div className={styles.account} ref={menu}><button type="button" className={styles.accountTrigger} aria-expanded={open} aria-label="账号菜单" onClick={()=>setOpen(!open)}><span>{name}</span><span className={styles.avatar}>{name.slice(0,1)}{user?.avatar && <img src={user.avatar} alt="" onError={e=>{ e.currentTarget.style.display="none"; }} />}</span></button>{open && <div className={styles.accountMenu}><Link href="/profile" onClick={()=>setOpen(false)}>个人资料</Link><button type="button" disabled={busy} onClick={()=>void signOut()}>{busy ? "正在退出…" : "退出登录"}</button></div>}</div>;
}

export default function AppShell({children}: {children: React.ReactNode}) {
  const pathname = usePathname();
  const router = useRouter();
  const {user,loading} = useStaffAuth();
  const [collapsed,setCollapsed] = useState(false);
  const isLogin = pathname === "/login";
  useEffect(()=>{ try { setCollapsed(localStorage.getItem("support.sidebar-collapsed") === "1"); } catch {} },[]);
  useEffect(()=>{
    if (!loading && !user && !isLogin) router.replace(`/login?next=${encodeURIComponent(pathname+window.location.search)}`);
  },[loading,user,isLogin,pathname,router]);
  function fold() { setCollapsed(value=>{ try {localStorage.setItem("support.sidebar-collapsed",value ? "0" : "1");} catch {} return !value; }); }
  if (isLogin) return <>{children}</>;
  if (loading || !user) return <div className={styles.loading}>正在读取登录状态…</div>;
  const label = pageLabel(pathname);
  return <div className={styles.shell}><aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ""}`}><div className={styles.brand}><ProjectMenu /><Link href="/tickets">售后工单系统</Link></div><nav className={styles.navigation}>{navigation.map(item=>{
    const active = pathname === item.href || pathname.startsWith(item.href+"/");
    return <Link key={item.href} href={item.href} title={collapsed ? item.label : undefined} className={`${styles.navLink} ${active ? styles.active : ""}`}><NavIcon name={item.icon} /><span>{item.label}</span></Link>;
  })}</nav><div className={styles.footer}><div><strong><i />Agent 控制台模型</strong><AgentModelStatus /></div><p>售后工单系统 · v1.0</p></div></aside><div className={styles.body}><header className={styles.header}><div className={styles.breadcrumb}><div className={styles.mobileMenu}><ProjectMenu /></div><button className={styles.fold} type="button" onClick={fold} aria-label={collapsed ? "展开侧栏" : "收起侧栏"}>☰</button><Link href="/tickets">首页</Link><span>/</span><span>{label}</span></div><div className={styles.right}><span className={styles.deployment}>本地部署</span><HumanNotifications /><AccountMenu /></div></header><div className={styles.tags}><Link href="/tickets">首页</Link><span className={styles.tagActive}><i />{label}</span></div><main className={`${styles.main} ${/^\/tickets\/[^/]+\/?$/.test(pathname) ? styles.conversationMain : ""}`}>{children}</main></div></div>;
}
