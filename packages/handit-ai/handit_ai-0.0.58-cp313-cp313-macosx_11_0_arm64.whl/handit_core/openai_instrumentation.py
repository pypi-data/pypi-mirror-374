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
    # OpenAI ChatCompletion specific handling - extract just the essential data
    try:
        import openai.types.chat.chat_completion
        if isinstance(x, openai.types.chat.chat_completion.ChatCompletion):
            try:
                # Extract just the essential data, not all the metadata
                result = {
                    "id": getattr(x, 'id', None),
                    "model": getattr(x, 'model', None),
                    "choices": []
                }
                
                if hasattr(x, 'choices') and x.choices:
                    for choice in x.choices:
                        choice_data = {
                            "index": getattr(choice, 'index', None),
                            "finish_reason": getattr(choice, 'finish_reason', None)
                        }
                        if hasattr(choice, 'message') and choice.message:
                            message = choice.message
                            choice_data["message"] = {
                                "role": getattr(message, 'role', None),
                                "content": getattr(message, 'content', None)
                            }
                            # Add tool calls if present
                            if hasattr(message, 'tool_calls') and message.tool_calls:
                                choice_data["message"]["tool_calls"] = str(message.tool_calls)
                        result["choices"].append(choice_data)
                
                # Add usage info if present
                if hasattr(x, 'usage') and x.usage:
                    result["usage"] = {
                        "prompt_tokens": getattr(x.usage, 'prompt_tokens', None),
                        "completion_tokens": getattr(x.usage, 'completion_tokens', None),
                        "total_tokens": getattr(x.usage, 'total_tokens', None)
                    }
                
                return result
            except Exception:
                # Fallback if extraction fails
                pass
    except ImportError:
        # OpenAI not available, continue with other methods
        pass
    
    # Handle OpenAI's NotGiven objects
    try:
        import openai._types
        if isinstance(x, openai._types.NotGiven):
            return None  # Convert NotGiven to None for JSON serialization
    except (ImportError, AttributeError):
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
            # Use exclude_unset=True to avoid NotGiven objects
            return x.model_dump(exclude_unset=True)
        except Exception:
            # Fallback: try without exclude_unset
            try:
                return x.model_dump()
            except Exception:
                # Final fallback if model_dump fails
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
    print("DEBUG: patch_openai() called")
    try:
        import openai
        from openai.resources.chat import completions
    except Exception:
        print("DEBUG: Failed to import openai")
        return
    
    # Prevent double patching
    if getattr(completions.Completions.create, "_handit_patched", False):
        print("DEBUG: OpenAI already patched")
        return
    
    print("DEBUG: Patching OpenAI completions.create")
    
    # Also patch LangChain's structured output calls
    try:
        from langchain_openai import ChatOpenAI
        print("DEBUG: Patching LangChain structured output")
        _patch_langchain_structured_output()
    except ImportError:
        print("DEBUG: LangChain not available for structured output patching")
        pass
    
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

        # Debug: Check message structure
        print(f"DEBUG: Messages in request: {len(messages)} messages")
        for i, msg in enumerate(messages):
            print(f"DEBUG: Message {i}: {type(msg)} - {msg}")
        
        try:
            params_json = to_json_string(params_dict)
            print(f"DEBUG: Successfully serialized params, length: {len(params_json)}")
        except Exception as e:
            print(f"DEBUG: Failed to serialize params: {e}")
            # Fallback serialization for problematic messages
            try:
                safe_params = {
                    "model": model,
                    "message_count": len(messages),
                    "message_types": [str(type(msg)) for msg in messages],
                    "serialization_error": str(e)[:100]
                }
                params_json = json.dumps(safe_params)
                print(f"DEBUG: Using fallback params serialization")
            except Exception:
                params_json = '{"error": "Failed to serialize OpenAI parameters"}'

        print(f"DEBUG: About to call _native_on")
        _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
        print(f"DEBUG: _native_on call completed")
        
        # Suppress profiler during OpenAI call to avoid capturing internal metadata
        _suppress_enter = getattr(_native, "suppress_profiler_enter_py", None)
        _suppress_exit = getattr(_native, "suppress_profiler_exit_py", None)
        if callable(_suppress_enter):
            try:
                _suppress_enter()
            except Exception:
                pass
        
        try:
            # Make the actual call
            result = orig_create(self, **kwargs)
            
            # Calculate timing immediately after the call, before serialization
            t1 = time.time_ns()
            dt_ns = t1 - t0
            
            # Extract just the essential OpenAI response data - skip complex serialization
            try:
                # Check if this is a LegacyAPIResponse that needs to be parsed
                if hasattr(result, 'parse') and callable(result.parse):
                    actual_result = result.parse()
                else:
                    actual_result = result
                
                # Simple extraction approach - just get the content
                if hasattr(actual_result, 'choices') and actual_result.choices and len(actual_result.choices) > 0:
                    first_choice = actual_result.choices[0]
                    content = None
                    role = None
                    
                    if hasattr(first_choice, 'message') and first_choice.message:
                        content = getattr(first_choice.message, 'content', None)
                        role = getattr(first_choice.message, 'role', None)
                    
                    # Build minimal response object
                    response_data = {
                        "content": content,
                        "role": role,
                        "model": getattr(actual_result, 'model', None),
                        "id": getattr(actual_result, 'id', None)
                    }
                    
                    # Add usage if available
                    if hasattr(actual_result, 'usage') and actual_result.usage:
                        response_data["usage"] = {
                            "prompt_tokens": getattr(actual_result.usage, 'prompt_tokens', None),
                            "completion_tokens": getattr(actual_result.usage, 'completion_tokens', None),
                            "total_tokens": getattr(actual_result.usage, 'total_tokens', None)
                        }
                    
                    result_json = json.dumps(response_data, ensure_ascii=False, separators=(",", ":"))
                else:
                    result_json = f"{{\"openai_result\": \"No choices in response\"}}"
                    
            except Exception as serialize_error:
                # Ultimate fallback - just get the content as string
                try:
                    if hasattr(result, 'choices') and result.choices:
                        first_choice = result.choices[0]
                        if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'content'):
                            content = first_choice.message.content
                            result_json = f"{{\"content\": \"{content}\", \"extraction_method\": \"fallback\"}}"
                        else:
                            result_json = f"{{\"error\": \"No message content found\"}}"
                    else:
                        result_json = f"{{\"error\": \"No choices found in OpenAI response\"}}"
                except Exception:
                    result_json = f"{{\"error\": \"Failed to extract OpenAI response data\"}}"
            
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
        finally:
            # Always restore profiler suppression
            if callable(_suppress_exit):
                try:
                    _suppress_exit()
                except Exception:
                    pass
    
    setattr(wrapped_create, "_handit_patched", True)
    setattr(wrapped_create, "_handit_orig", orig_create)
    completions.Completions.create = wrapped_create  # type: ignore

def _patch_langchain_structured_output():
    """Patch LangChain's with_structured_output method to capture structured calls"""
    print("DEBUG: _patch_langchain_structured_output() called")
    try:
        from langchain_openai import ChatOpenAI
        print(f"DEBUG: ChatOpenAI imported: {ChatOpenAI}")
        
        # Prevent double patching
        if hasattr(ChatOpenAI, '_structured_output_patched'):
            print("DEBUG: Structured output already patched")
            return
            
        print("DEBUG: Getting original with_structured_output method")
        original_with_structured_output = ChatOpenAI.with_structured_output
        
        def patched_with_structured_output(self, schema, **kwargs):
            """Patched version of with_structured_output"""
            # Create the structured LLM normally
            structured_llm = original_with_structured_output(self, schema, **kwargs)
            
            # Now patch its invoke method to capture calls
            if hasattr(structured_llm, 'invoke') and not hasattr(structured_llm.invoke, '_handit_patched'):
                original_invoke = structured_llm.invoke
                
                def traced_structured_invoke(input, **invoke_kwargs):
                    """Traced version of structured LLM invoke"""
                    print(f"DEBUG: Structured output invoke called with: {type(input)}")
                    
                    # Extract messages for logging
                    messages = []
                    if hasattr(input, 'get') and 'messages' in input:
                        messages = input['messages']
                    elif hasattr(input, '__iter__') and not isinstance(input, str):
                        messages = list(input)
                    else:
                        messages = [{"role": "user", "content": str(input)}]
                    
                    # Emit call event
                    sid = _active_session_id.get()
                    if sid and _native:
                        _native_on = getattr(_native, "on_call_with_args_py", None)
                        _return_on = getattr(_native, "on_return_with_preview_py", None)
                        
                        if _native_on and _return_on:
                            func_name = "with_structured_output"
                            module_name = "langchain_openai.chat_models"
                            file_name = "<langchain-structured>"
                            line_no = 1
                            t0 = time.time_ns()
                            
                            try:
                                params_json = json.dumps({
                                    "schema": str(schema),
                                    "messages": [str(msg) for msg in messages]
                                })
                            except:
                                params_json = f'{{"schema": "{str(schema)}", "message_count": {len(messages)}}}'
                            
                            print(f"DEBUG: Emitting structured call event")
                            _native_on(sid, func_name, module_name, file_name, line_no, t0, params_json)
                            
                            try:
                                # Make the actual call
                                result = original_invoke(input, **invoke_kwargs)
                                
                                # Calculate timing immediately after the call
                                t1 = time.time_ns()
                                dt_ns = t1 - t0
                                
                                # Extract result data
                                try:
                                    if hasattr(result, 'model_dump'):
                                        result_json = json.dumps(result.model_dump())
                                    else:
                                        result_json = json.dumps(str(result))
                                except:
                                    result_json = f'{{"structured_result": "{str(result)[:500]}"}}'
                                
                                print(f"DEBUG: Emitting structured return event")
                                _return_on(sid, func_name, t1, dt_ns, result_json)
                                return result
                                
                            except Exception as e:
                                # Emit return event for exceptions
                                t1 = time.time_ns()
                                dt_ns = t1 - t0
                                error_json = f'{{"error": "{str(e)[:500]}"}}'
                                try:
                                    _return_on(sid, func_name, t1, dt_ns, error_json)
                                except:
                                    pass
                                raise
                    
                    # Fallback if no session or native
                    return original_invoke(input, **invoke_kwargs)
                
                structured_llm.invoke = traced_structured_invoke
                structured_llm.invoke._handit_patched = True
            
            return structured_llm
        
        ChatOpenAI.with_structured_output = patched_with_structured_output
        ChatOpenAI._structured_output_patched = True
        
    except Exception as e:
        print(f"DEBUG: Failed to patch structured output: {e}")
        pass

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
