# agent.py
import os
from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, HttpServerParameters

PAYSTABL_MCP_URL = os.getenv("PAYSTABL_MCP_URL", "http://localhost:3000/mcp")
# Token used by your MCP to identify which wallet/agent to use.
# If your MCP doesn't need it, leave empty.
PAYSTABL_AGENT_TOKEN = os.getenv("PAYSTABL_AGENT_TOKEN", "")

INSTRUCTION = """
**Role:** You are the PayStabl Payments Agent. You execute payments for AI agents
and return provider results.

**Tools & Usage**
- `pay_x402_api(url, agent_token?)`: For any URL that returns HTTP 402. Handles fetch → pay → retry.
- `pay_address(to, amount, agent_token?)`: Send direct transfers.
- `get_balance()`, `get_payment_history()`: Wallet status & history.

**Behavior**
- Be concise and stay strictly within payments.
- If inputs are missing, ask once for exactly what's needed (URL, `agent_token`, `to`, `amount`, etc.).
"""

def create_agent() -> LlmAgent:
    """Constructs the ADK agent for PayStabl using an existing HTTP MCP."""
    paystabl_mcp = MCPToolset(
        connection_params=HttpServerParameters(
            url=PAYSTABL_MCP_URL,
            headers=(
                {"Authorization": f"Bearer {PAYSTABL_AGENT_TOKEN}"}
                if PAYSTABL_AGENT_TOKEN else {}
            ),
        )
    )

    return LlmAgent(
        model="gemini-2.5-flash-preview-04-17",
        name="PayStabl_Agent",
        instruction=INSTRUCTION,
        tools=[paystabl_mcp],  # Exposes your MCP tools to the agent
    )
