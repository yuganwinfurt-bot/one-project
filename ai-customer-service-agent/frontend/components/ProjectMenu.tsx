"use client";

import { useId, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import styles from "./ProjectMenu.module.css";

// Keep the same local destinations as the commerce project's project menu.
const projects = [
  { label: "电商分析平台", href: "http://127.0.0.1:35173/manager/home" },
  { label: "客服工单系统", href: "http://127.0.0.1:3000/tickets" },
  { label: "Agent 控制台", href: "http://127.0.0.1:8020/" },
  { label: "RAG 知识库", href: "http://127.0.0.1:4173/" },
  { label: "项目主页", href: "http://127.0.0.1:8030/" },
];

export default function ProjectMenu() {
  const menuId = useId();
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState({ left: 8, top: 8, width: 235 });
  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLElement>(null);

  useLayoutEffect(() => {
    if (!open) return;
    const positionMenu = () => {
      const anchor = buttonRef.current?.getBoundingClientRect();
      if (!anchor || !anchor.width) { setOpen(false); return; }
      const width = Math.min(235, window.innerWidth - 16);
      const height = menuRef.current?.offsetHeight || 260;
      setPosition({
        left: Math.max(8, Math.min(anchor.left, window.innerWidth - width - 8)),
        top: Math.max(8, Math.min(anchor.bottom + 10, window.innerHeight - height - 8)),
        width,
      });
    };
    const outside = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!buttonRef.current?.contains(target) && !menuRef.current?.contains(target)) setOpen(false);
    };
    const keydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") { setOpen(false); buttonRef.current?.focus(); }
    };
    positionMenu();
    window.addEventListener("resize", positionMenu);
    document.addEventListener("scroll", positionMenu, true);
    document.addEventListener("pointerdown", outside);
    document.addEventListener("keydown", keydown);
    return () => {
      window.removeEventListener("resize", positionMenu);
      document.removeEventListener("scroll", positionMenu, true);
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("keydown", keydown);
    };
  }, [open]);

  return <>
    <button ref={buttonRef} type="button" className={styles.toggle} aria-label="打开项目菜单" aria-controls={menuId} aria-haspopup="true" aria-expanded={open} onClick={() => setOpen(!open)}>
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
    </button>
    {open && createPortal(
      <nav ref={menuRef} id={menuId} className={styles.menu} style={position} aria-label="项目入口">
        <span className={styles.heading}>项目入口</span>
        {projects.map((project) => project.label === "客服工单系统" ? <span key={project.href} className={styles.current}>客服工单系统 <small>当前页面</small></span> : <a key={project.href} href={project.href} className={styles.link} onClick={() => setOpen(false)}>{project.label}<span aria-hidden="true">→</span></a>)}
      </nav>, document.body
    )}
  </>;
}
