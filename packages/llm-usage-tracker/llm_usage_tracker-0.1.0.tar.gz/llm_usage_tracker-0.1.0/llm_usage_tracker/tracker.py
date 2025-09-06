import json, threading, os, importlib
from collections import defaultdict
from contextvars import ContextVar
from contextlib import contextmanager  # NEW

__all__ = [
    "setup_patch", "compute_usage_costs", "print_usage_costs",
    "UsageSession", "track_usage", "TOKENS_BY_MODEL",
    "set_scope", "scope_context", "print_usage_costs_by_scope",  # NEW
]


# ---------- Globals ----------
USAGE_LOCK = threading.Lock()
TOKENS_BY_MODEL = defaultdict(lambda: {"input_full": 0, "input_cached": 0, "output": 0})
_PATCHED = False
SCOPE = ContextVar("llm_scope", default="global")
# NEW: per-scope accumulator: PER_SCOPE[scope][model] = token dict
PER_SCOPE = defaultdict(lambda: defaultdict(lambda: {"input_full": 0, "input_cached": 0, "output": 0}))  # NEW


def set_scope(scope: str) -> None:
    """Set the current logical scope (e.g., 'agent:Task Delegator')."""
    SCOPE.set(scope)

@contextmanager
def scope_context(scope: str):  # NEW: convenient context manager if you need it
    token = SCOPE.set(scope)
    try:
        yield
    finally:
        SCOPE.reset(token)

# ---------- Helpers ----------
def _safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def _record_usage_from_mapping(model, usage):
    """
    Normalize usage across OpenAI v1/v0/Responses + LiteLLM variants (and more).
    """
    if not model or not usage:
        return
    try:
        pt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        ct = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
        cached = int(
            usage.get("cached_prompt_tokens")
            or _safe_get(usage, "prompt_tokens_details", "cached_tokens", default=0)
            or usage.get("cache_read_input_tokens")
            or 0
        )
        input_full = max(pt - cached, 0)
        with USAGE_LOCK:
            m = str(model).lower()
            TOKENS_BY_MODEL[m]["input_full"]   += input_full
            TOKENS_BY_MODEL[m]["input_cached"] += cached
            TOKENS_BY_MODEL[m]["output"]       += ct

            # NEW: per-scope totals
            scope = SCOPE.get()
            PER_SCOPE[scope][m]["input_full"]   += input_full
            PER_SCOPE[scope][m]["input_cached"] += cached
            PER_SCOPE[scope][m]["output"]       += ct
    except Exception:
        pass

# ---------- Patchers ----------
def _patch_openai_v1():
    try:
        from openai import OpenAI
        client = OpenAI()

        if hasattr(client, "chat") and hasattr(client.chat, "completions") and hasattr(client.chat.completions, "create"):
            _orig = client.chat.completions.create
            def _wrap(*a, **k):
                resp = _orig(*a, **k)
                try:
                    model = getattr(resp, "model", None)
                    usage = getattr(resp, "usage", None)
                    if hasattr(resp, "dict"):
                        d = resp.dict()
                        model = model or d.get("model")
                        usage = usage or d.get("usage")
                    if usage and hasattr(usage, "dict"):
                        usage = usage.dict()
                    if isinstance(usage, dict):
                        _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            client.chat.completions.create = _wrap

        if hasattr(client, "responses") and hasattr(client.responses, "create"):
            _orig = client.responses.create
            def _wrap(*a, **k):
                resp = _orig(*a, **k)
                try:
                    model = getattr(resp, "model", None)
                    usage = getattr(resp, "usage", None)
                    if hasattr(resp, "dict"):
                        d = resp.dict()
                        model = model or d.get("model")
                        usage = usage or d.get("usage")
                    if usage and hasattr(usage, "dict"):
                        usage = usage.dict()
                    if isinstance(usage, dict):
                        _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            client.responses.create = _wrap
    except Exception:
        pass

def _patch_openai_module():
    try:
        import openai as mod
        if hasattr(mod, "chat") and hasattr(mod.chat, "completions") and hasattr(mod.chat.completions, "create"):
            _orig = mod.chat.completions.create
            def _wrap(*a, **k):
                resp = _orig(*a, **k)
                try:
                    model = getattr(resp, "model", None)
                    usage = getattr(resp, "usage", None)
                    if hasattr(resp, "dict"):
                        d = resp.dict()
                        model = model or d.get("model")
                        usage = usage or d.get("usage")
                    if usage and hasattr(usage, "dict"):
                        usage = usage.dict()
                    if isinstance(usage, dict):
                        _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            mod.chat.completions.create = _wrap

        if hasattr(mod, "responses") and hasattr(mod.responses, "create"):
            _orig2 = mod.responses.create
            def _wrap2(*a, **k):
                resp = _orig2(*a, **k)
                try:
                    model = getattr(resp, "model", None)
                    usage = getattr(resp, "usage", None)
                    if hasattr(resp, "dict"):
                        d = resp.dict()
                        model = model or d.get("model")
                        usage = usage or d.get("usage")
                    if usage and hasattr(usage, "dict"):
                        usage = usage.dict()
                    if isinstance(usage, dict):
                        _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            mod.responses.create = _wrap2
    except Exception:
        pass

def _patch_openai_v0():
    try:
        import openai as v0
        if hasattr(v0, "ChatCompletion") and hasattr(v0.ChatCompletion, "create"):
            _orig = v0.ChatCompletion.create
            def _wrap(*a, **k):
                resp = _orig(*a, **k)  # dict-like
                try:
                    model = resp.get("model")
                    usage = resp.get("usage") or {}
                    _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            v0.ChatCompletion.create = _wrap

        if hasattr(v0, "Completion") and hasattr(v0.Completion, "create"):
            _orig2 = v0.Completion.create
            def _wrap2(*a, **k):
                resp = _orig2(*a, **k)
                try:
                    model = resp.get("model")
                    usage = resp.get("usage") or {}
                    _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            v0.Completion.create = _wrap2
    except Exception:
        pass

def _patch_litellm():
    try:
        if importlib.util.find_spec("litellm") is None:
            return
        litellm = importlib.import_module("litellm")

        if hasattr(litellm, "completion"):
            _orig = litellm.completion
            def _wrap(*a, **k):
                resp = _orig(*a, **k)  # dict-like
                try:
                    model = resp.get("model")
                    usage = resp.get("usage") or {}
                    if not usage and isinstance(resp.get("choices"), list):
                        usage = _safe_get(resp, "choices", 0, "usage", default={}) or {}
                    _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            litellm.completion = _wrap

        if hasattr(litellm, "acompletion"):
            _orig_a = litellm.acompletion
            async def _wrap_a(*a, **k):
                resp = await _orig_a(*a, **k)
                try:
                    model = resp.get("model")
                    usage = resp.get("usage") or {}
                    if not usage and isinstance(resp.get("choices"), list):
                        usage = _safe_get(resp, "choices", 0, "usage", default={}) or {}
                    _record_usage_from_mapping(model, usage)
                except Exception:
                    pass
                return resp
            litellm.acompletion = _wrap_a
    except Exception:
        pass

def _patch_gemini():
    try:
        if importlib.util.find_spec("google.generativeai") is None:
            return
        genai = importlib.import_module("google.generativeai")

        def _record_gemini_usage(model_name, usage_md):
            if not usage_md: return
            pt = int(getattr(usage_md, "prompt_token_count", None) or getattr(usage_md, "get", lambda *_:0)("prompt_token_count", 0))
            ct = int(getattr(usage_md, "candidates_token_count", None) or getattr(usage_md, "get", lambda *_:0)("candidates_token_count", 0))
            with USAGE_LOCK:
                m = str(model_name).lower()
                TOKENS_BY_MODEL[m]["input_full"] += pt
                TOKENS_BY_MODEL[m]["output"]     += ct

        if hasattr(genai, "GenerativeModel"):
            _orig_gc = genai.GenerativeModel.generate_content
            def _wrap(self, *a, **k):
                resp = _orig_gc(self, *a, **k)
                try:
                    model_name = getattr(resp, "model", None) or getattr(self, "model_name", None) or getattr(self, "model", None)
                    usage_md = getattr(resp, "usage_metadata", None)
                    if hasattr(usage_md, "to_dict"): usage_md = usage_md.to_dict()
                    elif hasattr(usage_md, "__dict__") and not isinstance(usage_md, dict): usage_md = usage_md.__dict__
                    _record_gemini_usage(model_name, usage_md or {})
                except Exception:
                    pass
                return resp
            genai.GenerativeModel.generate_content = _wrap

        if hasattr(genai, "ChatSession"):
            _orig_send = genai.ChatSession.send_message
            def _wrap(self, *a, **k):
                resp = _orig_send(self, *a, **k)
                try:
                    model_obj = getattr(self, "_model", None)
                    model_name = getattr(model_obj, "model_name", None) or getattr(model_obj, "model", None)
                    usage_md = getattr(resp, "usage_metadata", None)
                    if hasattr(usage_md, "to_dict"): usage_md = usage_md.to_dict()
                    elif hasattr(usage_md, "__dict__") and not isinstance(usage_md, dict): usage_md = usage_md.__dict__
                    _record_gemini_usage(model_name, usage_md or {})
                except Exception:
                    pass
                return resp
            genai.ChatSession.send_message = _wrap
    except Exception:
        pass

def setup_patch():
    """Call once at process start. Idempotent."""
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    _patch_openai_v1()
    _patch_openai_module()
    _patch_openai_v0()
    _patch_litellm()
    _patch_gemini()

# ---------- Pricing / Reporting ----------
def compute_usage_costs(pricing_table):
    per_model, grand = {}, 0.0
    with USAGE_LOCK:
        for m, t in TOKENS_BY_MODEL.items():
            p = next((r for r in pricing_table if r["match"] in m), {"input_full":0.0,"input_cached":0.0,"output":0.0})
            fresh_usd  = t["input_full"]   * p["input_full"]
            cached_usd = t["input_cached"] * p["input_cached"]
            out_usd    = t["output"]       * p["output"]
            total_usd  = fresh_usd + cached_usd + out_usd
            per_model[m] = {
                "tokens": dict(t),
                "usd_breakdown": {
                    "fresh_input_usd":  round(fresh_usd, 6),
                    "cached_input_usd": round(cached_usd, 6),
                    "output_usd":       round(out_usd, 6),
                    "total_usd":        round(total_usd, 6),
                }
            }
            grand += total_usd
    return per_model, round(grand, 6)

def print_usage_costs(pricing_table, *, header=None):
    per_model, grand = compute_usage_costs(pricing_table)
    if header:
        print(header)
    print(json.dumps({"per_model": per_model, "grand_total_usd": grand}, indent=2))
    with USAGE_LOCK:
        agg_prompt = sum(v["tokens"]["input_full"] + v["tokens"]["input_cached"] for v in per_model.values())
        agg_cached = sum(v["tokens"]["input_cached"] for v in per_model.values())
        agg_output = sum(v["tokens"]["output"] for v in per_model.values())
        agg_total  = agg_prompt + agg_output
    print({"per_model_prompt_sum": agg_prompt, "per_model_cached_sum": agg_cached,
           "per_model_output_sum": agg_output, "per_model_total_sum": agg_total})
    
def print_usage_costs_by_scope(pricing_table, *, header=None):
    """Print cost breakdown per scope (e.g., per agent) and per model."""
    with USAGE_LOCK:
        snapshot = json.loads(json.dumps(PER_SCOPE))  # deep-ish copy

    report = {}
    grand_total = 0.0

    for scope, models in snapshot.items():
        scope_total = 0.0
        per_model_out = {}
        for m, t in models.items():
            price = next((r for r in pricing_table if r["match"] in m), {"input_full":0.0,"input_cached":0.0,"output":0.0})
            fresh_usd  = t["input_full"]   * price["input_full"]
            cached_usd = t["input_cached"] * price["input_cached"]
            out_usd    = t["output"]       * price["output"]
            total_usd  = fresh_usd + cached_usd + out_usd
            per_model_out[m] = {
                "tokens": t,
                "usd_breakdown": {
                    "fresh_input_usd":  round(fresh_usd, 6),
                    "cached_input_usd": round(cached_usd, 6),
                    "output_usd":       round(out_usd, 6),
                    "total_usd":        round(total_usd, 6),
                }
            }
            scope_total += total_usd
        report[scope] = {
            "per_model": per_model_out,
            "scope_total_usd": round(scope_total, 6),
        }
        grand_total += scope_total

    if header:
        print(header)
    print(json.dumps({"per_scope": report, "grand_total_usd": round(grand_total, 6)}, indent=2))

# ---------- Context manager & Decorator ----------
class UsageSession:
    """Capture delta usage for a block, optionally save to JSON."""
    def __init__(self, pricing_table, label=None, save_path=None):
        self.pricing_table = pricing_table
        self.label = label
        self.save_path = save_path
        self._start = None
        self.result = None

    def __enter__(self):
        with USAGE_LOCK:
            self._start = {m: dict(t) for m, t in TOKENS_BY_MODEL.items()}
        return self

    def __exit__(self, exc_type, exc, tb):
        with USAGE_LOCK:
            end = {m: dict(t) for m, t in TOKENS_BY_MODEL.items()}

        delta = defaultdict(lambda: {"input_full": 0, "input_cached": 0, "output": 0})
        for m, e in end.items():
            s = self._start.get(m, {"input_full":0,"input_cached":0,"output":0})
            delta[m]["input_full"]   = e["input_full"]   - s.get("input_full", 0)
            delta[m]["input_cached"] = e["input_cached"] - s.get("input_cached", 0)
            delta[m]["output"]       = e["output"]       - s.get("output", 0)
        delta = {m: t for m, t in delta.items() if any(v>0 for v in t.values())}

        per_model, grand = {}, 0.0
        for m, t in delta.items():
            p = next((r for r in self.pricing_table if r["match"] in m), {"input_full":0.0,"input_cached":0.0,"output":0.0})
            fresh_usd  = t["input_full"]   * p["input_full"]
            cached_usd = t["input_cached"] * p["input_cached"]
            out_usd    = t["output"]       * p["output"]
            total_usd  = fresh_usd + cached_usd + out_usd
            per_model[m] = {
                "tokens": dict(t),
                "usd_breakdown": {
                    "fresh_input_usd":  round(fresh_usd, 6),
                    "cached_input_usd": round(cached_usd, 6),
                    "output_usd":       round(out_usd, 6),
                    "total_usd":        round(total_usd, 6),
                }
            }
            grand += total_usd

        self.result = {"label": self.label, "per_model": per_model, "grand_total_usd": round(grand, 6)}
        if self.save_path:
            try:
                os.makedirs(os.path.dirname(self.save_path) or ".", exist_ok=True)
                with open(self.save_path, "w") as f:
                    json.dump(self.result, f, indent=2)
            except Exception:
                pass

def track_usage(pricing_table, label=None, save_path=None):
    """Decorator to track usage for a single function call."""
    def _decorator(fn):
        def _wrapped(*args, **kwargs):
            with UsageSession(pricing_table, label=label, save_path=save_path) as sess:
                rv = fn(*args, **kwargs)
            print(json.dumps(sess.result, indent=2))
            return rv
        return _wrapped
    return _decorator
