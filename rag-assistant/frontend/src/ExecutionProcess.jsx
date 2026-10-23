import { h } from "vue";
import { ChevronDown, Check, X } from "./icons.js";

const seconds = (milliseconds) => `${(Math.max(0, milliseconds || 0) / 1000).toFixed(1)} 秒`;
export default function ExecutionProcess({ message, clock, onToggle }) {
  const steps = message.execution_steps || [];
  if (!steps.length) return null;
  const open = message.processOpen !== false;
  const running = message.streaming;
  const failed = message.error || steps.some((step) => step.status === "error");
  const elapsed = running ? clock - (message.executionStartedAt || clock) : message.execution_elapsed_ms;
  const status = running ? "处理中" : failed ? "处理失败" : "已处理";
  return <section className={`execution-process ${failed ? "process-failed" : ""}`} aria-label="协作执行过程">
    <button type="button" className="process-heading" aria-expanded={open} aria-controls={`process-${message.id}`} onClick={onToggle}>
      <span className={`process-indicator ${running ? "is-running" : ""}`} />
      <span>{status} · {steps.length} 步 · {seconds(elapsed)}</span>
      {running && <span className="process-current">{steps.find((step) => step.status === "running")?.label || "调度"}</span>}
      <span className="process-toggle">{open ? "收起" : "展开"}<ChevronDown size={13} class={open ? "is-open" : ""} /></span>
    </button>
    {open && <div className="process-content" id={`process-${message.id}`}>
      <p className="process-flow">检索规划 → 资料检索 → 证据审核 → 回答生成；资料不足时最多补检一次。</p>
      <ol className="process-steps" aria-live={running ? "polite" : "off"} aria-relevant="additions text">
        {steps.map((step) => <li key={step.id} className={`process-step step-${step.status}`}>
          <span className="process-step-state" aria-label={{ running: "正在执行", completed: "已完成", warning: "提示", error: "失败" }[step.status]}>
            {step.status === "running" ? <span className="spinner" /> : step.status === "completed" ? <Check size={13} /> : step.status === "error" ? <X size={13} /> : "!"}
          </span>
          <div className="process-step-body"><div className="process-step-title">
            <b className={`process-agent agent-${step.agent}`}>{step.label}</b><code>{step.stage}</code>
            <time>{seconds(step.status === "running" ? clock - (step.started_at || clock) : step.duration_ms)}</time>
          </div><p>{step.detail}</p></div>
        </li>)}
      </ol>
    </div>}
  </section>;
}
