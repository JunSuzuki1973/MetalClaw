"""Local shell tool for nanobot."""

import asyncio
from typing import Any
from nanobot.agent.tools.base import Tool


class LocalTool(Tool):
    """Tool to execute local shell commands (no Agent Zero)."""
    
    def __init__(self, timeout: int = 60, working_dir: str = "/root/.nanobot/workspace"):
        self.timeout = timeout
        self.working_dir = working_dir
    
    @property
    def name(self) -> str:
        return "exec_local"
    
    @property
    def description(self) -> str:
        return "Execute a local shell command."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str, **kwargs: Any) -> str:
        """Execute shell command locally."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
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
            return f"Error executing command: {str(e)}"
