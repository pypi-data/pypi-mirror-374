import os, json
from datetime import datetime

_SECRET_KEYS = {"password","api_key","authorization","token","secret","client_secret","access_token","refresh_token"}

def _safe_redact(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = "***" if k.lower() in _SECRET_KEYS else _safe_redact(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [_safe_redact(x) for x in obj]
    s = str(obj)
    return s[:4000]  # cap size

def _summarize(obj, hard_cap=2000):
    s = str(obj)
    return (s[:hard_cap] + "…") if len(s) > hard_cap else s

class TraceLogger:
    """Writes JSONL traces to logs/<ticket_id>/trace.jsonl"""
    def __init__(self, base_dir="logs", ticket_id="unknown"):
        self.base_dir = base_dir
        self.ticket_id = str(ticket_id)
        os.makedirs(os.path.join(base_dir, self.ticket_id), exist_ok=True)
        self.path = os.path.join(base_dir, self.ticket_id, "trace.jsonl")

    def _write(self, rec: dict):
        rec["ts"] = datetime.utcnow().isoformat() + "Z"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def log_agent_input(self, agent_name, task_desc, payload):
        self._write({
            "event": "agent_input",
            "agent": agent_name,
            "task": (task_desc or "")[:2000],
            "payload": _safe_redact(payload),
        })

    def log_step(self, agent_name, step_kind, tool=None, input=None, output=None, ok=True, elapsed_ms=None):
        self._write({
            "event": "agent_step",
            "agent": agent_name,
            "step_kind": step_kind,          # e.g. "tool_call", "tool_result", "final"
            "tool": tool,
            "input": _safe_redact(input),
            "output_summary": _summarize(output),
            "ok": ok,
            "elapsed_ms": elapsed_ms,
        })

    def log_final(self, agent_name, final_output):
        self._write({
            "event": "agent_final",
            "agent": agent_name,
            "final_output": _summarize(final_output, hard_cap=8000),
        })
