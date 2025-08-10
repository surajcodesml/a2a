"""This file serves as the main entry point for the application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import SchedulingAgent
from agent_executor import CarfaxAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def main():
    """Entry point for Carfax Agent"""
    host = "localhost" # DEBUG: Change to Nirajs MCP host"
    port = 10003 #change port
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)
        skill = AgentSkill(
            id="carfax_report_fetcher",
            name="Carfax Report Fetcher",
            description="fetch the carfax report for the car with the given VIN",
            tags=["vin", "report", "vehicle"],
            examples=[
                "What does the Carfax say about this VIN?",
                "Can you fetch the Carfax report for this vehicle?",
            ],
        )
#DEBUG: WHY?
        #agent_host_url = os.getenv("HOST_OVERRIDE") or f"http://{host}:{port}/"
        
        agent_card = AgentCard(
            name="Carfax Agent",
            description=" An agent that fetches Carfax reports for vehicles using VINs.",
            url=f"http://{host}:{port}/", #removed agent_host_url
            version="1.0.0",
            defaultInputModes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=CarfaxAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
