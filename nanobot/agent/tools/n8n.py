"""n8n workflow management tool for MetalClaw."""

import json
import asyncio
from typing import Any, Optional
from pathlib import Path
from nanobot.agent.tools.base import Tool


class N8nTool(Tool):
    """Tool to manage n8n workflows via REST API."""

    def __init__(
        self,
        config_path: str = "/home/jun/.clawdbot/n8n-config.json",
        timeout: int = 30,
    ):
        self.config_path = config_path
        self.timeout = timeout
        self.api_url: Optional[str] = None
        self.api_key: Optional[str] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load n8n API configuration."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.api_url = config.get('apiUrl')
                self.api_key = config.get('apiKey')

            if not self.api_url or not self.api_key:
                raise ValueError("Invalid config: apiUrl and apiKey are required")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    @property
    def name(self) -> str:
        return "exec_n8n"

    @property
    def description(self) -> str:
        return """Manage n8n workflows via REST API. Available actions:
- list: List all workflows (active=true|false|all)
- get: Get a specific workflow by ID
- create: Create a new workflow from JSON
- update: Update a workflow by ID
- execute: Execute a workflow by ID
- delete: Delete a workflow by ID

Examples:
- List all workflows: list active=all
- Get workflow: get id=abc123
- Execute workflow: execute id=abc123
- Create workflow: create @workflow.json
"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "get", "create", "update", "execute", "delete"],
                    "description": "The action to perform"
                },
                "active": {
                    "type": "string",
                    "enum": ["true", "false", "all"],
                    "description": "Filter by active status (for list action)"
                },
                "id": {
                    "type": "string",
                    "description": "Workflow ID (for get, update, execute, delete)"
                },
                "data": {
                    "type": "string",
                    "description": "JSON data for create/update actions"
                }
            }
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
    ) -> str:
        """Make an HTTP request to n8n API."""
        try:
            import aiohttp
        except ImportError:
            # Fallback to synchronous requests if aiohttp not available
            return await self._make_request_sync(method, endpoint, data)

        url = f"{self.api_url}{endpoint}"
        headers = {
            "accept": "application/json",
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        response_text = await response.text()
                        return self._format_response(response.status, response_text)
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        response_text = await response.text()
                        return self._format_response(response.status, response_text)
                elif method == "PATCH":
                    async with session.patch(url, headers=headers, json=data) as response:
                        response_text = await response.text()
                        return self._format_response(response.status, response_text)
                elif method == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        response_text = await response.text()
                        return self._format_response(response.status, response_text)
        except asyncio.TimeoutError:
            return f"Error: Request timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error making request: {str(e)}"

    async def _make_request_sync(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
    ) -> str:
        """Synchronous fallback using requests library."""
        import requests

        url = f"{self.api_url}{endpoint}"
        headers = {
            "accept": "application/json",
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return f"Error: Unknown method '{method}'"

            return self._format_response(response.status_code, response.text)
        except requests.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error making request: {str(e)}"

    def _format_response(self, status: int, response_text: str) -> str:
        """Format API response."""
        try:
            data = json.loads(response_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return f"Status: {status}\n{formatted}"
        except json.JSONDecodeError:
            return f"Status: {status}\n{response_text}"

    async def execute(self, action: str, **kwargs: Any) -> str:
        """Execute n8n workflow action."""
        if not self.api_url or not self.api_key:
            return "Error: n8n API not configured"

        try:
            if action == "list":
                active = kwargs.get("active", "true")
                if active == "all":
                    endpoint = "/workflows"
                else:
                    endpoint = f"/workflows?active={active}"
                return await self._make_request("GET", endpoint)

            elif action == "get":
                workflow_id = kwargs.get("id")
                if not workflow_id:
                    return "Error: 'id' parameter required for get action"
                return await self._make_request("GET", f"/workflows/{workflow_id}")

            elif action == "create":
                data_str = kwargs.get("data")
                if not data_str:
                    return "Error: 'data' parameter required for create action"
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    return "Error: Invalid JSON in 'data' parameter"
                return await self._make_request("POST", "/workflows", data)

            elif action == "update":
                workflow_id = kwargs.get("id")
                data_str = kwargs.get("data")
                if not workflow_id:
                    return "Error: 'id' parameter required for update action"
                if not data_str:
                    return "Error: 'data' parameter required for update action"
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    return "Error: Invalid JSON in 'data' parameter"
                return await self._make_request("PATCH", f"/workflows/{workflow_id}", data)

            elif action == "execute":
                workflow_id = kwargs.get("id")
                if not workflow_id:
                    return "Error: 'id' parameter required for execute action"
                return await self._make_request("POST", f"/workflows/{workflow_id}/execute")

            elif action == "delete":
                workflow_id = kwargs.get("id")
                if not workflow_id:
                    return "Error: 'id' parameter required for delete action"
                return await self._make_request("DELETE", f"/workflows/{workflow_id}")

            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            return f"Error executing n8n action: {str(e)}"
