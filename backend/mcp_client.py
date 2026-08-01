import sys
import os
import json
import subprocess
from typing import Dict, Any

class MCPClientHarness:
    def __init__(self):
        self.server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            res_proc = subprocess.run(
                [sys.executable, self.server_script],
                input=(json.dumps(req) + "\n").encode(),
                capture_output=True,
                timeout=5
            )
            stdout = res_proc.stdout
            if not stdout:
                return f"MCP Error: Empty response from tool {tool_name}"
            
            res = json.loads(stdout.decode().strip())
            content = res.get("result", {}).get("content", [])
            if content and isinstance(content, list):
                return content[0].get("text", "")
            return str(res)
        except Exception as e:
            return f"MCP Subprocess Execution Exception: {str(e)}"
