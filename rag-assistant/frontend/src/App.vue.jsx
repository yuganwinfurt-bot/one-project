import { Fragment, h, Teleport } from "vue";
import { createStateFrame, useEffect, useMemo, useRef, useState } from "./vue-state.js";
import Markdown from "./Markdown.js";
import ExecutionProcess from "./ExecutionProcess.jsx";
import { runBrowserRag } from "./rag-workflow.js";
import {
  BookOpen, Bot, Check, ChevronDown, ChevronLeft, ChevronRight,
  CircleHelp, FileText, FolderKanban, Home, Layers3, MessageSquare,
  Menu, PanelLeftClose, Pencil, Plus, RotateCcw, Send, Settings2, ShieldCheck, Sparkles, Trash2, Upload,
  X,
} from "./icons.js";
import { API, request } from "./api.js";

const jsonOptions = (method, body) => ({ method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const uniqueId = () => globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
const filesFromTransfer = (event) => Array.from(event.dataTransfer?.files || []);
const transferHasFiles = (event) => Array.from(event.dataTransfer?.types || []).includes("Files");
const localProjectHost = ["127.0.0.1", "localhost", "[::1]"].includes(window.location.hostname);
const rememberedProjectKey = "yugan-rag-active-project";
function getRememberedProjectId() {
  try { return window.sessionStorage.getItem(rememberedProjectKey) || ""; } catch { return ""; }
}
function rememberProjectId(id) {
  try {
    if (id) window.sessionStorage.setItem(rememberedProjectKey, id);
    else window.sessionStorage.removeItem(rememberedProjectKey);
  } catch {}
}
const projectHomeUrl = new URL("/", window.location.href);
if (localProjectHost) projectHomeUrl.port = "8030";
const agentUrl = new URL(import.meta.env.VITE_AGENT_URL || (localProjectHost ? "/" : "/agent/"), window.location.href);
if (localProjectHost && !import.meta.env.VITE_AGENT_URL) agentUrl.port = "8020";
if (!agentUrl.pathname.endsWith("/")) agentUrl.pathname += "/";
const ecommerceEnvUrl = import.meta.env.VITE_ECOM_URL;
const ecommerceUrl = new URL(ecommerceEnvUrl || (localProjectHost ? "/" : "/ecommerce/"), window.location.href);
if (localProjectHost && !ecommerceEnvUrl) ecommerceUrl.port = "35173";
if (!ecommerceUrl.pathname.endsWith("/")) ecommerceUrl.pathname += "/";

async function requestBrowserModel(profile, messages) {
  if (profile.mode === "server") {
    let response;
    try {
      response = await fetch(new URL("api/models/server-ollama/chat/completions", agentUrl), {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(profile.api_token ? { Authorization: `Bearer ${profile.api_token}` } : {}),
        },
        body: JSON.stringify({ model: profile.model, messages, max_tokens: 1024 }),
        signal: AbortSignal.timeout(300000),
      });
    } catch (error) {
      if (error.name === "TimeoutError") throw new Error("服务器模型请求超时。");
      if (error instanceof TypeError) throw new Error("无法连接 Agent 服务器模型，请检查 Agent 地址及跨源配置。");
      throw error;
    }
    const raw = await response.text();
    let payload; try { payload = JSON.parse(raw); } catch { payload = {}; }
    if (!response.ok) throw new Error(payload.detail || payload.error?.message || `Agent 模型接口返回 HTTP ${response.status}`);
    const answer = payload.choices?.[0]?.message?.content;
    if (typeof answer !== "string" || !answer.trim()) throw new Error("服务器模型没有返回文本回答。");
    return answer;
  }
  const anthropic = profile.provider === "anthropic" || profile.vendor === "Claude";
  const endpoint = profile.endpoint.replace(/\/+$/, "");
  const url = anthropic
    ? `${endpoint.endsWith("/v1") ? endpoint : `${endpoint}/v1`}/messages`
    : `${endpoint}/chat/completions`;
  const headers = { "Content-Type": "application/json" };
  let body;
  if (anthropic) {
    headers["x-api-key"] = profile.api_key;
    headers["anthropic-version"] = "2023-06-01";
    headers["anthropic-dangerous-direct-browser-access"] = "true";
    body = {
      model: profile.model,
      max_tokens: 4096,
      system: messages.filter((item) => item.role === "system").map((item) => item.content).join("\n\n"),
      messages: messages.filter((item) => item.role !== "system"),
    };
  } else {
    if (profile.mode !== "local") headers.Authorization = `Bearer ${profile.api_key}`;
    body = { model: profile.model, messages, stream: false };
  }
  let response;
  try { response = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: AbortSignal.timeout(120000) }); }
  catch (error) {
    if (error.name === "TimeoutError") throw new Error("模型请求超时。");
    if (error instanceof TypeError) throw new Error("浏览器无法直连模型接口，可能是接口未开放跨源访问；API Key 没有发送到 RAG 服务。");
    throw error;
  }
  const raw = await response.text();
  let payload; try { payload = JSON.parse(raw); } catch { payload = {}; }
  if (!response.ok) throw new Error(payload.error?.message || payload.message || `模型接口返回 HTTP ${response.status}`);
  const answer = anthropic
    ? (payload.content || []).filter((item) => item.type === "text").map((item) => item.text).join("")
    : payload.choices?.[0]?.message?.content;
  if (typeof answer !== "string" || !answer.trim()) throw new Error("模型接口没有返回文本回答。");
  return answer;
}

function renderApp() {
  const [projects, setProjects] = useState([]);
  const [knowledgeBases, setKnowledgeBases] = useState([]);
  const [projectId, setProjectId] = useState("");
  const [chats, setChats] = useState([]);
  const [chatId, setChatId] = useState("");
  const [messages, setMessages] = useState([]);
  const [selectedKbIds, setSelectedKbIds] = useState([]);
  const [scopeMode, setScopeMode] = useState("project");
  const [status, setStatus] = useState(null);
  const [auth, setAuth] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authAvailable, setAuthAvailable] = useState(false);
  const [identityBusy, setIdentityBusy] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [loginBusy, setLoginBusy] = useState(false);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [agentModelProfiles, setAgentModelProfiles] = useState([]);
  const [selectedAgentModelId, setSelectedAgentModelId] = useState("");
  const [browserModel, setBrowserModel] = useState(null);
  const [modelSyncing, setModelSyncing] = useState(false);
  const [modelSettings, setModelSettings] = useState({ mode: "local", local_model: "qwen3.5:9b" });
  const [modelSaving, setModelSaving] = useState(false);
  const [modelSettingsError, setModelSettingsError] = useState("");
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [scopeSaving, setScopeSaving] = useState(false);
  const [toast, setToast] = useState("");
  const [brandMenuOpen, setBrandMenuOpen] = useState(false);
  const [sidebarMenu, setSidebarMenu] = useState(null);
  const [deleteChatTarget, setDeleteChatTarget] = useState(null);
  const [deleteChatSaving, setDeleteChatSaving] = useState(false);
  const [deleteProjectTarget, setDeleteProjectTarget] = useState(null);
  const [deleteProjectSaving, setDeleteProjectSaving] = useState(false);
  const [deleteKbTarget, setDeleteKbTarget] = useState(null);
  const [deleteKbSaving, setDeleteKbSaving] = useState(false);
  const [renameTarget, setRenameTarget] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const [renameSaving, setRenameSaving] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try { return window.localStorage.getItem("yugan-rag-sidebar-collapsed") === "1"; } catch { return false; }
  });
  const [projectSpaceCollapsed, setProjectSpaceCollapsed] = useState(() => {
    try { return window.localStorage.getItem("yugan-rag-project-space-collapsed") === "1"; } catch { return false; }
  });
  const [processClock, setProcessClock] = useState(() => Date.now());
  const [smallViewport, setSmallViewport] = useState(() => window.innerWidth <= 680);
  const [brandMenuPosition, setBrandMenuPosition] = useState({ left: "8px", top: "50px" });
  const [managerOpen, setManagerOpen] = useState(false);
  const [activeKbId, setActiveKbId] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const [uploadTargetKbId, setUploadTargetKbId] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [chunkDocument, setChunkDocument] = useState(null);
  const [chunks, setChunks] = useState([]);
  const [chunkTotal, setChunkTotal] = useState(0);
  const [chunkOffset, setChunkOffset] = useState(0);
  const [chunksLoading, setChunksLoading] = useState(false);
  const [chunksError, setChunksError] = useState("");
  const [deletingChunkId, setDeletingChunkId] = useState("");
  const [kbName, setKbName] = useState("");
  const [kbDescription, setKbDescription] = useState("");
  const [showKbForm, setShowKbForm] = useState(false);
  const [scopeOpen, setScopeOpen] = useState(false);
  const [projectDialog, setProjectDialog] = useState(false);
  const [editingProject, setEditingProject] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectKbIds, setProjectKbIds] = useState([]);
  const [projectSaving, setProjectSaving] = useState(false);
  const endRef = useRef(null);
  const fileRef = useRef(null);
  const brandSwitchRef = useRef(null);
  const brandToggleRef = useRef(null);
  const brandMenuRef = useRef(null);
  const sidebarMenuRef = useRef(null);
  const scopeRef = useRef(null);
  const generationRef = useRef(null);
  const scopeQueueRef = useRef(Promise.resolve());
  const scopeSequenceRef = useRef(0);
  const chunkRequestRef = useRef(0);
  const documentRequestRef = useRef(0);
  const chatRequestRef = useRef(0);
  const projectRequestRef = useRef(0);
  const currentChatIdRef = useRef(chatId);
  const currentProjectIdRef = useRef(projectId);
  const currentKbIdRef = useRef(activeKbId);
  const currentRoleRef = useRef(auth?.role || "");
  const uploadRunningRef = useRef(false);
  const dragDepthRef = useRef(0);
  currentChatIdRef.current = chatId;
  currentProjectIdRef.current = projectId;
  currentKbIdRef.current = activeKbId;
  currentRoleRef.current = auth?.role || "";
  const currentProject = projects.find((project) => project.id === projectId);
  const currentChat = chats.find((chat) => chat.id === chatId);
  const activeKb = knowledgeBases.find((kb) => kb.id === activeKbId);
  const activeScopeMode = scopeMode;
  const activeScopeIds = activeScopeMode === "project" ? (currentProject?.knowledge_base_ids || []) : selectedKbIds;
  const selectedKbs = useMemo(() => knowledgeBases.filter((kb) => activeScopeIds.includes(kb.id)), [knowledgeBases, activeScopeIds]);

  useEffect(() => {
    if (!busy) return;
    setProcessClock(Date.now());
    const timer = window.setInterval(() => setProcessClock(Date.now()), 500);
    return () => window.clearInterval(timer);
  }, [busy]);

  function toggleProjectSpace() {
    setProjectSpaceCollapsed((previous) => {
      const collapsed = !previous;
      try { window.localStorage.setItem("yugan-rag-project-space-collapsed", collapsed ? "1" : "0"); } catch {}
      return collapsed;
    });
  }

  useEffect(() => {
    const resize = () => setSmallViewport(window.innerWidth <= 680);
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  function toggleSidebar() {
    setBrandMenuOpen(false);
    if (smallViewport) {
      setMobileNav((value) => !value);
    } else {
      const collapsed = !sidebarCollapsed;
      setSidebarCollapsed(collapsed);
      try { window.localStorage.setItem("yugan-rag-sidebar-collapsed", collapsed ? "1" : "0"); } catch {}
    }
  }

  function notify(message) {
    setToast(message);
    window.clearTimeout(notify.timer);
    notify.timer = window.setTimeout(() => setToast(""), 2600);
  }

  async function refreshKnowledgeBases() {
    const data = await request("/api/knowledge-bases");
    setKnowledgeBases(data);
    if (!activeKbId && data.length) setActiveKbId(data[0].id);
    return data;
  }

  async function refreshIdentity() {
    setAuthLoading(true);
    try {
      const identity = await request("/api/auth/status");
      setAuth({ ...identity, subject: identity.role === "admin" ? "admin" : identity.subject });
      setAuthAvailable(true);
      return identity;
    } catch (error) {
      setAuthAvailable(false);
      notify(`无法读取身份：${error.message}`);
      return null;
    } finally {
      setAuthLoading(false);
    }
  }

  function openLogin() {
    setLoginUsername("");
    setLoginPassword("");
    setLoginError("");
    setLoginOpen(true);
  }

  function closeLogin() {
    if (loginBusy) return;
    setLoginOpen(false);
    setLoginPassword("");
    setLoginError("");
  }

  async function handleIdentityClick() {
    if (authLoading || identityBusy) return;
    if (!authAvailable) { await refreshIdentity(); return; }
    if (auth?.role !== "admin") {
      if (auth?.login_configured) openLogin();
      else notify("管理员登录尚未配置。");
      return;
    }
    setIdentityBusy(true);
    try {
      await request("/api/auth/logout", { method: "POST" });
      window.location.reload();
    } catch (error) { notify(`退出失败：${error.message}`); }
    finally { setIdentityBusy(false); }
  }

  async function submitLogin(event) {
    event.preventDefault();
    if (loginBusy) return;
    setLoginBusy(true);
    setLoginError("");
    try {
      await request("/api/auth/login", jsonOptions("POST", { username: loginUsername, password: loginPassword }));
      window.location.reload();
    } catch (error) { setLoginError(error.message || "登录失败，请检查账号或密码。"); }
    finally { setLoginBusy(false); }
  }

  function loadBrowserModels(subject) {
    try {
      const savedProfiles = JSON.parse(localStorage.getItem(`yugan-rag-browser-models:${subject}`) || "[]");
      const selectedProfile = JSON.parse(localStorage.getItem(`yugan-rag-browser-model:${subject}`) || "null");
      const serverApiToken = sessionStorage.getItem(`yugan-rag-server-token:${subject}`) || "";
      const restoreProfile = (profile) => profile?.mode === "server"
        ? { ...profile, name: `服务器模型 · ${profile.model}`, vendor: "服务器模型", api_token: serverApiToken }
        : profile;
      const profiles = Array.isArray(savedProfiles) ? savedProfiles.filter((profile) => profile?.id && profile?.model && profile?.endpoint).map(restoreProfile) : [];
      const selected = restoreProfile(selectedProfile);
      setAgentModelProfiles(profiles);
      setBrowserModel(selected?.id && selected?.model ? selected : null);
      setSelectedAgentModelId(selected?.id || profiles[0]?.id || "");
    } catch {
      setAgentModelProfiles([]);
      setBrowserModel(null);
      setSelectedAgentModelId("");
    }
  }

  useEffect(() => {
    let live = true;
    request("/api/auth/status")
      .then((authData) => {
        if (!live) return;
        const identity = { ...authData, subject: authData.role === "admin" ? "admin" : authData.subject };
        setAuth(identity);
        setAuthAvailable(true);
        setAuthLoading(false);
        loadBrowserModels(identity.subject);
      })
      .catch((error) => { if (live) { setAuthAvailable(false); setAuthLoading(false); notify(`无法读取身份：${error.message}`); } });
    Promise.all([request("/api/projects"), request("/api/knowledge-bases"), request("/api/status"), request("/api/model-settings")])
      .then(([projectData, kbData, statusData, modelData]) => {
        setStatus(statusData);
        setModelSettings(modelData);
        setProjects(projectData);
        setKnowledgeBases(kbData);
        if (projectData.length) {
          const rememberedId = getRememberedProjectId();
          const selectedProject = projectData.find((project) => project.id === rememberedId) || projectData[0];
          setProjectId(selectedProject.id);
          rememberProjectId(selectedProject.id);
        }
        if (kbData.length) setActiveKbId(kbData[0].id);
      })
      .catch((error) => { if (live) notify(`后端连接失败：${error.message}`); });
    return () => { live = false; };
  }, []);

  const knowledgeLinkOpened = useRef(false);
  useEffect(() => {
    if (knowledgeLinkOpened.current || auth?.role !== "admin" || !knowledgeBases.length) return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("manage") !== "knowledge") return;
    const target = knowledgeBases.find((kb) => kb.id === params.get("knowledge_base_id") || kb.name === params.get("knowledge_base_name"));
    if (target) setActiveKbId(target.id);
    setManagerOpen(true);
    knowledgeLinkOpened.current = true;
  }, [knowledgeBases, auth?.role]);

  useEffect(() => {
    const onFocus = async () => {
      const previousRole = currentRoleRef.current;
      const identity = await refreshIdentity();
      if (previousRole && identity && previousRole !== identity.role) window.location.reload();
    };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, []);

  function openModelDialog() {
    setModelDialogOpen(true);
    setModelSettingsError("");
    if (!agentModelProfiles.length && !modelSyncing) void syncAgentModel();
  }

  async function refreshModelStatus() {
    try {
      const [statusData, modelData] = await Promise.all([request("/api/status"), request("/api/model-settings")]);
      setStatus(statusData);
      setModelSettings(modelData);
      setModelSettingsError("");
    } catch (error) { setModelSettingsError(`读取模型失败：${error.message}`); }
  }

  async function saveModelSettings() {
    if (modelSaving || auth?.role !== "admin") return;
    setModelSaving(true);
    try {
      const saved = await request("/api/model-settings", jsonOptions("PUT", { mode: "local", local_model: modelSettings.local_model }));
      const nextStatus = await request("/api/status");
      setModelSettings(saved);
      setStatus(nextStatus);
      setModelDialogOpen(false);
      notify(`RAG 回答模型已切换为 ${saved.local_model}。`);
    } catch (error) { setModelSettingsError(`保存失败：${error.message}`); }
    finally { setModelSaving(false); }
  }

  async function syncAgentModel() {
    if (modelSyncing || !auth) return;
    setModelSyncing(true);
    const nonce = uniqueId();
    const popupUrl = new URL("static/model-bridge.html", agentUrl);
    popupUrl.hash = nonce;
    const bridgeFrame = document.createElement("iframe");
    bridgeFrame.title = "Agent 模型配置共享";
    bridgeFrame.setAttribute("aria-hidden", "true");
    Object.assign(bridgeFrame.style, { position: "fixed", width: "1px", height: "1px", opacity: "0", pointerEvents: "none", border: "0", left: "-10000px", top: "0" });
    bridgeFrame.src = popupUrl.href;
    document.body.appendChild(bridgeFrame);
    const expectedOrigin = agentUrl.origin;
    let cancelled = false;
    let retryTimer;
    const finish = () => { cancelled = true; window.removeEventListener("message", receive); window.clearTimeout(timer); window.clearTimeout(retryTimer); bridgeFrame.remove(); setModelSyncing(false); };
    const receive = (event) => {
      if (event.source !== bridgeFrame.contentWindow || event.origin !== expectedOrigin || event.data?.nonce !== nonce) return;
      if (event.data?.type === "yugan-model-profiles-error") {
        const message = event.data.message || "读取 Agent 模型失败。";
        setModelSettingsError(message); notify(message); finish(); return;
      }
      if (event.data?.type !== "yugan-model-profiles") return;
      try {
        const browserProfiles = (Array.isArray(event.data.profiles) ? event.data.profiles : []).filter((profile) => {
          const localOrServer = profile?.mode === "local" || profile?.mode === "server";
          return Boolean(profile?.id && profile?.model && profile?.endpoint && (localOrServer || profile?.api_key));
        });
        const serverProfiles = (Array.isArray(event.data.server_models) ? event.data.server_models : [])
          .filter((name) => typeof name === "string" && name.trim())
          .map((name) => ({
            id: `server:${name}`, name: `服务器模型 · ${name}`, endpoint: "server-ollama://configured",
            model: name, api_key: "", api_token: event.data.server_api_token || "", vendor: "服务器模型", provider: "compatible", mode: "server", effort_supported: false,
          }));
        const profiles = [
          ...browserProfiles.filter((profile) => profile.mode !== "server"),
          ...serverProfiles,
        ];
        if (!profiles.length) throw new Error("Agent 中还没有可选择的模型。请先保存 API 模型，或在聊天模型菜单选择 Ollama。");
        if (event.data.server_api_token) sessionStorage.setItem(`yugan-rag-server-token:${auth.subject}`, event.data.server_api_token);
        else sessionStorage.removeItem(`yugan-rag-server-token:${auth.subject}`);
        setAgentModelProfiles(profiles);
        localStorage.setItem(`yugan-rag-browser-models:${auth.subject}`, JSON.stringify(profiles.map(({ api_token, ...profile }) => profile)));
        setSelectedAgentModelId((current) => profiles.some((profile) => profile.id === current) ? current : browserModel?.id && profiles.some((profile) => profile.id === browserModel.id) ? browserModel.id : profiles[0].id);
        setModelSettingsError("");
        notify(`已读取 ${profiles.length} 个个人 API 或 Ollama 模型。`);
      } catch (error) { setModelSettingsError(error.message); notify(error.message); }
      finish();
    };
    const timer = window.setTimeout(() => { finish(); setModelSettingsError("读取超时；请确认 Agent 页面已启动，并且 RAG 与 Agent 使用相同的主机地址（例如都用 127.0.0.1）。"); notify("读取 Agent 模型配置超时，请检查 Agent 页面和访问地址。"); }, 10000);
    window.addEventListener("message", receive);
    const sendRequest = () => {
      if (cancelled) return;
      try { bridgeFrame.contentWindow?.postMessage({ type: "yugan-request-model-profiles", nonce }, expectedOrigin); } catch { /* retry while the bridge frame loads */ }
      retryTimer = window.setTimeout(sendRequest, 250);
    };
    retryTimer = window.setTimeout(sendRequest, 250);
  }

  function saveSelectedAgentModel() {
    const profile = agentModelProfiles.find((item) => item.id === selectedAgentModelId);
    if (!profile || !auth) return;
    try {
      const { api_token, ...savedProfile } = profile;
      localStorage.setItem(`yugan-rag-browser-model:${auth.subject}`, JSON.stringify(savedProfile));
      setBrowserModel(profile);
      setModelDialogOpen(false);
      notify(profile.mode === "server" ? `RAG 已切换到服务器模型：${profile.name}。` : `RAG 已切换到：${profile.name}。`);
    } catch (error) { setModelSettingsError(`保存失败：${error.message}`); }
  }

  useEffect(() => {
    if (!projectId) return;
    let live = true;
    const sequence = ++projectRequestRef.current;
    setChatLoading(true);
    request(`/api/projects/${projectId}/chats`)
      .then((data) => {
        if (!live || sequence !== projectRequestRef.current) return;
        setChats(data);
        const next = data[0];
        setChatId(next?.id || "");
        setScopeMode(next?.scope_mode || "project");
        setSelectedKbIds(next?.knowledge_base_ids || []);
        if (!next) {
          setMessages([]);
          setScopeMode("project");
          setSelectedKbIds(projects.find((project) => project.id === projectId)?.knowledge_base_ids || []);
        }
      })
      .catch((error) => { if (live) notify(error.message); })
      .finally(() => { if (live && sequence === projectRequestRef.current) setChatLoading(false); });
    return () => { live = false; };
  }, [projectId]);

  useEffect(() => {
    const sequence = ++chatRequestRef.current;
    if (!chatId) { if (!generationRef.current) setMessages([]); return; }
    if (generationRef.current?.chatId === chatId) return;
    let live = true;
    setChatLoading(true);
    setMessages([]);
    request(`/api/chats/${chatId}`)
      .then((chat) => {
        if (!live || sequence !== chatRequestRef.current || generationRef.current?.chatId === chatId) return;
        setMessages(chat.messages || []);
        setSelectedKbIds(chat.knowledge_base_ids || []);
        setScopeMode(chat.scope_mode || "project");
      })
      .catch((error) => { if (live) notify(error.message); })
      .finally(() => { if (live && sequence === chatRequestRef.current) setChatLoading(false); });
    return () => { live = false; };
  }, [chatId]);

  useEffect(() => {
    if (!managerOpen || !activeKbId) return;
    refreshDocuments(activeKbId);
    return () => { documentRequestRef.current += 1; };
  }, [managerOpen, activeKbId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: busy ? "smooth" : "auto", block: "end" });
  }, [messages, busy]);

  useEffect(() => {
    function closeScope(event) {
      if (scopeRef.current && !scopeRef.current.contains(event.target)) setScopeOpen(false);
    }
    document.addEventListener("mousedown", closeScope);
    return () => document.removeEventListener("mousedown", closeScope);
  }, []);

  useEffect(() => {
    if (!brandMenuOpen) return undefined;
    function positionMenu() {
      const anchor = brandToggleRef.current?.getBoundingClientRect();
      if (!anchor) return;
      const width = Math.min(235, window.innerWidth - 16);
      const height = brandMenuRef.current?.offsetHeight || 238;
      setBrandMenuPosition({
        width: `${width}px`,
        left: `${Math.max(8, Math.min(anchor.left, window.innerWidth - width - 8))}px`,
        top: `${Math.max(8, Math.min(anchor.bottom + 8, window.innerHeight - height - 8))}px`,
      });
    }
    const frame = window.requestAnimationFrame(positionMenu);
    window.addEventListener("resize", positionMenu);
    document.addEventListener("scroll", positionMenu, true);
    document.addEventListener("transitionend", positionMenu);
    function closeOnOutsideClick(event) {
      if (!brandSwitchRef.current?.contains(event.target) && !brandMenuRef.current?.contains(event.target)) setBrandMenuOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") {
        setBrandMenuOpen(false);
        brandToggleRef.current?.focus();
      }
    }
    document.addEventListener("mousedown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
      window.cancelAnimationFrame(frame);
      window.removeEventListener("resize", positionMenu);
      document.removeEventListener("scroll", positionMenu, true);
      document.removeEventListener("transitionend", positionMenu);
    };
  }, [brandMenuOpen, sidebarCollapsed, mobileNav]);

  useEffect(() => {
    if (!sidebarMenu) return undefined;
    const menuElement = sidebarMenuRef.current;
    if (menuElement) {
      const rect = menuElement.getBoundingClientRect();
      menuElement.style.left = `${Math.max(8, Math.min(sidebarMenu.x, window.innerWidth - rect.width - 8))}px`;
      menuElement.style.top = `${Math.max(8, Math.min(sidebarMenu.y, window.innerHeight - rect.height - 8))}px`;
    }
    const closeOnOutsideClick = (event) => {
      if (!sidebarMenuRef.current?.contains(event.target)) setSidebarMenu(null);
    };
    const closeOnEscape = (event) => {
      if (event.key === "Escape") setSidebarMenu(null);
    };
    const close = () => setSidebarMenu(null);
    document.addEventListener("pointerdown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    window.addEventListener("resize", close);
    window.addEventListener("scroll", close, true);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
      window.removeEventListener("resize", close);
      window.removeEventListener("scroll", close, true);
    };
  }, [sidebarMenu]);

  async function selectProject(id) {
    if (busy) return;
    if (id === projectId) { setMobileNav(false); return; }
    setProjectId(id);
    rememberProjectId(id);
    currentProjectIdRef.current = id;
    currentChatIdRef.current = "";
    chatRequestRef.current += 1;
    setChatLoading(true);
    setChats([]);
    setChatId("");
    setMessages([]);
    setScopeMode("project");
    setSelectedKbIds(projects.find((project) => project.id === id)?.knowledge_base_ids || []);
    setMobileNav(false);
  }

  async function startChat() {
    if (!projectId || busy || chatLoading || scopeSaving) return;
    const targetProject = projectId;
    setChatLoading(true);
    try {
      const chat = await request(`/api/projects/${projectId}/chats`, jsonOptions("POST", { scope_mode: "project" }));
      if (currentProjectIdRef.current !== targetProject) return;
      setChats((items) => [chat, ...items]);
      setChatId(chat.id);
      setMessages([]);
      setSelectedKbIds(chat.knowledge_base_ids || currentProject?.knowledge_base_ids || []);
      setScopeMode("project");
      setMobileNav(false);
    } catch (error) { notify(error.message); }
    finally { if (currentProjectIdRef.current === targetProject) setChatLoading(false); }
  }

  async function selectChat(chat) {
    if (busy || scopeSaving || chat.id === chatId) return;
    chatRequestRef.current += 1;
    currentChatIdRef.current = chat.id;
    setChatLoading(true);
    setChatId(chat.id);
    setScopeMode(chat.scope_mode || "project");
    setSelectedKbIds(chat.knowledge_base_ids || []);
    setMessages([]);
    setMobileNav(false);
    setScopeOpen(false);
  }

  async function removeChat(chat, event) {
    event?.stopPropagation();
    if (busy || chatLoading || scopeSaving) return;
    setDeleteChatTarget(chat);
  }

  async function confirmRemoveChat() {
    if (!deleteChatTarget || deleteChatSaving) return;
    const chat = deleteChatTarget;
    setDeleteChatSaving(true);
    try {
      await request(`/api/chats/${chat.id}`, { method: "DELETE" });
      const remaining = chats.filter((item) => item.id !== chat.id);
      setChats(remaining);
      if (chatId === chat.id) {
        setChatId(remaining[0]?.id || "");
        if (!remaining.length) setMessages([]);
      }
      setDeleteChatTarget(null);
      notify("对话已删除");
    } catch (error) { notify(error.message); }
    finally { setDeleteChatSaving(false); }
  }

  function openSidebarMenu(event, type, item) {
    event.preventDefault();
    if (type === "project" && auth?.role !== "admin") return;
    if (busy || chatLoading || scopeSaving || projectSaving) return;
    const anchor = event.currentTarget?.getBoundingClientRect?.() || event.target?.closest?.(".conversation-item, .project-item")?.getBoundingClientRect?.();
    const pointerX = Number.isFinite(event.clientX) && event.clientX > 0 ? event.clientX : anchor?.right - 8 || 8;
    const pointerY = Number.isFinite(event.clientY) && event.clientY > 0 ? event.clientY : anchor?.top + 8 || 8;
    setSidebarMenu({
      type,
      id: item.id,
      name: type === "project" ? item.name : item.title,
      x: Math.max(8, Math.min(pointerX, window.innerWidth - 176)),
      y: Math.max(8, Math.min(pointerY, window.innerHeight - 90)),
    });
  }

  function openRenameFromMenu() {
    if (!sidebarMenu) return;
    setRenameTarget(sidebarMenu);
    setRenameValue(sidebarMenu.name);
    setSidebarMenu(null);
  }

  async function saveRename(event) {
    event.preventDefault();
    if (!renameTarget || renameSaving) return;
    const name = renameValue.trim();
    if (!name) return;
    if (name === renameTarget.name) { setRenameTarget(null); return; }
    setRenameSaving(true);
    try {
      if (renameTarget.type === "project") {
        const updated = await request(`/api/projects/${renameTarget.id}`, jsonOptions("PATCH", { name }));
        setProjects((items) => items.map((item) => item.id === updated.id ? updated : item));
      } else {
        const updated = await request(`/api/chats/${renameTarget.id}`, jsonOptions("PATCH", { title: name }));
        setChats((items) => items.map((item) => item.id === updated.id ? { ...item, ...updated } : item));
      }
      setRenameTarget(null);
      notify("名称已更新");
    } catch (error) { notify(error.message); }
    finally { setRenameSaving(false); }
  }

  function removeProject(project) {
    if (auth?.role !== "admin") { notify("游客不能删除项目。"); return; }
    if (busy || chatLoading || scopeSaving || projectSaving || deleteProjectSaving) return;
    setDeleteProjectTarget(project);
  }

  async function confirmRemoveProject() {
    if (!deleteProjectTarget || deleteProjectSaving) return;
    const project = deleteProjectTarget;
    setDeleteProjectSaving(true);
    try {
      await request(`/api/projects/${project.id}`, { method: "DELETE" });
      const remaining = projects.filter((item) => item.id !== project.id);
      setProjects(remaining);
      if (projectId === project.id) {
        const next = remaining[0];
        currentProjectIdRef.current = next?.id || "";
        currentChatIdRef.current = "";
        projectRequestRef.current += 1;
        chatRequestRef.current += 1;
        setProjectId(next?.id || "");
        rememberProjectId(next?.id || "");
        setChats([]);
        setChatId("");
        setMessages([]);
        setScopeMode("project");
        setSelectedKbIds(next?.knowledge_base_ids || []);
      }
      setDeleteProjectTarget(null);
      notify("项目已删除，知识库资料已保留");
    } catch (error) { notify(error.message); }
    finally { setDeleteProjectSaving(false); }
  }

  function openProjectDialog(edit = false) {
    if (auth?.role !== "admin") { notify("游客不能新建或修改项目。"); return; }
    setEditingProject(edit);
    setProjectName(edit ? currentProject?.name || "" : "");
    setProjectKbIds(edit ? currentProject?.knowledge_base_ids || [] : []);
    setProjectDialog(true);
  }

  async function saveProject(event) {
    event.preventDefault();
    if (auth?.role !== "admin") { notify("游客不能新建或修改项目。"); return; }
    setProjectSaving(true);
    try {
      if (editingProject) {
        const updated = await request(`/api/projects/${projectId}`, jsonOptions("PATCH", { name: projectName, knowledge_base_ids: projectKbIds }));
        setProjects((items) => items.map((item) => item.id === projectId ? updated : item));
        if (activeScopeMode === "project") setSelectedKbIds(updated.knowledge_base_ids || []);
        notify("项目自动范围已同步；自定义范围的对话保持原设置");
      } else {
        const created = await request("/api/projects", jsonOptions("POST", { name: projectName, knowledge_base_ids: projectKbIds }));
        setProjects((items) => [...items, created]);
        setChats([]);
        setChatId("");
        setMessages([]);
        setScopeMode("project");
        setProjectId(created.id);
        rememberProjectId(created.id);
        notify("项目已创建");
      }
      setProjectDialog(false);
    } catch (error) { notify(error.message); }
    finally { setProjectSaving(false); }
  }

  async function saveScope(mode, ids = selectedKbIds) {
    if (busy || chatLoading || scopeSaving) return;
    const previousMode = activeScopeMode;
    const previousIds = selectedKbIds;
    const targetProjectId = projectId;
    const targetChatId = chatId;
    setScopeMode(mode);
    if (mode === "custom") setSelectedKbIds(ids);
    setScopeSaving(true);
    const sequence = ++scopeSequenceRef.current;

    if (!targetChatId) {
      try {
        if (mode === "project") {
          setSelectedKbIds(currentProject?.knowledge_base_ids || []);
        } else {
          // 还没有对话时，把选择保存为当前项目的默认检索范围，刷新后仍然保留。
          const updatedProject = await request(
            `/api/projects/${targetProjectId}`,
            jsonOptions("PATCH", { knowledge_base_ids: ids }),
          );
          if (sequence !== scopeSequenceRef.current || targetProjectId !== currentProjectIdRef.current) return;
          setProjects((items) => items.map((item) => item.id === targetProjectId ? updatedProject : item));
          setScopeMode("project");
          setSelectedKbIds(updatedProject.knowledge_base_ids || ids);
          notify("已保存为项目默认知识库范围");
        }
      } catch (error) {
        if (sequence === scopeSequenceRef.current && targetProjectId === currentProjectIdRef.current) {
          setScopeMode(previousMode);
          setSelectedKbIds(previousIds);
          notify(error.message);
        }
      } finally {
        if (sequence === scopeSequenceRef.current) setScopeSaving(false);
      }
      return;
    }

    const body = mode === "project" ? { scope_mode: "project" } : { scope_mode: "custom", knowledge_base_ids: ids };
    const saveRequest = scopeQueueRef.current.catch(() => {}).then(() => request(`/api/chats/${targetChatId}`, jsonOptions("PATCH", body)));
    scopeQueueRef.current = saveRequest;
    try {
      const updated = await saveRequest;
      if (sequence !== scopeSequenceRef.current || targetChatId !== currentChatIdRef.current) return;
      setScopeMode(updated.scope_mode || mode);
      setSelectedKbIds(updated.knowledge_base_ids || (mode === "project" ? currentProject?.knowledge_base_ids || [] : ids));
      setChats((items) => items.map((item) => item.id === targetChatId ? { ...item, ...updated } : item));
    } catch (error) {
      if (sequence === scopeSequenceRef.current && targetChatId === currentChatIdRef.current) {
        setScopeMode(previousMode);
        setSelectedKbIds(previousIds);
        notify(error.message);
      }
    } finally { if (sequence === scopeSequenceRef.current) setScopeSaving(false); }
  }

  async function sendMessage(event) {
    event?.preventDefault();
    const content = input.trim();
    if (!content || busy || chatLoading || scopeSaving || !projectId) return;
    setInput("");
    setBusy(true);
    const requestId = uniqueId();
    const assistantId = `pending-${requestId}`;
    const executionStartedAt = Date.now();
    const identity = { id: requestId, projectId, chatId };
    generationRef.current = identity;
    chatRequestRef.current += 1;
    const updateStep = (step) => {
      if (generationRef.current?.id !== requestId) return;
      setMessages((items) => items.map((message) => {
        if (message.id !== assistantId) return message;
        const steps = [...(message.execution_steps || [])];
        const index = steps.findIndex((item) => item.id === step.id);
        const updated = { ...step, started_at: index >= 0 ? steps[index].started_at : Date.now() };
        if (index < 0) steps.push(updated); else steps[index] = updated;
        return { ...message, execution_steps: steps };
      }));
    };
    setMessages((items) => [...items,
      { id: `user-${requestId}`, role: "user", content, sources: [] },
      { id: assistantId, role: "assistant", content: "", sources: [], streaming: true, executionStartedAt, processOpen: true,
        execution_steps: [{ id: "dispatch", agent: "coordinator", label: "调度", stage: "scheduling", status: "running",
          detail: "正在准备本轮对话与检索范围…", duration_ms: 0, started_at: executionStartedAt }] },
    ]);
    let activeChatId = chatId;
    try {
      if (!activeChatId) {
        const created = await request(`/api/projects/${projectId}/chats`, jsonOptions("POST", { scope_mode: "project" }));
        activeChatId = created.id;
        identity.chatId = created.id;
        setChatId(created.id);
        setChats((items) => [created, ...items]);
        setScopeMode("project");
        setSelectedKbIds(created.knowledge_base_ids || currentProject?.knowledge_base_ids || []);
        if (scopeMode === "custom") {
          const updated = await request(`/api/chats/${created.id}`, jsonOptions("PATCH", { scope_mode: "custom", knowledge_base_ids: selectedKbIds }));
          setChats((items) => items.map((item) => item.id === created.id ? { ...item, ...updated } : item));
          setScopeMode("custom");
          setSelectedKbIds(updated.knowledge_base_ids || selectedKbIds);
        }
      }
      if (generationRef.current?.id !== requestId) return;
      await scopeQueueRef.current;
      if (browserModel) {
        const result = await runBrowserRag({
          profile: browserModel, chatId: activeChatId, question: content,
          history: messages.filter((item) => ["user", "assistant"].includes(item.role)),
          knowledgeBases: selectedKbs, customIds: scopeMode === "custom" ? selectedKbIds : null,
          callModel: requestBrowserModel, onStep: updateStep,
        });
        if (generationRef.current?.id === requestId) {
          setMessages((items) => items.map((message) => message.id === assistantId ? {
            ...message, content: result.content, sources: result.sources, streaming: false,
            execution_steps: result.execution_steps, execution_elapsed_ms: result.execution_elapsed_ms,
          } : message));
        }
        const refreshed = await request(`/api/projects/${projectId}/chats`);
        if (generationRef.current?.id === requestId) setChats(refreshed);
        return;
      }
      const response = await fetch(`${API}/api/chats/${activeChatId}/messages/stream`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, ...(scopeMode === "custom" ? { knowledge_base_ids: selectedKbIds } : {}) }),
      });
      if (!response.ok) {
        let detail = `请求失败（${response.status}）`;
        try { detail = (await response.json()).detail || detail; } catch { /* use the HTTP status */ }
        throw new Error(detail);
      }
      if (!response.body) throw new Error("浏览器不支持实时响应");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let streamedAnswer = "";
      let finalAnswer = null;
      let finalSources = [];
      let finalSteps = null;
      let finalElapsed = 0;
      const handleEvent = (block) => {
        const line = block.split("\n").find((item) => item.startsWith("data: "));
        if (!line) return;
        const update = JSON.parse(line.slice(6));
        if (update.type === "progress") { updateStep(update.step); return; }
        if (update.type === "error") {
          if (Array.isArray(update.execution_steps)) update.execution_steps.forEach(updateStep);
          throw new Error(update.message || "回答生成失败");
        }
        if (update.type === "token") {
          streamedAnswer += update.content || "";
          if (generationRef.current?.id === requestId) setMessages((items) => items.map((message) => message.id === assistantId ? { ...message, content: streamedAnswer } : message));
        } else if (update.type === "sources") {
          finalSources = update.sources || [];
        } else if (update.type === "done") {
          finalAnswer = update.answer || streamedAnswer;
          finalSources = update.sources || finalSources;
          finalSteps = update.execution_steps || null;
          finalElapsed = update.execution_elapsed_ms || 0;
        }
      };
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer = (buffer + decoder.decode(value, { stream: true })).replaceAll("\r\n", "\n");
        let boundary;
        while ((boundary = buffer.indexOf("\n\n")) >= 0) {
          handleEvent(buffer.slice(0, boundary));
          buffer = buffer.slice(boundary + 2);
        }
      }
      if (buffer.trim()) handleEvent(buffer);
      if (finalAnswer === null) throw new Error("实时连接中断，未收到回答结果");
      if (generationRef.current?.id === requestId) setMessages((items) => items.map((message) => message.id === assistantId ? {
        ...message, content: finalAnswer, sources: finalSources, streaming: false,
        execution_steps: finalSteps || message.execution_steps, execution_elapsed_ms: finalElapsed || Date.now() - executionStartedAt,
      } : message));
      const refreshed = await request(`/api/projects/${projectId}/chats`);
      if (generationRef.current?.id === requestId) setChats(refreshed);
    } catch (error) {
      if (generationRef.current?.id === requestId) {
        setInput(content);
        notify(error.message);
        setMessages((items) => items.map((message) => message.id === assistantId ? {
          ...message, content: `${message.content}${message.content ? "\n\n" : ""}出错了：${error.message}`, error: true, streaming: false,
          execution_elapsed_ms: Date.now() - executionStartedAt,
          execution_steps: (message.execution_steps || []).map((step) => step.status === "running" ? {
            ...step, status: "error", detail: "处理失败，请检查当前模型与知识库服务后重试。", duration_ms: Date.now() - (step.started_at || executionStartedAt),
          } : step),
        } : message));
      }
    } finally {
      if (generationRef.current?.id === requestId) {
        generationRef.current = null;
        setBusy(false);
      }
    }
  }

  async function addKnowledgeBase(event) {
    event.preventDefault();
    if (auth?.role !== "admin") { notify("游客不能新建知识库。"); return; }
    try {
      const created = await request("/api/knowledge-bases", jsonOptions("POST", { name: kbName, description: kbDescription }));
      const all = await refreshKnowledgeBases();
      const next = [...all.filter((item) => item.id !== created.id), created];
      setKnowledgeBases(next);
      setActiveKbId(created.id);
      setDocuments([]);
      setKbName("");
      setKbDescription("");
      setShowKbForm(false);
      notify("知识库已创建，可继续添加资料");
    } catch (error) { notify(error.message); }
  }

  async function refreshDocuments(kbId) {
    const sequence = ++documentRequestRef.current;
    setDocumentsLoading(true);
    setDocumentsError("");
    setDocuments([]);
    try {
      const data = await request(`/api/knowledge-bases/${kbId}/documents`);
      if (sequence === documentRequestRef.current && kbId === currentKbIdRef.current) setDocuments(data);
    } catch (error) {
      if (sequence === documentRequestRef.current && kbId === currentKbIdRef.current) setDocumentsError(error.message);
    } finally {
      if (sequence === documentRequestRef.current) setDocumentsLoading(false);
    }
  }

  // 保存真实的 File 对象，点击选择与拖放统一进入同一条上传队列。
  function queueFiles(files, preferredKbId = "") {
    if (auth?.role !== "admin") { notify("游客不能向知识库添加文件。"); return; }
    if (!files.length) return;
    if (uploadRunningRef.current) { notify("正在导入资料，请等待当前队列完成后再添加。"); return; }
    const additions = files.map((file) => {
      const validType = /\.(pdf|docx|txt|md|csv)$/i.test(file.name);
      const error = !validType ? "格式不支持，请上传 PDF、DOCX、TXT、MD 或 CSV。" : file.size > 30 * 1024 * 1024 ? "文件超过 30 MB，请缩小后重新选择。" : "";
      return { id: uniqueId(), file, status: error ? "invalid" : "pending", error, chunkCount: null, targetKbId: "" };
    });
    setUploadQueue((items) => uploadDialogOpen ? [...items, ...additions] : additions);
    if (!uploadDialogOpen) setUploadTargetKbId(preferredKbId || activeScopeIds[0] || activeKbId || knowledgeBases[0]?.id || "");
    setUploadDialogOpen(true);
    setDragActive(false);
    dragDepthRef.current = 0;
  }

  function handleDrop(event, preferredKbId = "") {
    if (!transferHasFiles(event)) return;
    event.preventDefault();
    event.stopPropagation();
    if (auth?.role !== "admin") { notify("游客不能向知识库添加文件。"); return; }
    queueFiles(filesFromTransfer(event), preferredKbId);
    setDragActive(false);
    dragDepthRef.current = 0;
  }

  async function runUploadQueue(retryId = "") {
    if (auth?.role !== "admin") { notify("游客不能向知识库添加文件。"); return; }
    if (uploadRunningRef.current || !uploadTargetKbId) return;
    const targetKbId = uploadTargetKbId;
    const pending = uploadQueue.filter((item) => retryId ? item.id === retryId && item.status === "error" : item.status === "pending" || item.status === "error");
    if (!pending.length) return;
    uploadRunningRef.current = true;
    setUploading(true);
    const updateItem = (id, updates) => setUploadQueue((items) => items.map((item) => item.id === id ? { ...item, ...updates } : item));
    let completed = 0;
    try {
      for (const item of pending) {
        updateItem(item.id, { status: "uploading", error: "", targetKbId });
        try {
          const form = new FormData();
          form.append("files", item.file);
          const result = await request(`/api/knowledge-bases/${targetKbId}/documents`, { method: "POST", body: form });
          const document = result.uploaded?.[0];
          if (!document) throw new Error("服务器没有返回导入结果，请在知识库中确认文件状态。");
          updateItem(item.id, { status: "done", chunkCount: document.chunk_count, documentId: document.id });
          completed += 1;
        } catch (error) { updateItem(item.id, { status: "error", error: error.message }); }
      }
      await refreshKnowledgeBases();
      if (currentKbIdRef.current === targetKbId) await refreshDocuments(targetKbId);
      notify(completed ? `已导入 ${completed} 份资料，后续提问会自动检索。` : "导入未完成，请查看每个文件下的原因并重试。");
    } catch (error) { notify(`资料已处理，但列表刷新失败：${error.message}`); }
    finally { uploadRunningRef.current = false; setUploading(false); }
  }

  function closeChunks() {
    chunkRequestRef.current += 1;
    setChunkDocument(null);
    setChunks([]);
    setChunksLoading(false);
  }

  async function loadChunks(document, offset = 0) {
    const sequence = ++chunkRequestRef.current;
    setChunkDocument(document);
    setChunks([]);
    setChunkOffset(offset);
    setChunksLoading(true);
    setChunksError("");
    try {
      const data = await request(`/api/knowledge-bases/${document.knowledge_base_id}/documents/${document.id}/chunks?offset=${offset}&limit=20`);
      if (sequence !== chunkRequestRef.current) return;
      setChunks(data.items || []);
      setChunkTotal(data.total || 0);
    } catch (error) { if (sequence === chunkRequestRef.current) setChunksError(error.message); }
    finally { if (sequence === chunkRequestRef.current) setChunksLoading(false); }
  }

  async function removeChunk(chunk) {
    if (auth?.role !== "admin") { notify("游客不能删除知识库分片。"); return; }
    if (deletingChunkId || !chunkDocument) return;
    if (!window.confirm(`删除分片 ${chunk.index}？之后的检索不会再使用这段内容，原始文件保留。`)) return;
    const document = chunkDocument;
    setDeletingChunkId(chunk.id);
    try {
      const result = await request(`/api/knowledge-bases/${document.knowledge_base_id}/documents/${document.id}/chunks/${encodeURIComponent(chunk.id)}`, { method: "DELETE" });
      const remaining = result.remaining_chunks;
      setDocuments((items) => items.map((item) => item.id === document.id ? { ...item, chunk_count: remaining } : item));
      const offset = remaining > 0 ? Math.min(chunkOffset, Math.floor((remaining - 1) / 20) * 20) : 0;
      await loadChunks({ ...document, chunk_count: remaining }, offset);
      await refreshKnowledgeBases();
      notify("分片已删除，后续提问不会再检索到它。");
    } catch (error) { notify(error.message); }
    finally { setDeletingChunkId(""); }
  }

  async function removeDocument(document) {
    if (auth?.role !== "admin") { notify("游客不能删除知识库文件。"); return; }
    if (!window.confirm(`从知识库中删除“${document.filename}”？`)) return;
    try {
      await request(`/api/knowledge-bases/${activeKbId}/documents/${document.id}`, { method: "DELETE" });
      setDocuments((items) => items.filter((item) => item.id !== document.id));
      await refreshKnowledgeBases();
      notify("资料和对应的向量片段已删除");
    } catch (error) { notify(error.message); }
  }

  async function removeKnowledgeBase(kb) {
    if (auth?.role !== "admin") { notify("游客不能删除知识库。"); return; }
    if (uploading || busy || deleteKbSaving) return;
    setDeleteKbTarget(kb);
  }

  async function confirmRemoveKnowledgeBase() {
    if (!deleteKbTarget || deleteKbSaving || uploading || busy) return;
    const kb = deleteKbTarget;
    setDeleteKbSaving(true);
    try {
      await request(`/api/knowledge-bases/${kb.id}`, { method: "DELETE" });
      const next = await refreshKnowledgeBases();
      setProjects(await request("/api/projects"));
      setChats((items) => items.map((chat) => ({ ...chat, knowledge_base_ids: (chat.knowledge_base_ids || []).filter((id) => id !== kb.id) })));
      setSelectedKbIds((ids) => ids.filter((id) => id !== kb.id));
      setActiveKbId(next[0]?.id || "");
      setDeleteKbTarget(null);
      notify("知识库已删除");
    } catch (error) { notify(error.message); }
    finally { setDeleteKbSaving(false); }
  }

  return (
    <div className={`app-shell app-shell--commerce ${sidebarCollapsed && !smallViewport ? "sidebar-collapsed" : ""}`}
      onDragenter={(event) => { if (auth?.role === "admin" && transferHasFiles(event)) { event.preventDefault(); dragDepthRef.current += 1; setDragActive(true); } }}
      onDragover={(event) => { if (auth?.role === "admin" && transferHasFiles(event)) { event.preventDefault(); event.dataTransfer.dropEffect = uploading ? "none" : "copy"; } }}
      onDragleave={(event) => { if (auth?.role === "admin" && transferHasFiles(event)) { dragDepthRef.current = Math.max(0, dragDepthRef.current - 1); if (!dragDepthRef.current) setDragActive(false); } }}
      onDrop={(event) => handleDrop(event, managerOpen ? activeKbId : "")}>
      <input ref={fileRef} type="file" multiple accept=".pdf,.docx,.txt,.md,.csv" onInput={(event) => { queueFiles(Array.from(event.target.files || []), managerOpen ? activeKbId : ""); event.target.value = ""; }} hidden />
      {dragActive && auth?.role === "admin" && <div className="file-drag-overlay"><Upload size={36} /><strong>{uploading ? "正在导入，请稍候" : "松开文件，选择知识库导入"}</strong><span>支持多个 PDF、DOCX、TXT、MD 和 CSV 文件</span></div>}
      {mobileNav && <button className="mobile-scrim" aria-label="关闭侧边栏" onClick={() => setMobileNav(false)} />}
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-switcher" ref={brandSwitchRef}>
            <button ref={brandToggleRef} className="brand-logo brand-switcher-toggle" type="button" aria-label="打开项目菜单" aria-expanded={brandMenuOpen} aria-controls="brand-switcher-menu" onClick={() => setBrandMenuOpen((value) => !value)}><Menu size={20} /></button>
            <Teleport to="body"><nav ref={brandMenuRef} id="brand-switcher-menu" className="brand-switcher-menu" style={brandMenuPosition} aria-label="项目入口" hidden={!brandMenuOpen}>
              <span className="brand-switcher-heading">项目入口</span>
              <a className="brand-switcher-link" href={ecommerceUrl.href}>电商分析平台 <span aria-hidden="true">→</span></a>
              <a className="brand-switcher-link" href="http://127.0.0.1:3000/tickets">售后工单系统 <span aria-hidden="true">→</span></a>
              <a className="brand-switcher-link" href={agentUrl.href}>Agent 控制台 <span aria-hidden="true">→</span></a>
              <span className="brand-switcher-current">RAG 知识库 <small>当前页面</small></span>
              <a className="brand-switcher-link" href={projectHomeUrl.href}>项目主页 <span aria-hidden="true">→</span></a>
            </nav></Teleport>
          </div>
          <div className="brand-copy"><strong>RAG 知识库</strong><span>知答 · 本地知识助手</span></div>
          <button className="icon-button mobile-close" aria-label="关闭菜单" onClick={() => setMobileNav(false)}><X size={17} /></button>
        </div>
        <button className="new-chat-button" title="新建对话" aria-label="新建对话" onClick={startChat} disabled={busy || chatLoading || scopeSaving || !projectId}><Plus size={17} /><span>新建对话</span></button>
        <div className="sidebar-section project-section">
          <div className="sidebar-label project-section-heading">
            <button type="button" className="project-section-toggle" title={projectSpaceCollapsed ? "展开项目空间" : "收起项目空间"} aria-label={projectSpaceCollapsed ? "展开项目空间" : "收起项目空间"} aria-expanded={!projectSpaceCollapsed} aria-controls="rag-project-space" onClick={toggleProjectSpace}><span>项目空间</span><ChevronDown size={14} class={projectSpaceCollapsed ? "" : "is-open"} /></button>
            {auth?.role === "admin" && <button type="button" className="project-section-add" title="新建项目" aria-label="新建项目" onClick={() => openProjectDialog(false)}><Plus size={15} /></button>}
          </div>
          <div className="project-list" id="rag-project-space" hidden={projectSpaceCollapsed}>
            {projects.map((project) => <button key={project.id} title={project.name} aria-label={project.name} className={`project-item ${project.id === projectId ? "selected" : ""}`} onClick={() => selectProject(project.id)} onContextmenu={(event) => openSidebarMenu(event, "project", project)} onKeydown={(event) => { if (event.key === "ContextMenu" || (event.shiftKey && event.key === "F10")) openSidebarMenu(event, "project", project); }}>
              <span className="project-icon"><FolderKanban size={16} /></span><span className="project-name">{project.name}</span><span className="project-count">{project.knowledge_base_ids?.length || 0}</span>
            </button>)}
          </div>
        </div>
        <div className="sidebar-section conversation-section">
          <div className="sidebar-label"><span>最近对话</span><span className="conversation-count">{chats.length}</span></div>
          <div className="conversation-list">
            {chats.map((chat) => <button key={chat.id} title={chat.title} aria-label={chat.title} className={`conversation-item ${chat.id === chatId ? "active" : ""}`} onClick={() => selectChat(chat)} onContextmenu={(event) => openSidebarMenu(event, "chat", chat)} onKeydown={(event) => { if (event.key === "ContextMenu" || (event.shiftKey && event.key === "F10")) openSidebarMenu(event, "chat", chat); }}>
              <MessageSquare size={15} /><span>{chat.title}</span><i className="delete-chat" role="button" aria-label="删除对话" onClick={(event) => removeChat(chat, event)}><Trash2 size={13} /></i>
            </button>)}
            {!chats.length && <p className="sidebar-empty">还没有对话，点击上方开始。</p>}
          </div>
        </div>
        <div className="sidebar-bottom">
          <button className="manage-link" title="管理知识库" aria-label="管理知识库" onClick={() => { setManagerOpen(true); setShowKbForm(false); }}><BookOpen size={16} /><span>管理知识库</span><ChevronRight size={15} /></button>
          <button type="button" className={`model-status ${browserModel || status?.ollama_connected ? "online" : "offline"}`} onClick={openModelDialog} title="查看并切换 RAG 回答模型">
            <span className="status-dot" />
            <div><strong>{browserModel ? "当前回答模型" : status?.ollama_connected ? "RAG 回答模型" : "等待 Ollama"}</strong><small>{browserModel ? (browserModel.mode === "server" ? `服务器模型 · ${browserModel.model}` : browserModel.name) : (status?.ollama_connected ? modelSettings.local_model || status.chat_model : "检查本地模型服务")}</small></div>
            <Settings2 size={15} />
          </button>
          <div className="privacy-note"><ShieldCheck size={14} />资料保存在本机</div>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="topbar-title">
            <button className="icon-button sidebar-toggle" type="button" aria-label={smallViewport ? (mobileNav ? "收起侧栏" : "展开侧栏") : sidebarCollapsed ? "展开侧栏" : "收起侧栏"} aria-expanded={smallViewport ? mobileNav : !sidebarCollapsed} onClick={toggleSidebar}><PanelLeftClose size={18} /></button>
            <div className="breadcrumb"><a href={projectHomeUrl.href}>首页</a><span className="breadcrumb-divider">/</span><span>RAG 知识库</span><span className="breadcrumb-divider">/</span><span>{currentProject?.name || "项目空间"}</span><ChevronRight size={14} /><strong>{currentChat?.title || "新对话"}</strong></div>
            <div className="topbar-subtitle"><span className="tiny-live" />每轮自动检索{activeScopeMode === "project" ? "项目关联的" : "自定义的"}知识库</div>
          </div>
          <div className="topbar-actions">
            <button type="button" className={`identity-control-button ${auth?.role === "admin" ? "identity-admin" : ""} ${!authAvailable && !authLoading ? "identity-unavailable" : ""}`} aria-live="polite" disabled={authLoading || identityBusy} onClick={handleIdentityClick}>
              {authLoading ? "正在读取身份…" : !authAvailable ? "身份状态未知 · 重试" : `${auth?.role === "admin" ? "服务器管理员" : "游客"} · ${auth?.role === "admin" ? "退出" : "登录"}`}
            </button>
            <div className="scope-wrap" ref={scopeRef}>
              <button className={`scope-button ${scopeOpen ? "is-open" : ""}`} onClick={() => setScopeOpen((value) => !value)}>
                <Layers3 size={15} /><span>{activeScopeMode === "project" ? "自动检索" : "自定义范围"}</span><b>{selectedKbs.length}</b><ChevronDown size={14} />
              </button>
              {scopeOpen && <div className="scope-menu">
                <div className="scope-menu-head"><strong>每轮自动检索资料</strong><small>{scopeSaving ? "正在保存范围…" : chatId ? "默认跟随项目；也可为这段对话单独选择。" : "当前还没有对话，选择后会保存为项目默认范围。"}</small></div>
                <div className="scope-mode-options">
                  <button disabled={busy || chatLoading || scopeSaving} className={activeScopeMode === "project" ? "active" : ""} onClick={() => saveScope("project")}><FolderKanban size={13} />跟随项目</button>
                  <button disabled={busy || chatLoading || scopeSaving} className={activeScopeMode === "custom" ? "active" : ""} onClick={() => saveScope("custom", activeScopeIds)}><Settings2 size={13} />单独选择</button>
                </div>
                {knowledgeBases.map((kb) => <label className="scope-option" key={kb.id}>
                  <input type="checkbox" disabled={busy || chatLoading || scopeSaving} checked={activeScopeIds.includes(kb.id)} onInput={(event) => saveScope("custom", event.target.checked ? [...activeScopeIds, kb.id] : activeScopeIds.filter((id) => id !== kb.id))} />
                  <span className="scope-option-icon"><BookOpen size={14} /></span><span><b>{kb.name}</b><small>{kb.document_count || 0} 份资料</small></span>
                </label>)}
                {!knowledgeBases.length && <p className="empty-small">先创建一个知识库</p>}
              </div>}
            </div>
            <a className="manage-top-button home-top-link" href={projectHomeUrl.href} aria-label="返回项目主页"><Home size={16} /><span>返回主页</span></a>
            {auth?.role === "admin" && <button className="settings-top-button" title="项目设置" disabled={!projectId || busy} onClick={() => openProjectDialog(true)}><Settings2 size={17} /><span>设置</span></button>}
          </div>
        </header>
        <nav className="workspace-tabs" aria-label="知识库功能">
          <span className="workspace-tab active" aria-current="page"><i />知识库问答</span>
          <button className="workspace-tab" type="button" onClick={() => { setManagerOpen(true); setShowKbForm(false); }}>知识库管理</button>
          <span className="workspace-current-project">当前项目：{currentProject?.name || "加载中"}</span>
        </nav>

        {status?.ollama_connected === false && <div className="connection-banner"><CircleHelp size={16} /><span>知识检索服务暂不可用，请检查 RAG 服务端的向量模型配置。</span></div>}

        <section className="chat-area">
          {chatLoading ? <div className="loading-state"><span className="spinner" />正在读取对话…</div> : messages.length === 0 ? <div className="welcome-screen">
            <section className="workspace-welcome-card">
              <div className="welcome-heading"><span className="workspace-title-icon"><MessageSquare size={21} /></span><div><h1>知识库问答</h1><p>检索项目资料，结合来源生成回答。</p></div></div>
              <button className="quiet-button" type="button" onClick={() => { setManagerOpen(true); setShowKbForm(false); }}><BookOpen size={15} />管理知识库</button>
            </section>
            <div className="knowledge-overview" aria-label="当前项目资料概况">
              <div className="overview-card"><span>检索知识库</span><strong>{projectId ? selectedKbs.length : "—"}</strong><small>{activeScopeMode === "project" ? "跟随项目自动检索" : "当前对话自定义范围"}</small></div>
              <div className="overview-card"><span>可检索资料</span><strong>{projectId ? selectedKbs.reduce((count, kb) => count + Number(kb.document_count || 0), 0) : "—"}</strong><small>当前检索范围内的文件数量</small></div>
              <div className="overview-card"><span>最近会话</span><strong>{projectId ? chats.length : "—"}</strong><small>当前项目已保存的历史对话</small></div>
            </div>
            <section className="welcome-question-card">
              <div className="workspace-section-heading"><h2>开始知识检索</h2><span><i className="tiny-live" />每轮自动检索</span></div>
              <p className="welcome-copy">在 <b>{currentProject?.name || "当前项目"}</b> 中向多个知识库提问。每轮会自动检索关联资料，并显示来源。</p>
              <div className="active-kb-row">
                {selectedKbs.slice(0, 4).map((kb) => <span className="kb-chip" key={kb.id}><BookOpen size={13} />{kb.name}</span>)}
                {!selectedKbs.length && <button className="empty-scope-chip" onClick={() => setScopeOpen(true)}>选择一个知识库</button>}
                <button className="add-scope-chip" title="调整检索知识库" aria-label="调整检索知识库" onClick={() => { setScopeOpen(true); }}><Plus size={13} /></button>
              </div>
              {auth?.role === "admin" && <button className="welcome-upload" disabled={uploading} onClick={() => fileRef.current?.click()}><Upload size={20} /><span>拖入资料或点击上传<small>支持 PDF、DOCX、TXT、Markdown 和 CSV，导入后自动建立索引</small></span></button>}
            </section>
          </div> : <div className="messages-list">
            {messages.map((message) => <article key={message.id} className={`message-row ${message.role === "user" ? "user-row" : "assistant-row"}`}>
              <div className={`message-avatar ${message.role}`}>
                {message.role === "user" ? <img src="default-user-avatar.svg" alt="" /> : <Bot size={17} />}
              </div>
              <div className="message-body">
                {message.role === "assistant" && <ExecutionProcess message={message} clock={processClock} onToggle={() => setMessages((items) => items.map((item) => item.id === message.id ? { ...item, processOpen: item.processOpen === false } : item))} />}
                <div className="message-meta"><b>{message.role === "user" ? "你" : "知答"}</b>{message.role === "assistant" && <span>· 基于知识库</span>}</div>
                {message.retrievalStatus && <div className="retrieval-status"><span className="spinner" /><span>{message.retrievalStatus.answering ? `正在使用 ${message.retrievalStatus.model} 生成回答…` : message.retrievalStatus.knowledge_bases?.length ? `正在检索：${message.retrievalStatus.knowledge_bases.map((kb) => kb.name).join("、")}` : "当前范围没有知识库，请在项目设置中关联资料。"}</span></div>}
                <div className={`message-content ${message.error ? "message-error" : ""}`}>
                  {message.content ? <Markdown content={message.content} /> : <span className="typing"><i /><i /><i /></span>}
                </div>
                {message.sources?.length > 0 && <knowledge-disclosure label={`参考了 ${message.sources.length} 段资料`}>
                  <div className="source-list">{message.sources.map((source, index) => <div className="source-item" key={`${source.filename}-${index}`}>
                    <span className="source-index">{index + 1}</span><div><b>{source.filename}{source.page ? ` · 第 ${source.page} 页` : ""}</b><small>{source.knowledge_base_name}</small>{source.preview && <p>{source.preview}</p>}</div>
                  </div>)}</div>
                </knowledge-disclosure>}
              </div>
            </article>)}
            <div ref={endRef} />
          </div>}
        </section>

        <footer className="composer-wrap">
          <form className="composer" onSubmit={sendMessage}>
            <textarea rows="1" value={input} onInput={(event) => setInput(event.target.value)} onKeydown={(event) => { if (event.key === "Enter" && !event.shiftKey && !event.isComposing && event.keyCode !== 229) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="直接提问，每轮都会自动检索知识库…" disabled={busy || chatLoading} />
            <div className="composer-bottom"><div className="composer-tools">{auth?.role === "admin" && <button type="button" className="attach-button" disabled={uploading} onClick={() => fileRef.current?.click()} title="上传资料到知识库"><Upload size={15} />添加资料</button>}<span><kbd>Enter</kbd> 发送 <span className="composer-divider">·</span> <kbd>Shift + Enter</kbd> 换行</span></div><button className="send-button" disabled={!input.trim() || busy || chatLoading || scopeSaving || !projectId} title="发送"><Send size={16} />{busy ? "回答中" : "发送"}</button></div>
          </form>
          <p className="composer-disclaimer">回答由所选模型生成，请核对重要的硬件参数和接线信息。</p>
        </footer>
      </main>

      {managerOpen && <div className="modal-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget) setManagerOpen(false); }}>
        <section className="knowledge-modal" role="dialog" aria-modal="true" aria-label="管理知识库">
          <header className="modal-header"><div><span className="modal-icon"><BookOpen size={18} /></span><div><h2>管理知识库</h2><p>不同主题分开存放，需要时组合到同一个项目。</p></div></div><button className="icon-button" onClick={() => setManagerOpen(false)}><X size={18} /></button></header>
          <div className="kb-manager-body">
            <aside className="kb-manager-sidebar">
              <div className="kb-list-title">我的知识库 <span>{knowledgeBases.length}</span></div>
              {knowledgeBases.map((kb) => <button key={kb.id} className={`kb-manager-item ${kb.id === activeKbId ? "active" : ""}`} onClick={() => setActiveKbId(kb.id)}>
                <span className="kb-manager-icon"><BookOpen size={16} /></span><span><b>{kb.name}</b><small>{kb.document_count || 0} 份文件</small></span><ChevronRight size={14} />
              </button>)}
              {auth?.role === "admin" && (showKbForm ? <form className="new-kb-form" onSubmit={addKnowledgeBase}><input autoFocus value={kbName} onInput={(event) => setKbName(event.target.value)} placeholder="知识库名称" required maxLength={60} /><input value={kbDescription} onInput={(event) => setKbDescription(event.target.value)} placeholder="简介（可选）" maxLength={240} /><div><button type="button" className="quiet-button" onClick={() => setShowKbForm(false)}>取消</button><button className="small-primary" type="submit">创建</button></div></form> : <button className="create-kb-link" onClick={() => setShowKbForm(true)}><Plus size={15} />新建知识库</button>)}
            </aside>
            <div className="kb-detail">
              {activeKb ? <>
                <div className="kb-detail-head"><div><p className="eyebrow">KNOWLEDGE BASE</p><h3>{activeKb.name}</h3><p>{activeKb.description || "把同一主题的资料放在这里，项目可以组合多个知识库。"}</p></div>{auth?.role === "admin" && <button className="danger-quiet" disabled={uploading || busy} onClick={() => removeKnowledgeBase(activeKb)} title="删除知识库"><Trash2 size={16} /></button>}</div>
                {auth?.role === "admin" ? <button type="button" className="upload-zone" disabled={uploading} onClick={() => fileRef.current?.click()} onDrop={(event) => handleDrop(event, activeKbId)}>
                  <span className="upload-icon">{uploading ? <span className="spinner" /> : <Upload size={20} />}</span><b>{uploading ? "正在读取并建立索引…" : "添加资料文件"}</b><small>点击选择或拖入 PDF、DOCX、TXT、MD、CSV · 单个文件 ≤ 30 MB</small>
                </button> : <p className="answer-model-note">游客可查看公开知识库的资料、分片并进行检索；资料修改由管理员维护。</p>}
                <div className="document-list-head"><b>已导入资料</b><span>{documents.length} 份</span></div>
                <div className="document-list">
                  {documentsLoading && <div className="loading-state"><span className="spinner" />正在读取资料列表…</div>}
                  {documentsError && <div className="error-state"><p>{documentsError}</p><button className="quiet-button" onClick={() => refreshDocuments(activeKbId)}>重新加载</button></div>}
                  {!documentsLoading && !documentsError && documents.map((document) => <div className="document-item" key={document.id}><span className="file-type"><FileText size={16} /></span><div><b title={document.filename}>{document.filename}</b><small>{document.chunk_count} 个文本片段 · {new Date(document.uploaded_at).toLocaleDateString("zh-CN")}</small></div><button className="quiet-button chunk-open" title="查看文本分片" onClick={() => loadChunks(document)}><Layers3 size={13} />分片</button>{auth?.role === "admin" && <button className="icon-button danger-hover" title="删除文件" disabled={uploading || busy} onClick={() => removeDocument(document)}><Trash2 size={15} /></button>}</div>)}
                  {!documentsLoading && !documentsError && !documents.length && <div className="empty-documents"><div><FileText size={20} /></div><b>还没有资料</b><p>添加文件后，系统会用 Ollama 向量模型处理并保存到本地。</p></div>}
                </div>
              </> : <div className="empty-documents"><BookOpen size={24} /><b>创建第一个知识库</b><p>之后可以把它加入任意项目。</p></div>}
            </div>
          </div>
          <footer className="modal-footer"><span><ShieldCheck size={14} />文件与向量索引保存在本机</span><button className="quiet-button" onClick={() => setManagerOpen(false)}>完成</button></footer>
        </section>
      </div>}

      {uploadDialogOpen && <div className="modal-backdrop upload-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !uploading) setUploadDialogOpen(false); }}>
        <section className="upload-modal" role="dialog" aria-modal="true" aria-label="上传资料">
          <header className="modal-header"><div><span className="modal-icon"><Upload size={18} /></span><div><h2>导入资料</h2><p>选择目标知识库，文件会逐个上传并自动分片。</p></div></div><button className="icon-button" disabled={uploading} aria-label="关闭上传窗口" onClick={() => setUploadDialogOpen(false)}><X size={18} /></button></header>
          <label className="field-label upload-target">上传到知识库<select value={uploadTargetKbId} disabled={uploading || uploadQueue.some((item) => item.status === "done")} onInput={(event) => setUploadTargetKbId(event.target.value)}><option value="" disabled>请选择知识库</option>{knowledgeBases.map((kb) => <option value={kb.id} key={kb.id}>{kb.name}</option>)}</select><small>项目已关联这个知识库时，下次提问就会自动使用新资料。</small></label>
          {!knowledgeBases.length && <div className="upload-empty"><p>先创建一个用于保存资料的知识库。</p><button className="quiet-button" onClick={() => { setUploadDialogOpen(false); setManagerOpen(true); setShowKbForm(true); }}>创建知识库</button></div>}
          <div className="upload-queue">{uploadQueue.map((item) => <div key={item.id} className={`upload-queue-item upload-${item.status}`}><span className="file-type">{item.status === "uploading" ? <span className="spinner" /> : item.status === "done" ? <Check size={17} /> : <FileText size={17} />}</span><div><b title={item.file.name}>{item.file.name}</b><small>{(item.file.size / 1024 / 1024).toFixed(2)} MB · {item.status === "pending" ? "等待上传" : item.status === "uploading" ? "上传并读取、分片、建立索引中…" : item.status === "done" ? `导入成功 · ${item.chunkCount} 个分片` : item.status === "invalid" ? "无法上传" : "导入失败"}</small>{item.error && <p>{item.error}</p>}</div>{item.status === "error" && <button className="quiet-button" disabled={uploading || !uploadTargetKbId} onClick={() => runUploadQueue(item.id)}><RotateCcw size={13} />重试</button>}{item.status !== "done" && <button className="icon-button" disabled={uploading} title="从队列移除" onClick={() => setUploadQueue((items) => items.filter((entry) => entry.id !== item.id))}><X size={15} /></button>}</div>)}</div>
          <div className="upload-add-row"><button className="quiet-button" disabled={uploading} onClick={() => fileRef.current?.click()}><Plus size={14} />继续添加文件</button><small>也可以把更多文件拖到窗口中</small></div>
          <footer className="modal-footer"><span>{uploadQueue.filter((item) => item.status === "done").length} / {uploadQueue.length} 份已完成</span><div className="modal-footer-actions"><button className="quiet-button" disabled={uploading} onClick={() => setUploadDialogOpen(false)}>关闭</button><button className="primary-button" disabled={uploading || !uploadTargetKbId || !uploadQueue.some((item) => item.status === "pending" || item.status === "error")} onClick={() => runUploadQueue()}>{uploading ? "正在导入…" : "开始导入"}</button></div></footer>
        </section>
      </div>}

      {chunkDocument && <div className="modal-backdrop chunk-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !deletingChunkId) closeChunks(); }}>
        <section className="chunk-modal" role="dialog" aria-modal="true" aria-label="文档分片">
          <header className="modal-header"><div><span className="modal-icon"><Layers3 size={18} /></span><div className="chunk-heading"><h2>文档分片</h2><p title={chunkDocument.filename}>{chunkDocument.filename}</p></div></div><button className="icon-button" disabled={Boolean(deletingChunkId)} aria-label="关闭分片窗口" onClick={closeChunks}><X size={18} /></button></header>
          <p className="chunk-help">以下是参与检索的完整文本。删除分片后，后续提问不会再使用该段；原始文件和历史回答保留。</p>
          <div className="chunk-list">
            {chunksLoading && <div className="loading-state"><span className="spinner" />正在读取分片…</div>}
            {chunksError && <div className="error-state"><p>{chunksError}</p><button className="quiet-button" onClick={() => loadChunks(chunkDocument, chunkOffset)}>重新加载</button></div>}
            {!chunksLoading && !chunksError && chunks.map((chunk) => <article key={chunk.id} className="chunk-card"><header><div><b>分片 {chunk.index}</b>{chunk.page != null && <span>第 {chunk.page} 页</span>}<span>{chunk.content.length} 字符</span></div>{auth?.role === "admin" && <button className="quiet-button delete-chunk" disabled={Boolean(deletingChunkId)} onClick={() => removeChunk(chunk)}><Trash2 size={13} />{deletingChunkId === chunk.id ? "删除中…" : "删除此分片"}</button>}</header><pre>{chunk.content || "（空文本）"}</pre></article>)}
            {!chunksLoading && !chunksError && !chunks.length && <div className="empty-documents"><Layers3 size={24} /><b>这份资料没有可用分片</b><p>全部分片被删除后，原始文件记录仍然保留。</p></div>}
          </div>
          <footer className="modal-footer"><span>共 {chunkTotal} 个分片 · {chunkTotal ? chunkOffset + 1 : 0}–{Math.min(chunkOffset + 20, chunkTotal)}</span><div className="chunk-pagination"><button className="quiet-button" disabled={chunksLoading || Boolean(deletingChunkId) || chunkOffset === 0} onClick={() => loadChunks(chunkDocument, Math.max(0, chunkOffset - 20))}><ChevronLeft size={14} />上一页</button><button className="quiet-button" disabled={chunksLoading || Boolean(deletingChunkId) || chunkOffset + 20 >= chunkTotal} onClick={() => loadChunks(chunkDocument, chunkOffset + 20)}>下一页<ChevronRight size={14} /></button></div></footer>
        </section>
      </div>}

      {modelDialogOpen && <div className="modal-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !modelSaving) setModelDialogOpen(false); }}>
        <section className="answer-model-modal" role="dialog" aria-modal="true" aria-labelledby="answer-model-title">
          <header><div><span className="modal-icon"><Settings2 size={18} /></span><div><h2 id="answer-model-title">RAG 回答模型</h2><p>可选个人 API、浏览器 Ollama 或服务器模型。</p></div></div><button className="icon-button" type="button" aria-label="关闭" disabled={modelSaving} onClick={() => setModelDialogOpen(false)}><X size={18} /></button></header>
          <div className="answer-model-body">
            {modelSettingsError && <p className="answer-model-error" role="alert">{modelSettingsError}</p>}
            <section className="answer-model-personal">
              <div className="answer-model-section-head"><div><b>个人可用模型</b><small>打开此窗口时自动读取；切换只影响当前浏览器。</small></div><button className="quiet-button" type="button" disabled={modelSyncing || modelSaving} onClick={syncAgentModel}>{modelSyncing ? "正在读取…" : "刷新 Agent 模型"}</button></div>
              {agentModelProfiles.length ? <div className="answer-agent-models">{agentModelProfiles.map((profile) => {
                const detail = profile.mode === "server" ? "服务器模型" : profile.mode === "local" ? "浏览器本机 Ollama" : `${profile.vendor || profile.provider || "API"} · ${profile.model}`;
                return <label key={profile.id} className={selectedAgentModelId === profile.id ? "selected" : ""}><input type="radio" name="rag-browser-model" value={profile.id} checked={selectedAgentModelId === profile.id} onChange={() => setSelectedAgentModelId(profile.id)} /><span><b>{profile.name || profile.model}</b><small>{detail}</small></span>{browserModel?.id === profile.id && <em className="model-current-tag">当前使用</em>}</label>;
              })}</div> : <p className="answer-model-note">{modelSyncing ? "正在从 Agent 读取可用模型…" : "还没有可选模型。请先在 Agent 保存 API 模型，或从聊天模型菜单选择 Ollama。"}</p>}
              <p className="answer-model-note">个人 API 的密钥保存在当前浏览器并直连模型服务；使用个人 API 时，本轮问题、最近对话和检索资料会发送给所选服务。若 Agent 配置了网页令牌，它只保存在当前标签页会话中，并随服务器模型请求发给 Agent。</p>
            </section>
            {auth?.role === "admin" && <section className="answer-model-admin">
              <b>管理员默认模型（RAG Ollama）</b>
              <label>回答模型
                <select value={modelSettings.local_model} disabled={modelSaving} onChange={(event) => setModelSettings((current) => ({ ...current, local_model: event.target.value }))}>
                  {!status?.models?.includes(modelSettings.local_model) && <option value={modelSettings.local_model}>{modelSettings.local_model}（当前配置）</option>}
                  {(status?.models || []).map((model) => <option key={model} value={model}>{model}</option>)}
                </select>
                <small>{status?.ollama_connected ? `RAG 服务 Ollama 已连接；默认模型：${modelSettings.local_model}` : "尚未连接 RAG 服务 Ollama。启动后刷新模型列表。"}</small>
              </label>
            </section>}
          </div>
          <footer className="answer-model-actions">
            <button className="quiet-button" type="button" disabled={modelSaving} onClick={() => setModelDialogOpen(false)}>关闭</button>
            <button className="quiet-button" type="button" disabled={modelSaving} onClick={refreshModelStatus}>刷新模型</button>
            {auth?.role === "admin" && <button className="quiet-button" type="button" disabled={modelSaving || !modelSettings.local_model} onClick={saveModelSettings}>保存 RAG 默认模型</button>}
            <button className="primary-button" type="button" disabled={modelSaving || modelSyncing || !selectedAgentModelId} onClick={saveSelectedAgentModel}>使用此模型</button>
          </footer>
        </section>
      </div>}

      {sidebarMenu && <Teleport to="body"><div ref={sidebarMenuRef} className="sidebar-context-menu" role="menu" aria-label={`${sidebarMenu.type === "project" ? "项目" : "对话"}操作`} style={{ left: `${sidebarMenu.x}px`, top: `${sidebarMenu.y}px` }}>
        <button type="button" role="menuitem" onClick={openRenameFromMenu}><Pencil size={14} />重命名</button>
        <button type="button" role="menuitem" className="danger" onClick={() => {
          const target = sidebarMenu;
          setSidebarMenu(null);
          if (target.type === "project") {
            const project = projects.find((item) => item.id === target.id);
            if (project) removeProject(project);
          } else {
            const chat = chats.find((item) => item.id === target.id);
            if (chat) removeChat(chat);
          }
        }}><Trash2 size={14} />删除{sidebarMenu.type === "project" ? "项目" : "对话"}</button>
      </div></Teleport>}

      {deleteChatTarget && <div className="modal-backdrop delete-chat-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !deleteChatSaving) setDeleteChatTarget(null); }}>
        <form className="delete-chat-modal" role="dialog" aria-modal="true" aria-labelledby="delete-chat-title" aria-describedby="delete-chat-description" onSubmit={(event) => { event.preventDefault(); void confirmRemoveChat(); }} onKeydown={(event) => { if (event.key === "Escape" && !deleteChatSaving) { event.preventDefault(); setDeleteChatTarget(null); } }}>
          <header className="delete-chat-modal-head">
            <span className="delete-chat-modal-icon"><Trash2 size={18} /></span>
            <div><span className="delete-chat-eyebrow">对话管理</span><h2 id="delete-chat-title">删除这条对话？</h2></div>
            <button type="button" className="icon-button" aria-label="关闭" disabled={deleteChatSaving} onClick={() => setDeleteChatTarget(null)}><X size={18} /></button>
          </header>
          <p id="delete-chat-description" className="delete-chat-description">删除后，这段对话及其中的消息记录将从本机移除。</p>
          <div className="delete-chat-preview"><span><MessageSquare size={16} /></span><div><small>将删除的对话</small><strong>{deleteChatTarget.title || "新对话"}</strong></div></div>
          <div className="delete-chat-warning"><span className="delete-chat-warning-dot" />删除后无法恢复</div>
          <footer className="delete-chat-modal-actions"><button type="button" autoFocus className="quiet-button" disabled={deleteChatSaving} onClick={() => setDeleteChatTarget(null)}>取消</button><button type="submit" className="delete-chat-confirm" disabled={deleteChatSaving}>{deleteChatSaving ? "正在删除…" : "删除对话"}</button></footer>
        </form>
      </div>}

      {deleteProjectTarget && <div className="modal-backdrop delete-chat-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !deleteProjectSaving) setDeleteProjectTarget(null); }}>
        <form className="delete-chat-modal delete-project-modal" role="dialog" aria-modal="true" aria-labelledby="delete-project-title" aria-describedby="delete-project-description" onSubmit={(event) => { event.preventDefault(); void confirmRemoveProject(); }} onKeydown={(event) => { if (event.key === "Escape" && !deleteProjectSaving) { event.preventDefault(); setDeleteProjectTarget(null); } }}>
          <header className="delete-chat-modal-head">
            <span className="delete-chat-modal-icon"><Trash2 size={18} /></span>
            <div><span className="delete-chat-eyebrow">项目管理</span><h2 id="delete-project-title">删除项目？</h2></div>
            <button type="button" className="icon-button" aria-label="关闭" disabled={deleteProjectSaving} onClick={() => setDeleteProjectTarget(null)}><X size={18} /></button>
          </header>
          <p id="delete-project-description" className="delete-chat-description delete-project-description">确定删除 <strong>“{deleteProjectTarget.name}”</strong> 吗？项目及其中的全部对话、消息记录将无法恢复。</p>
          <p className="delete-project-retained"><ShieldCheck size={15} />关联的知识库、资料与索引会保留。</p>
          <footer className="delete-chat-modal-actions"><button type="button" autoFocus className="quiet-button" disabled={deleteProjectSaving} onClick={() => setDeleteProjectTarget(null)}>取消</button><button type="submit" className="delete-chat-confirm" disabled={deleteProjectSaving}>{deleteProjectSaving ? "正在删除…" : "删除项目"}</button></footer>
        </form>
      </div>}

      {deleteKbTarget && <div className="modal-backdrop delete-chat-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !deleteKbSaving) setDeleteKbTarget(null); }}>
        <form className="delete-chat-modal delete-kb-modal" role="dialog" aria-modal="true" aria-labelledby="delete-kb-title" aria-describedby="delete-kb-description" onSubmit={(event) => { event.preventDefault(); void confirmRemoveKnowledgeBase(); }} onKeydown={(event) => { if (event.key === "Escape" && !deleteKbSaving) { event.preventDefault(); setDeleteKbTarget(null); } }}>
          <header className="delete-chat-modal-head">
            <span className="delete-chat-modal-icon"><Trash2 size={18} /></span>
            <div><span className="delete-chat-eyebrow">知识库管理</span><h2 id="delete-kb-title">删除知识库？</h2></div>
            <button type="button" className="icon-button" aria-label="关闭" disabled={deleteKbSaving} onClick={() => setDeleteKbTarget(null)}><X size={18} /></button>
          </header>
          <p id="delete-kb-description" className="delete-chat-description delete-kb-description">确定删除这个知识库吗？其中的资料文件、文本分片和向量索引都会一并删除；已关联的对话将不再使用它。</p>
          <div className="delete-chat-preview"><span><BookOpen size={16} /></span><div><small>将删除的知识库 · {deleteKbTarget.document_count || 0} 份文件</small><strong title={deleteKbTarget.name}>{deleteKbTarget.name}</strong></div></div>
          <div className="delete-chat-warning"><span className="delete-chat-warning-dot" />此操作无法撤销</div>
          <footer className="delete-chat-modal-actions"><button type="button" autoFocus className="quiet-button" disabled={deleteKbSaving} onClick={() => setDeleteKbTarget(null)}>取消</button><button type="submit" className="delete-chat-confirm" disabled={deleteKbSaving || uploading || busy}>{deleteKbSaving ? "正在删除…" : "删除知识库"}</button></footer>
        </form>
      </div>}

      {renameTarget && <div className="modal-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget && !renameSaving) setRenameTarget(null); }}>
        <form className="rename-modal" role="dialog" aria-modal="true" aria-labelledby="rename-title" onSubmit={saveRename} onKeydown={(event) => { if (event.key === "Escape" && !renameSaving) setRenameTarget(null); }}>
          <h2 id="rename-title">重命名{renameTarget.type === "project" ? "项目" : "对话"}</h2>
          <label htmlFor="rename-value">名称</label>
          <input id="rename-value" autoFocus value={renameValue} onInput={(event) => setRenameValue(event.target.value)} maxLength={renameTarget.type === "project" ? 60 : 80} required />
          <div className="rename-actions"><button type="button" className="quiet-button" onClick={() => setRenameTarget(null)} disabled={renameSaving}>取消</button><button type="submit" className="primary-button" disabled={renameSaving || !renameValue.trim()}>{renameSaving ? "保存中…" : "保存"}</button></div>
        </form>
      </div>}

      {projectDialog && <div className="modal-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget) setProjectDialog(false); }}>
        <form className="project-modal" onSubmit={saveProject}>
          <header className="modal-header"><div><span className="modal-icon"><FolderKanban size={18} /></span><div><h2>{editingProject ? "项目设置" : "新建项目"}</h2><p>{editingProject ? "选择这个项目常用的知识库。" : "一个项目可以组合多个知识库。"}</p></div></div><button type="button" className="icon-button" onClick={() => setProjectDialog(false)}><X size={18} /></button></header>
          <label className="field-label">项目名称<input value={projectName} onInput={(event) => setProjectName(event.target.value)} required maxLength={60} placeholder="例如：智能小车" /></label>
          <div className="field-label">关联知识库 <small>新对话会默认使用这些资料；也可以在每段对话中单独调整。</small></div>
          <div className="project-kb-options">{knowledgeBases.map((kb) => <label className="project-kb-option" key={kb.id}><input type="checkbox" checked={projectKbIds.includes(kb.id)} onInput={(event) => setProjectKbIds((ids) => event.target.checked ? [...ids, kb.id] : ids.filter((id) => id !== kb.id))} /><span className="scope-option-icon"><BookOpen size={14} /></span><span><b>{kb.name}</b><small>{kb.document_count || 0} 份资料</small></span><Check size={15} /></label>)}</div>
          {!knowledgeBases.length && <button type="button" className="quiet-button" onClick={() => { setProjectDialog(false); setManagerOpen(true); setShowKbForm(true); }}>先创建知识库</button>}
          <footer className="project-modal-footer"><button type="button" className="quiet-button" onClick={() => setProjectDialog(false)}>取消</button><button className="primary-button" disabled={projectSaving || !projectName.trim()}>{projectSaving ? "保存中…" : editingProject ? "保存设置" : "创建项目"}</button></footer>
        </form>
      </div>}

      {loginOpen && <div className="modal-backdrop identity-login-backdrop" onMousedown={(event) => { if (event.target === event.currentTarget) closeLogin(); }}>
        <form className="identity-login-modal" role="dialog" aria-modal="true" aria-labelledby="identity-login-title" onSubmit={submitLogin} onKeydown={(event) => { if (event.key === "Escape" && !loginBusy) closeLogin(); }}>
          <button className="icon-button identity-login-close" type="button" aria-label="关闭" disabled={loginBusy} onClick={closeLogin}><X size={18} /></button>
          <p className="eyebrow">ADMINISTRATOR ACCESS</p>
          <h2 id="identity-login-title">管理员登录</h2>
          <p className="identity-login-description">登录后，Agent、RAG 和项目主页会同步显示管理员身份。</p>
          <label htmlFor="identity-login-username">账号</label>
          <input id="identity-login-username" autoFocus autoComplete="username" maxLength={80} required value={loginUsername} onInput={(event) => setLoginUsername(event.target.value)} />
          <label htmlFor="identity-login-password">密码</label>
          <input id="identity-login-password" type="password" autoComplete="current-password" maxLength={512} required value={loginPassword} onInput={(event) => setLoginPassword(event.target.value)} />
          {loginError && <p className="identity-login-error" role="alert">{loginError}</p>}
          <div className="identity-login-actions"><button className="quiet-button" type="button" disabled={loginBusy} onClick={closeLogin}>取消</button><button className="primary-button" type="submit" disabled={loginBusy}>{loginBusy ? "正在登录…" : "登录"}</button></div>
        </form>
      </div>}

      {toast && <div className="toast"><span><Check size={15} /></span>{toast}</div>}
    </div>
  );
}

export default {
  name: "RagApp",
  setup() {
    const frame = createStateFrame();
    return () => { frame.begin(); return renderApp(); };
  },
};
