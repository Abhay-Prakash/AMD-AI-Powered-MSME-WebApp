import json
from typing import Any
from app.ai.tools.registry import ToolRegistry
import logging

class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def parse_tool_call(self, text: str) -> dict | None:
        """Looks for a JSON block containing a tool_call."""
        try:
            # We look for a JSON signature {"tool_call": ...}
            # The LLM might output text before or after the JSON.
            start_idx = text.find('{"tool_call":')
            if start_idx == -1:
                return None
                
            # Naive bracket matching to extract the JSON object
            bracket_count = 0
            end_idx = -1
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    bracket_count += 1
                elif text[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
                        
            if end_idx != -1:
                json_str = text[start_idx:end_idx]
                data = json.loads(json_str)
                return data.get("tool_call")
        except Exception as e:
            logging.error(f"Failed to parse tool call: {e}")
            return None
            
        return None

    async def execute(self, tool_call: dict, context_kwargs: dict = None) -> str:
        """Executes the tool and returns the observation as string."""
        name = tool_call.get("name")
        args = tool_call.get("arguments", {})
        
        tool = self.registry.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found."
            
        try:
            # If the tool requires a session or other context, inject it
            # We assume context_kwargs contains db session, etc.
            if context_kwargs:
                import inspect
                sig = inspect.signature(tool)
                for k, v in context_kwargs.items():
                    if k in sig.parameters:
                        args[k] = v
                        
            # Execute async or sync
            import asyncio
            if asyncio.iscoroutinefunction(tool):
                result = await tool(**args)
            else:
                result = tool(**args)
                
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            logging.error(f"Error executing tool {name}: {e}")
            return f"Error executing tool {name}: {str(e)}"
