"use client";
import { useEffect, useState } from "react";
import { getActiveAgentModel } from "@/lib/agentModel";

export default function AgentModelStatus() {
  const [name, setName] = useState("正在连接控制台…");
  useEffect(() => {
    let active = true;
    const sync = () => getActiveAgentModel().then((profile) => { if (active) setName(profile.name || profile.model); }).catch(() => { if (active) setName("请前往Agent控制台选择模型"); });
    sync();
    window.addEventListener("focus", sync);
    return () => { active = false; window.removeEventListener("focus", sync); };
  }, []);
  return <p className="mt-1.5 pl-4 text-[11px] text-slate-400">{name}</p>;
}
