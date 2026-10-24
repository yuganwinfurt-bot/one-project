"use client";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { getStaffSession, loginStaff, logoutStaff, type StaffUser } from "@/lib/auth";

type AuthState = {user: StaffUser | null; loading: boolean; login: (name: string, password: string) => Promise<void>; logout: () => Promise<void>};
const Context = createContext<AuthState | null>(null);
export function AuthProvider({children}: {children: React.ReactNode}) {
  const [user, setUser] = useState<StaffUser | null>(null);
  const [loading, setLoading] = useState(true);
  const generation = useRef(0);
  useEffect(() => {
    let live = true;
    const version = generation.current;
    getStaffSession().then(data => { if (live && version === generation.current) setUser(data.user); }).catch(() => { if (live && version === generation.current) setUser(null); }).finally(() => { if (live && version === generation.current) setLoading(false); });
    const expired = () => setUser(null);
    window.addEventListener("support-auth-expired", expired);
    return () => { live = false; window.removeEventListener("support-auth-expired", expired); };
  }, []);
  const login = useCallback(async (name: string, password: string) => { ++generation.current; const data = await loginStaff(name, password); setUser(data.user); setLoading(false); }, []);
  const logout = useCallback(async () => { await logoutStaff(); ++generation.current; setUser(null); }, []);
  return <Context.Provider value={{user, loading, login, logout}}>{children}</Context.Provider>;
}
export function useStaffAuth() { const context = useContext(Context); if (!context) throw new Error("AuthProvider is required"); return context; }
