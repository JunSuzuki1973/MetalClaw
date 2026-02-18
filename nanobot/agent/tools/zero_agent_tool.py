"""Zero Agent tool for nanobot - uses opencode agent command."""

import asyncio
from typing import Any
from nanobot.agent.tools.base import Tool


class ZeroAgentTool(Tool):
    """Tool to execute OpenCode Agent Zero commands."""
    
    def __init__(self, timeout: int = 60, working_dir: str = "/root/.openclaw/workspace/agent-zero"):
        self.timeout = timeout
        self.working_dir = working_dir
    
    @property
    def name(self) -> str:
        return "exec_zero_agent"
    
    @property
    def description(self) -> str:
        return "Execute OpenCode Agent Zero commands (opencode agent). For example: 'agent list', 'agent attach <url>', or 'opencode agent' for interactive agent management."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The OpenCode Agent Zero command to execute. Examples: 'agent list', 'agent attach http://localhost:4096', 'opencode agent' for interactive management."
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, command: str, **kwargs: Any) -> str:
        """Execute OpenCode Agent Zero command."""
        try:
            # Prepend 'opencode agent' to the command
            full_command = f"opencode agent {command}"
            
            process = await asyncio.create_subprocess_shell(
                full_command,
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
                result += f"\\nError: {error}"
            if process.returncode != 0:
                result += f"\\nExit code: {process.returncode}"
            return result
        except asyncio.TimeoutError:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
