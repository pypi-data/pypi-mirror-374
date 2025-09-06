from functools import wraps
from .tracker import set_scope
from .tool_logging import log_tool_calls
from .crew_helpers import step_cb_factory

def auto_scope(scope_name):
    """Decorator to automatically set scope for agents/tools"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            set_scope(scope_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def setup_agent_logging(agent_name, tracer):
    """Setup logging for an agent with minimal code"""
    def decorator(agent_func):
        @wraps(agent_func)
        def wrapper(*args, **kwargs):
            agent = agent_func(*args, **kwargs)
            agent.step_callback = step_cb_factory(f"agent:{agent_name}", tracer=tracer)
            return agent
        return wrapper
    return decorator

def setup_tool_logging(tool_name, tracer):
    """Setup logging for tools with minimal code"""
    def decorator(tool_class):
        tool_class.run = log_tool_calls(tool_name, tracer=tracer)(tool_class.run)
        return tool_class
    return decorator