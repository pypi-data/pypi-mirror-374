# llm_usage_tracker/crew_helpers.py

from .tool_logging import set_current_agent
from .tracker import set_scope

def step_cb_factory(agent_label: str, tracer=None):
    """
    Returns a step callback that:
      - sets the usage SCOPE so tokens are attributed per agent
      - sets the current agent for tool-call logs
      - logs step outputs to the tracer
      - emits a lightweight tracer.line event (optional)
    """
    def _cb(step):
        # attribute tokens to this agent (per-scope cost)
        set_scope(agent_label)

        # attribute tool logs to this agent
        set_current_agent(agent_label)

        # ---- OPTIONAL: simple event line (matches your earlier snippet) ----
        if tracer:
            try:
                tracer.line({
                    "event": "agent_step",
                    "scope": agent_label,
                    # keep 'step' out if it’s not JSON-serializable in your tracer;
                    # otherwise, stringify it:
                    "data": getattr(step, "dict", lambda: str(step))()
                             if hasattr(step, "dict") else str(step)
                })
            except Exception:
                # never break execution because of tracing
                pass

        # Try to capture agent's generated text at each step
        # CrewAI step objects vary; cover common attrs safely:
        text = getattr(step, "output", None) \
            or getattr(step, "final", None) \
            or getattr(step, "result", None)

        if tracer and text:
            # log as a step (you’ll still get the final summary below if you want)
            tracer.log_step(agent_name=agent_label,
                            step_kind="llm_output",
                            input=None,
                            output=text,
                            ok=True)

            # If your build exposes a "last step" flag, record final too:
            is_last = getattr(step, "is_last", False) or getattr(step, "final", None) is not None
            if is_last:
                tracer.log_final(agent_name=agent_label, final_output=text)

    return _cb
