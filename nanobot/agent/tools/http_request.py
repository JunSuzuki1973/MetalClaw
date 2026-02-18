"""HTTP request tool for MetalClaw."""

import asyncio
from typing import Any
from nanobot.agent.tools.base import Tool


class HttpRequestTool(Tool):
    """Tool to make HTTP requests (GET, POST, PUT, DELETE)."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "http_request"

    @property
    def description(self) -> str:
        return """Make HTTP requests to web services. Supports GET, POST, PUT, DELETE methods.
Useful for calling REST APIs, webhooks, or external services.

Parameters:
- url: The full URL to request
- method: HTTP method (GET, POST, PUT, DELETE). Default: GET
- headers: Optional dict of HTTP headers (e.g., {"Content-Type": "application/json"})
- body: Optional request body (for POST, PUT). Can be string or JSON object
- timeout: Optional timeout in seconds. Default: 30"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to request (e.g., 'https://api.example.com/endpoint')"
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method: GET, POST, PUT, DELETE",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers as key-value pairs"
                },
                "body": {
                    "type": "string",
                    "description": "Optional request body for POST/PUT requests"
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30
                }
            },
            "required": ["url"]
        }

    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        body: str | None = None,
        timeout: int | None = None,
        **kwargs: Any
    ) -> str:
        """Execute HTTP request."""
        try:
            import httpx

            timeout_val = timeout or self.timeout

            # Prepare headers
            request_headers = {
                "User-Agent": "MetalClaw/1.0"
            }
            if headers:
                request_headers.update(headers)

            # Make request
            async with httpx.AsyncClient(timeout=timeout_val) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers)
                elif method.upper() == "POST":
                    if body:
                        response = await client.post(url, headers=request_headers, content=body)
                    else:
                        response = await client.post(url, headers=request_headers)
                elif method.upper() == "PUT":
                    if body:
                        response = await client.put(url, headers=request_headers, content=body)
                    else:
                        response = await client.put(url, headers=request_headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=request_headers)
                else:
                    return f"Error: Unsupported HTTP method: {method}"

                # Format response
                result_parts = [
                    f"Status: {response.status_code}",
                    f"Headers: {dict(response.headers)}",
                    ""
                ]

                # Try to parse as JSON
                try:
                    json_response = response.json()
                    result_parts.append("Response (JSON):")
                    result_parts.append(str(json_response))
                except:
                    # Not JSON, return text
                    text_response = response.text
                    # Truncate if too long
                    max_len = 5000
                    if len(text_response) > max_len:
                        text_response = text_response[:max_len] + f"\n... (truncated, {len(text_response) - max_len} more chars)"
                    result_parts.append("Response (Text):")
                    result_parts.append(text_response)

                return "\n".join(result_parts)

        except asyncio.TimeoutError:
            return f"Error: Request timed out after {timeout_val} seconds"
        except Exception as e:
            return f"Error executing HTTP request: {str(e)}"
