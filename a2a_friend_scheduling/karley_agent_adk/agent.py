# karley_agent_adk/agent.py
import os
from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

PAYSTABL_MCP_URL = os.getenv("PAYSTABL_MCP_URL", "http://localhost:3000/mcp")
PAYSTABL_AGENT_TOKEN = os.getenv("PAYSTABL_AGENT_TOKEN", "")

INSTRUCTION = """
**Role:** You are the PayStabl Payments Agent. Handle x402 payments and simple transfers.
- Use `pay_x402_api(url, agent_token?)` for HTTP 402 paywalls.
- Use `pay_address(to, amount[, agent_token])` for direct transfers.
- Use `get_balance()` and `get_payment_history()` for wallet balance and transaction history respectively.
Stay concise and strictly payment-focused.
"""

def create_agent() -> LlmAgent:
    paystabl_mcp = MCPToolset(
        connection_params=StdioServerParameters(
            command="node",
            args=["stdio_bridge.js"],
            env={
                "MCP_HTTP_URL": PAYSTABL_MCP_URL,
                **({"MCP_BEARER": f"Bearer {PAYSTABL_AGENT_TOKEN}"} if PAYSTABL_AGENT_TOKEN else {})
            },
        )
    )

    return LlmAgent(
        model="gemini-2.0-flash",
        name="PayStabl_Agent",
        instruction=INSTRUCTION,
        tools=[paystabl_mcp],
    )
