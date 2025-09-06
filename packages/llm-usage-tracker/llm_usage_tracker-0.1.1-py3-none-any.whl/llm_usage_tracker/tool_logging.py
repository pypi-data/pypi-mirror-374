import json, time
from functools import wraps
from contextvars import ContextVar

_CURRENT_AGENT = ContextVar("current_agent", default="(unknown-agent)")

def set_current_agent(name: str):
    _CURRENT_AGENT.set(name)

def _redact(data, keys=()):
    try:
        if isinstance(data, dict):
            out = {}
            for k, v in data.items():
                out[k] = "***" if k in keys else _redact(v, keys)
            return out
        if isinstance(data, (list, tuple)):
            return [_redact(x, keys) for x in data]
        return data
    except Exception:
        return data

def log_tool_calls(tool_name: str, tracer=None, redact_keys=(), printer=print):
    """
    Decorate your .run(...) methods of tools to log input/output + write JSONL trace.
    Usage:
      OnlineCarrierStatusTool.run = log_tool_calls("Online Carrier Status Check", tracer)(OnlineCarrierStatusTool.run)
    """
    def deco(func):
        @wraps(func)
        def wrapper(*a, **k):
            t0 = time.time()
            safe_args = _redact({"args": a, "kwargs": k}, keys=redact_keys)
            try:
                printer(f"[tool:{tool_name}] ▶︎ input: {json.dumps(safe_args, default=str)}")
            except Exception:
                pass
            if tracer:
                tracer.log_step(agent_name=_CURRENT_AGENT.get(), step_kind="tool_call",
                                tool=tool_name, input=safe_args)
            out = func(*a, **k)
            ms = int((time.time()-t0)*1000)
            try:
                safe_out = _redact(out, keys=redact_keys)
                printer(f"[tool:{tool_name}] ◀︎ output: {json.dumps(safe_out, default=str)[:5000]}")
            except Exception:
                safe_out = out
            if tracer:
                tracer.log_step(agent_name=_CURRENT_AGENT.get(), step_kind="tool_result",
                                tool=tool_name, output=safe_out, elapsed_ms=ms)
            return out
        return wrapper
    return deco
