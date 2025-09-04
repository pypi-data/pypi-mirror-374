"""OpenAI instrumentation to capture high-level API calls."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
    from . import handit_core_native as _native  # type: ignore
except Exception:  # pragma: no cover
    _native = None  # type: ignore

from . import _active_session_id  # type: ignore

import json, dataclasses, base64
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime

def to_jsonable(x, _depth=0, _seen=None):
     # OpenAI ChatCompletion specific handling
    try:
        import openai.types.chat.chat_completion
        if isinstance(x, openai.types.chat.chat_completion.ChatCompletion):
            try:
                return json.loads(x.model_dump_json())
            except Exception:
                # Fallback if model_dump_json fails
                pass
    except ImportError:
        # OpenAI not available, continue with other methods
        pass

    # Prevent infinite recursion with depth limit and circular reference detection
    if _depth > 10:  # Max recursion depth
        # Even at max depth, try to capture important data as string
        try:
            if hasattr(x, 'content') and x.content:
                return f"<max-depth-reached-content: {x.content}>"
            elif hasattr(x, 'text') and x.text:
                return f"<max-depth-reached-text: {x.text}>"
            elif hasattr(x, 'message') and x.message:
                return f"<max-depth-reached-message: {x.message}>"
            else:
                return f"<max-depth-reached: {str(x)}>"
        except:
            return "<max-depth-reached>"
    
    if _seen is None:
        _seen = set()
    
    # Check for circular references
    obj_id = id(x)
    if obj_id in _seen:
        # Even for circular refs, try to capture important data as string
        try:
            if hasattr(x, 'content') and x.content:
                return f"<circular-ref-content: {x.content}>"
            elif hasattr(x, 'text') and x.text:
                return f"<circular-ref-text: {x.text}>"
            elif hasattr(x, 'message') and x.message:
                return f"<circular-ref-message: {x.message}>"
            else:
                return f"<circular-ref: {str(x)[:500]}>"
        except:
            return "<circular-reference>"
    
    # Handle None first
    if x is None:
        return None
    
    # Built-ins (fast path) - no need to track these in _seen
    if isinstance(x, (str, int, float, bool)):
        return x
    
    # Add to seen set for circular reference detection
    _seen.add(obj_id)
    
    # Pydantic v2 (OpenAI v1+) - with error handling
    if hasattr(x, "model_dump"):
        try:
            return x.model_dump()
        except Exception:
            # Fallback if model_dump fails
            pass
    
    # Pydantic v1 / common libs
    if hasattr(x, "dict"):
        try:
            return x.dict()
        except Exception:
            pass
    
    # Dataclasses
    if dataclasses.is_dataclass(x):
        try:
            return dataclasses.asdict(x)
        except Exception:
            pass
    
    # Collections - pass depth and seen set to prevent infinite recursion
    if isinstance(x, (list, tuple, set, frozenset)):
        try:
            return [to_jsonable(v, _depth + 1, _seen) for v in x]
        except Exception:
            return [str(v) for v in x]
    
    if isinstance(x, dict):
        try:
            return {str(k): to_jsonable(v, _depth + 1, _seen) for k, v in x.items()}
        except Exception:
            return {str(k): str(v) for k, v in x.items()}
    
    # Common non-JSON types
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, (UUID, Decimal)):
        return str(x)
    if isinstance(x, (bytes, bytearray)):
        return base64.b64encode(x).decode("utf-8")
    
    # Last resort with error handling
    if hasattr(x, "__dict__"):
        try:
            return {k: to_jsonable(v, _depth + 1, _seen) for k, v in vars(x).items()}
        except Exception:
            # If serialization fails, try to capture important attributes as strings
            try:
                important_data = {}
                for attr in ['content', 'text', 'message', 'data', 'response', 'choices']:
                    if hasattr(x, attr):
                        val = getattr(x, attr)
                        if val:
                            important_data[attr] = str(val)[:1000]  # Capture first 1000 chars
                if important_data:
                    return important_data
                else:
                    return {"<serialization-error>": str(x)[:500]}
            except:
                return {"<serialization-error>": str(x)[:500]}
    
    # Final fallback
    return str(x)

def to_json_string(obj) -> str:

    try:
        import openai.types.chat.chat_completion
        if isinstance(obj, openai.types.chat.chat_completion.ChatCompletion):
            return json.dumps(obj.model_dump(), ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        print(f"OpenAI not available, continuing with other methods: {e}")
        pass

    return json.dumps(to_jsonable(obj, _depth=0, _seen=None), ensure_ascii=False, separators=(",", ":"))

def patch_openai() -> None:
    """Patch OpenAI to emit custom events for API calls"""
    try:
        import openai
        from openai.resources.chat import completions
    except Exception:
        return
    
    # Prevent double patching
    if getattr(completions.Completions.create, "_handit_patched", False):
        return
    
    orig_create = completions.Completions.create
    
    def wrapped_create(self, **kwargs):  # type: ignore[no-untyped-def]
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        
        # Extract other params for logging (avoid **kwargs conflict)
        other_params = {k: v for k, v in kwargs.items() if k not in ["model", "messages"]}
        params = {
            "model": model,
            "messages": messages,
            **other_params
        }
        # Emit call event
        _native_on = getattr(_native, "on_call_with_args_py", None)
        _return_on = getattr(_native, "on_return_with_preview_py", None)
        if _native_on is None or _return_on is None:
            return
        sid = _active_session_id.get()
        if not sid or _native is None:
            return 0
        
        func_name = "create"  # Just "create"
        module_name = "openai.resources.chat.completions"
        file_name = "<openai-api>"
        line_no = 1
        t0 = time.time_ns()

        if isinstance(params, dict):
            params_dict = params
        else:
            params_dict = params.to_dict()

        params_json = to_json_string(params_dict)

        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        
        try:
            # Make the actual call
            result = orig_create(self, **kwargs)
            
            # Emit return event with safe serialization
            t1 = time.time_ns()
            dt_ns = t1 - t0
            
            # Safe result serialization with fallback
            try:
                result_json = to_json_string(result)
            except Exception as serialize_error:
                # If serialization fails, capture basic info as string
                try:
                    import openai.types.chat.chat_completion
                    if isinstance(result, openai.types.chat.chat_completion.ChatCompletion):
                        result_json = to_json_string(result.model_dump())
                    else:
                        if hasattr(result, 'choices') and result.choices:
                            first_choice = result.choices[0]
                            if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
                                result_json = f"{{\"content\": \"{first_choice.message.content}\", \"serialization_error\": \"{str(serialize_error)[:100]}\"}}"
                            else:
                                result_json = f"{{\"openai_result\": \"{str(result)[:500]}\", \"serialization_error\": \"{str(serialize_error)[:100]}\"}}"
                        else:
                            result_json = f"{{\"openai_result\": \"{str(result)[:500]}\", \"serialization_error\": \"{str(serialize_error)[:100]}\"}}"
                except Exception:
                    result_json = f"{{\"serialization_error\": \"Failed to serialize OpenAI result: {str(serialize_error)[:100]}\"}}"
            
            _return_on(sid, func_name, t1, dt_ns, result_json)
            
            return result
            
        except Exception as e:
            # Emit return event for exceptions too
            t1 = time.time_ns()
            dt_ns = t1 - t0
            error_json = f"{{\"error\": \"{str(e)[:500]}\"}}"
            try:
                _return_on(sid, func_name, t1, dt_ns, error_json)
            except:
                pass  # Don't let logging errors break the original exception
            raise
    
    setattr(wrapped_create, "_handit_patched", True)
    setattr(wrapped_create, "_handit_orig", orig_create)
    completions.Completions.create = wrapped_create  # type: ignore

def patch_openai_client_for_langchain():
    """Patch LangChain at the right level - when models are actually imported"""
    
    # Strategy: Patch the module import system to catch LangChain models when imported
    import sys
    import importlib.util
    
    # Store original import
    original_import = __builtins__['__import__']
    
    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Custom import that patches LangChain models as they're imported"""
        
        # Call original import first
        module = original_import(name, globals, locals, fromlist, level)
        
        # Check if this is a LangChain model import
        if name == 'langchain_openai' or (fromlist and 'ChatOpenAI' in fromlist):
            try:
                from langchain_openai import ChatOpenAI
                if not hasattr(ChatOpenAI, '_handit_patched'):
                    _patch_chatopenai()
            except:
                pass
        
        if name == 'langchain_anthropic' or (fromlist and 'ChatAnthropic' in fromlist):
            try:
                from langchain_anthropic import ChatAnthropic
                if not hasattr(ChatAnthropic, '_handit_patched'):
                    _patch_chatanthropic()
            except:
                pass
        
        return module
    
    # Apply the import hook
    __builtins__['__import__'] = traced_import

def _patch_chatopenai():
    """Actually patch ChatOpenAI.ainvoke"""
    try:
        from langchain_openai import ChatOpenAI
        
        original_ainvoke = ChatOpenAI.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            """Traced ChatOpenAI.ainvoke"""
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'gpt-3.5-turbo'))
            
            # Convert input to messages
            if hasattr(input, '__iter__') and not isinstance(input, str):
                messages = list(input)
            else:
                messages = [{"role": "user", "content": str(input)}]
            
            t0_ns = _emit_openai_call("ChatOpenAI.ainvoke", model_name, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                _emit_openai_return(t0_ns, "ChatOpenAI.ainvoke", result)
                return result
            except Exception as error:
                _emit_openai_return(t0_ns, "ChatOpenAI.ainvoke", None, str(error))
                raise
        
        ChatOpenAI.ainvoke = traced_ainvoke
        ChatOpenAI._handit_patched = True
        
    except Exception as e:
        pass

def _patch_chatanthropic():
    """Actually patch ChatAnthropic.ainvoke"""
    try:
        from langchain_anthropic import ChatAnthropic
        
        original_ainvoke = ChatAnthropic.ainvoke
        
        async def traced_ainvoke(self, input, config=None, **kwargs):
            model_name = getattr(self, 'model_name', getattr(self, 'model', 'claude'))
            
            if hasattr(input, '__iter__') and not isinstance(input, str):
                messages = list(input)
            else:
                messages = [{"role": "user", "content": str(input)}]
            
            t0_ns = _emit_openai_call("ChatAnthropic.ainvoke", model_name, messages, **kwargs)
            
            try:
                result = await original_ainvoke(self, input, config, **kwargs)
                _emit_openai_return(t0_ns, "ChatAnthropic.ainvoke", result)
                return result
            except Exception as error:
                _emit_openai_return(t0_ns, "ChatAnthropic.ainvoke", None, str(error))
                raise
        
        ChatAnthropic.ainvoke = traced_ainvoke
        ChatAnthropic._handit_patched = True
        
    except Exception as e:
        pass
