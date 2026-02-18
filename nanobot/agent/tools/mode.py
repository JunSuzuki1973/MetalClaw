"""Mode switching tool for nanobot."""

from typing import Any
from nanobot.agent.tools.base import Tool


class ModeTool(Tool):
    """Tool to switch between different interaction modes."""

    def __init__(self, context):
        self.context = context

    @property
    def name(self) -> str:
        return "switch_mode"

    @property
    def description(self) -> str:
        return """Switch between different interaction modes:
- local: Local shell commands (no Agent Zero)
- agent: Agent Zero via Docker commands
- default: Default LLM chat mode"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Mode to switch to (local/agent/default)",
                    "enum": ["local", "agent", "default"]
                }
            },
            "required": ["mode"]
        }

    async def execute(self, mode: str, **kwargs: Any) -> str:
        """Switch mode and return confirmation message."""
        if mode not in ["local", "agent", "default"]:
            return "Error: Invalid mode. Use 'local', 'agent', or 'default'."

        # Save mode to context
        self.context.data["mode"] = mode

        mode_emoji = {
            "local": "💻",
            "agent": "🤖",
            "default": "💬"
        }

        mode_desc = {
            "local": "Local shell commands",
            "agent": "Agent Zero via Docker",
            "default": "Default LLM chat"
        }

        return f"Switched to {mode_desc[mode]} mode {mode_emoji[mode]}\n" \
               f"Next message will be processed in {mode} mode."
