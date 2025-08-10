import os, json, requests
from typing import Optional
from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.tools.python_tool import PythonTool

# === ENV ===
# URL of your local MCP HTTP endpoint (your existing Node server)
PAYSTABL_MCP_URL = os.getenv("PAYSTABL_MCP_URL", "http://localhost:3000/mcp")
# Optional default wallet/agent token (lets you demo without always passing agent_token)
PAYSTABL_AGENT_TOKEN = os.getenv("PAYSTABL_AGENT_TOKEN", "")


def _mcp_call_tool(tool_name: str, params: dict, bearer: Optional[str] = None) -> str:
    """
    Minimal HTTP MCP client to call a tool on the local PayStabl MCP.
    Returns the first text item from the tool result, or raw JSON string as fallback.
    """
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": params},
    }
    headers = {"Content-Type": "application/json"}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"

    r = requests.post(PAYSTABL_MCP_URL, json=body, headers=headers, timeout=60)
    r.raise_for_status()
    out = r.json()
    try:
        # Expecting your MCP to return text content
        return out["result"]["content"][0]["text"]
    except Exception:
        return json.dumps(out)


def pay402_and_fetch(url: str, agent_token: Optional[str] = None) -> str:
    """
    Public tool exposed to other agents via A2A.
    1) Calls MCP tool 'pay_x402_api' with { url, agent_token? }
    2) Returns the raw provider response body as text.
    """
    # Prefer explicit token from caller; otherwise fall back to default demo token
    token_for_mcp = agent_token or PAYSTABL_AGENT_TOKEN or None
    params = {"url": url}
    if agent_token:
        params["agent_token"] = agent_token

    return _mcp_call_tool("pay_x402_api", params, bearer=token_for_mcp)


INSTRUCTION = """
You are the PayStabl Payments Agent.

Skill:
- pay402_and_fetch: Given a URL (HTTP 402 paywalled or free), pay if needed and return the raw response body.

Usage:
- If the user message starts with: pay402_and_fetch { ...json... }
  parse the JSON and call the `pay402_and_fetch` tool with those args.

Rules:
- Stay strictly within payments/fetching.
- Return only the provider's body (no commentary).
"""

def create_agent() -> LlmAgent:
    return LlmAgent(
        model="gemini-2.5-flash-preview-04-17",
        name="PayStabl Agent",
        instruction=INSTRUCTION,
        tools=[
            PythonTool(
                func=pay402_and_fetch,
                name="pay402_and_fetch",
                description="Pays an x402 URL (stablecoins) and returns the raw body text.",
            ),
        ],
    )
