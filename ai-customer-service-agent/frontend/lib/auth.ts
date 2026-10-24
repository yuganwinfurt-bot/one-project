function supportApiBase() {
  const configured = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002";
  if (typeof window === "undefined") return configured;
  const url = new URL(configured, window.location.href);
  const local = ["127.0.0.1", "localhost"];
  if (local.includes(url.hostname) && local.includes(window.location.hostname)) url.hostname = window.location.hostname;
  return url.href.replace(/\/$/, "");
}
export const SUPPORT_API_BASE = supportApiBase();
export interface StaffUser { id: number; username: string; name: string; role: "admin" | "user"; avatar?: string; email?: string; phone?: string; status: number }

export async function supportFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const response = await fetch(input, {...init, credentials: "include"});
  if ((response.status === 401 || response.status === 403) && typeof window !== "undefined") {
    if (response.status === 401) window.dispatchEvent(new Event("support-auth-expired"));
  }
  return response;
}
async function authRequest(path: string, body?: {username: string; password: string}) {
  const response = await fetch(`${SUPPORT_API_BASE}/api/auth/${path}`, {method: path === "me" ? "GET" : "POST", credentials: "include", cache: "no-store", headers: body ? {"Content-Type": "application/json"} : {}, body: body ? JSON.stringify(body) : undefined});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "账号服务暂时不可用");
  return data as {user: StaffUser};
}
export const getStaffSession = () => authRequest("me");
export const loginStaff = (username: string, password: string) => authRequest("login", {username, password});
export async function logoutStaff() {
  const response = await fetch(`${SUPPORT_API_BASE}/api/auth/logout`, {method: "POST", credentials: "include"});
  if (!response.ok) throw new Error("退出失败，请重试");
}
