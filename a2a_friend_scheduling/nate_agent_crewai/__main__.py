import logging, uvicorn, os
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agent import create_agent
from dotenv import load_dotenv
from agent_executor import CarfaxAgentExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    host, port = "localhost", 10004  # Carfax Agent
    capabilities = AgentCapabilities(streaming=True)
    skills = [
        AgentSkill(
            id="paid_fetch",
            name="Paid Fetch",
            description="Fetch a listing page. If 402, pay via PayStabl and return raw body.",
            tags=["x402", "payments", "fetch"],
            examples=["paid_fetch { 'url': 'http://localhost:9000/test' }"],
        ),
        AgentSkill(
            id="extract_vehicle_fields",
            name="Extract Vehicle Fields",
            description="Extract VIN/make/model/year/mileage from raw page text.",
            tags=["parse", "vehicle"],
            examples=["extract_vehicle_fields { 'raw': '<html...>' }"],
        ),
    ]

    agent_card = AgentCard(
        name="Carfax Agent",
        description="Fetches listing pages (x402-aware) and extracts key vehicle fields.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text/plain", "application/json"],
        defaultOutputModes=["application/json", "text/plain"],
        capabilities=capabilities,
        skills=skills,
    )

    runner = Runner(
        app_name=agent_card.name,
        agent=create_agent(),
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    handler = DefaultRequestHandler(agent_executor=CarfaxAgentExecutor(runner), task_store=InMemoryTaskStore())
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
    uvicorn.run(app.build(), host=host, port=port)

if __name__ == "__main__":
    main()
