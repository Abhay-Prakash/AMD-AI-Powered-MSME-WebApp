import inspect
import json
from typing import Any, Callable

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._descriptions: dict[str, str] = {}
        self._schemas: dict[str, dict] = {}

    def register(self, func: Callable, name: str | None = None, description: str | None = None):
        tool_name = name or func.__name__
        self._tools[tool_name] = func
        self._descriptions[tool_name] = description or inspect.getdoc(func) or "No description provided."
        
        # Simple schema generation from type hints
        sig = inspect.signature(func)
        schema = {
            "name": tool_name,
            "description": self._descriptions[tool_name],
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'session'):
                continue
            
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
                
            schema["parameters"]["properties"][param_name] = {"type": param_type}
            if param.default == inspect.Parameter.empty:
                schema["parameters"]["required"].append(param_name)
                
        self._schemas[tool_name] = schema
        return func

    def get_tool(self, name: str) -> Callable | None:
        return self._tools.get(name)

    def get_schemas(self) -> list[dict]:
        return list(self._schemas.values())
        
    def get_prompt_instructions(self) -> str:
        """Returns XML formatted tool descriptions for the LLM to understand."""
        if not self._schemas:
            return ""
            
        instructions = "You have access to the following tools. To use a tool, return ONLY a JSON block like:\n"
        instructions += '{"tool_call": {"name": "tool_name", "arguments": {"arg1": "val1"}}}\n\n'
        instructions += "Available Tools:\n"
        
        for schema in self._schemas.values():
            instructions += f"- {schema['name']}: {schema['description']}\n"
            instructions += f"  Parameters: {json.dumps(schema['parameters']['properties'])}\n"
            
        return instructions
