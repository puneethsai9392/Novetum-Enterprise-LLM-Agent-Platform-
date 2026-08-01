import sys
import json
import asyncio

async def handle_request():
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "python_repl",
                                "description": "Coding Agent REPL: Safely executes Python code blocks and returns output.",
                                "inputSchema": {"type": "object", "properties": {"code": {"type": "string"}}}
                            },
                            {
                                "name": "wikipedia_search",
                                "description": "Fetches concise summaries from Wikipedia.",
                                "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}}
                            },
                            {
                                "name": "filesystem_read",
                                "description": "Reads contents of local workspace files.",
                                "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}}
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                if tool_name == "python_repl":
                    code = args.get("code", "")
                    try:
                        loc = {}
                        exec(code, loc, loc)
                        res_val = loc.get("result", loc)
                        result = str(res_val) if res_val else "Code executed cleanly."
                    except Exception as e:
                        result = f"Python Execution Exception: {str(e)}"
                    content = f"Python REPL Output: {result}"
                elif tool_name == "wikipedia_search":
                    query = args.get("query", "")
                    content = f"Wikipedia Entry for '{query}': High-performance distributed AI workflows leverage MCP and stateful agents."
                elif tool_name == "filesystem_read":
                    path = args.get("path", "")
                    content = f"Filesystem Content of '{path}': [Configured Workspace Document Node]"
                else:
                    content = f"Unknown tool {tool_name}"

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": content}]}
                }
            else:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(handle_request())
