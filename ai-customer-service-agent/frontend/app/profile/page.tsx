"use client";
import { useStaffAuth } from "@/components/AuthProvider";
export default function ProfilePage() {
  const {user} = useStaffAuth();
  if (!user) return null;
  return <section className="m-4 rounded border border-slate-200 bg-white p-5"><h1 className="mb-2 text-xl font-semibold">个人资料</h1><p className="mb-6 text-sm text-slate-500">资料来自电商分析平台账号。</p><dl className="grid max-w-2xl grid-cols-[80px_1fr] gap-x-5 gap-y-5 text-sm">{[["账号",user.username],["名称",user.name],["角色",user.role === "admin" ? "管理员" : "运营"],["邮箱",user.email || "未填写"],["手机号",user.phone || "未填写"]].map(([label,value])=><div className="contents" key={label}><dt className="text-slate-500">{label}</dt><dd className="break-all text-slate-800">{value}</dd></div>)}</dl></section>;
}
