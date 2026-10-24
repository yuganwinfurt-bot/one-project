"use client";

import { use } from "react";
import Link from "next/link";
import TicketConversation from "@/components/TicketConversation";

export default function TicketDetailPage({params}:{params:Promise<{id:string}>}) {
  const {id} = use(params);
  const ticketId = Number(id);
  if (!Number.isInteger(ticketId) || ticketId < 1) return <div className="p-6"><p>工单编号无效</p><Link href="/tickets">返回工单列表</Link></div>;
  return <TicketConversation key={ticketId} ticketId={ticketId} />;
}
