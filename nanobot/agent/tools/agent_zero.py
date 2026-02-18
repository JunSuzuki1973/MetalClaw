"""Agent Zero tool for nanobot."""

import asyncio
from typing import Any
from nanobot.agent.tools.base import Tool


class AgentZeroTool(Tool):
    """Tool to interact with Agent Zero via Docker commands."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    @property
    def name(self) -> str:
        return "exec_agent_zero"
    
    @property
    def description(self) -> str:
        return "Execute a command in Agent Zero Docker container."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute in Agent Zero"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Agent Zero command via Docker."""
        try:
            process = await asyncio.create_subprocess_shell(
                f"docker exec agent-zero bash -c \"cd /root/.openclaw/workspace/agent-zero && source venv/bin/activate && {command}\"",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            output = stdout.decode("utf-8", errors="replace") if stdout else ""
            error = stderr.decode("utf-8", errors="replace") if stderr else ""
            result = output
            if error:
                result += f"\nError: {error}"
            if process.returncode != 0:
                result += f"\nExit code: {process.returncode}"
            return result
        except asyncio.TimeoutError:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing Agent Zero command: {str(e)}"
