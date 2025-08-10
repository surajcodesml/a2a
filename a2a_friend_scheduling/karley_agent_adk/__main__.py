import logging, os, uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .agent import create_agent
from .agent_executor import PayStablAgentExecutor

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    host = os.getenv("PAYSTABL_AGENT_HOST", "localhost")
    port = int(os.getenv("PAYSTABL_AGENT_PORT", "10002"))

    capabilities = AgentCapabilities(streaming=True)
    skill = AgentSkill(
        id="pay402_and_fetch",
        name="Pay x402 Endpoint",
        description="Pays a 402-paywalled URL (stablecoins) and returns the raw body text. Inputs: { url, agent_token? }",
        tags=["payments", "x402", "stablecoin", "agents"],
        examples=["pay402_and_fetch {'url':'http://localhost:9000/vin/TESTVIN'}"],
    )

    agent_card = AgentCard(
        name="PayStabl Agent",
        description="An agent that executes payments for AI agents (x402 URLs) and returns the provider body.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text/plain", "application/json"],
        defaultOutputModes=["text/plain"],
        capabilities=capabilities,
        skills=[skill],
    )

    runner = Runner(
        app_name=agent_card.name,
        agent=create_agent(),
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    handler = DefaultRequestHandler(agent_executor=PayStablAgentExecutor(runner), task_store=InMemoryTaskStore())
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
    uvicorn.run(app.build(), host=host, port=port)

if __name__ == "__main__":
    main()
