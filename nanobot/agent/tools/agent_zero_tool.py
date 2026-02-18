"""Agent Zero integration tool for MetalClaw."""

import asyncio
import json
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class AgentZeroTool(Tool):
    """
    Tool to communicate with Agent Zero via HTTP API.

    This tool allows MetalClaw to send messages to Agent Zero and receive responses.
    Agent Zero runs in a Docker container and exposes an HTTP API on port 5000.
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.api_url = "http://localhost:5000"
        # API key computed from: runtime_id::username:password
        # Current runtime_id: dc92d21faae8c49d
        self.api_key = "rkjGYeREjK+zDV9K"
        self._csrf_token = None
        self._cookies = {}

    @property
    def name(self) -> str:
        return "exec_agent_zero"

    @property
    def description(self) -> str:
        return """Execute commands in Agent Zero environment via HTTP API.

Agent Zero is a powerful AI agent with tools for:
- Code execution and file operations
- Web browsing and scraping
- Task automation and scheduling
- Multi-agent collaboration

Use this for complex coding tasks, web automation, or when you need advanced AI capabilities.

Parameters:
- message: The message to send to Agent Zero
- context: Optional context ID to continue a conversation (default: new context)
- timeout: Timeout in seconds for the request (default: 120)"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message or task to send to Agent Zero"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context ID to continue an existing conversation"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds for the request",
                    "default": 120
                }
            },
            "required": ["message"]
        }

    async def execute(
        self,
        message: str,
        context: str | None = None,
        timeout: int = 120,
        **kwargs: Any
    ) -> str:
        """Execute command in Agent Zero."""
        try:
            import httpx

            # Step 1: Get CSRF token
            csrf_url = f"{self.api_url}/csrf_token"
            async with httpx.AsyncClient(timeout=10) as client:
                csrf_response = await client.get(
                    csrf_url,
                    headers={"Origin": self.api_url}
                )

                if csrf_response.status_code != 200:
                    return f"Error: Failed to get CSRF token (status {csrf_response.status_code})"

                csrf_data = csrf_response.json()
                if not csrf_data.get("ok"):
                    return f"Error: {csrf_data.get('error', 'Unknown CSRF error')}"

                self._csrf_token = csrf_data["token"]

                # Extract cookies from response
                self._cookies = dict(csrf_response.cookies)

            # Step 2: Send message to Agent Zero
            message_url = f"{self.api_url}/message"
            payload = {
                "text": message
            }
            if context:
                payload["context"] = context

            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key,
                "X-CSRF-Token": self._csrf_token,
                "Origin": self.api_url
            }

            async with httpx.AsyncClient(timeout=timeout) as client:
                message_response = await client.post(
                    message_url,
                    json=payload,
                    headers=headers,
                    cookies=self._cookies
                )

                if message_response.status_code != 200:
                    return f"Error: Failed to send message (status {message_response.status_code})"

                result = message_response.json()

                # Format response
                response_message = result.get("message", "")
                context_id = result.get("context", "")

                output = [
                    f"🔌 Agent Zero Response (Context: {context_id})",
                    "",
                    response_message
                ]

                return "\n".join(output)

        except asyncio.TimeoutError:
            return f"Error: Request timed out after {timeout} seconds"
        except json.JSONDecodeError as e:
            return f"Error: Failed to parse JSON response: {str(e)}"
        except Exception as e:
            return f"Error communicating with Agent Zero: {str(e)}"
