# PayStabl Agent Demo - X402 Payment Protocol

This project demonstrates a multi-agent application that showcases the X402 payment protocol using PayStabl technology. The system allows agents to automatically handle paywalled content by facilitating secure payments through the PayStabl agent.

## Overview

This application contains three main agents:

- **Host Agent**: The primary orchestrator that facilitates communication between agents
- **Carfax Agent**: Demonstrates X402 payment by fetching vehicle data using VIN numbers from paywalled Carfax content  
- **PayStabl Agent**: Handles the X402 payment protocol when content is behind a paywall (HTTP 402 status)

## How It Works

1. The **Carfax Agent** attempts to fetch vehicle information using a VIN number
2. When encountering a 402 paywall status, the agent automatically calls the **PayStabl Agent**
3. The **PayStabl Agent** processes the payment and retrieves the content
4. The **Carfax Agent** then extracts vehicle details (VIN, make, model, year, mileage) from the retrieved content
5. The **Host Agent** orchestrates the entire process and provides the final results

## Setup and Deployment

### Prerequisites

Before running the application locally, ensure you have the following installed:

1. **uv:** The Python package management tool used in this project. Follow the installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. **Python 3.13:** Python 3.13 is required to run a2a-sdk 
3. **Environment Configuration**

Create a `.env` file in the root of the `a2a_friend_scheduling` directory with the following variables:
```bash
GOOGLE_API_KEY="your_google_api_key_here"
AGENT_TOKEN="your_agent_token_here"
PAYSTABL_CARD_URL="http://localhost:10002"
```

## Run the Agents

You will need to run each agent in a separate terminal window. The first time you run these commands, `uv` will create a virtual environment and install all necessary dependencies before starting the agent.

### Terminal 1: Run PayStabl Agent 
```bash
cd karley_agent_adk
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 2: Run Carfax Agent
```bash
cd nate_agent_crewai  
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 3: Run Host Agent
```bash
cd host_agent_adk
uv venv
source .venv/bin/activate
uv run --active adk web      
```

## Interact with the System

Once all agents are running, you can interact with the Host Agent to demonstrate the X402 payment protocol:

1. The Host Agent will be available at the endpoint shown in the terminal output
2. Send a request to fetch vehicle information using a VIN number
3. Watch as the system automatically handles the paywall through the PayStabl Agent
4. Receive the extracted vehicle information in JSON format

## Project Structure

```
a2a_friend_scheduling/
├── host_agent_adk/          # Host Agent - orchestrates conversations
├── nate_agent_crewai/       # Carfax Agent - fetches vehicle data
├── karley_agent_adk/        # PayStabl Agent - handles X402 payments
└── ai_docs/                 # Documentation and task descriptions
```

## Key Features

- **Automatic Paywall Detection**: Agents automatically detect HTTP 402 status codes
- **Seamless Payment Processing**: PayStabl Agent handles payment without user intervention
- **Content Extraction**: Intelligent parsing of vehicle information from retrieved content
- **Agent Orchestration**: Host Agent manages the entire workflow
- **Secure Token Management**: Environment-based configuration for sensitive data

## References
- [A2A Python SDK](https://github.com/google/a2a-python)
- [A2A Purchasing Concierge Codelab](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1)
- [X402 Payment Protocol Documentation](https://tools.ietf.org/html/rfc7234#section-6.5.2)
