import os, re, requests, json
from typing import Optional, Dict, Any
from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.tools import FunctionTool



PAYSTABL_CARD_URL = os.getenv("PAYSTABL_CARD_URL", "http://localhost:10002")

def _a2a_simple_task(agent_base_url: str, message: str, timeout: int = 90) -> str:
    """Minimal A2A /tasks/simple client expecting first text part back."""
    import requests
    url = agent_base_url.rstrip("/") + "/tasks/simple"
    r = requests.post(url, json={"message": message}, timeout=timeout)
    r.raise_for_status()
    if r.headers.get("content-type","").startswith("application/json"):
        data = r.json()
        try:
            for art in data["result"]["artifacts"]:
                for part in art.get("parts", []):
                    if part.get("type") == "text" and part.get("text"):
                        return part["text"]
        except Exception:
            pass
    return r.text


def paid_fetch(url: str, agent_token: Optional[str] = None) -> str:
    """GET url; if 402 (x402), call PayStabl Agent to pay and fetch; return raw body."""
    url = "https://proxy402.com/rZ0Or4VKA9?vin=JHMGE8H58DC009182"
    r = requests.get(url, validate_certs=True, timeout=30)
    
    if r.status_code != 402:
        return r.text
    
    token = agent_token or os.getenv("AGENT_TOKEN")
    payload = {"url": url , "agent_token": token}
    msg = f"pay402_and_fetch {payload}"
    return _a2a_simple_task(PAYSTABL_CARD_URL, msg)
paid_fetch_tool = FunctionTool(func=paid_fetch)

def extract_vehicle_fields(raw: str) -> Dict[str, Any]:
    """Very light extractor—good enough for demo. Improve as needed."""
    def grab(pattern, text):
        m = re.search(pattern, text, re.I)
        return m.group(1).strip() if m else None

    # naive grabs
    vin = grab(r"\bVIN[:\s]*([A-HJ-NPR-Z0-9]{11,17})\b", raw)
    make = grab(r"\bMake[:\s]*([A-Za-z0-9\- ]{2,30})\b", raw) or grab(r"\b([A-Z][a-z]+)\s+[A-Z][a-z]+\b", raw)
    model = grab(r"\bModel[:\s]*([A-Za-z0-9\- ]{2,30})\b")
    year = grab(r"\b(20\d{2}|19\d{2})\b", raw)
    mileage = grab(r"\b(\d{1,3}(?:,\d{3})*)\s*(?:miles|mi)\b", raw)

    return {
        "vin": vin,
        "make": make,
        "model": model,
        "year": year,
        "mileage": mileage,
        "raw_len": len(raw),
    }
extract_vehicle_fields_tool = FunctionTool(func=extract_vehicle_fields)
INSTRUCTION = """
You are the Carfax Agent. Your job:
1) Fetch listing/VIN pages (use `paid_fetch`). If the page is 402-paywalled, `paid_fetch` will route payment via PayStabl.
2) Extract VIN, make, model, year, and mileage with `extract_vehicle_fields`.
3) Return a concise JSON summary. No extra commentary.
"""

def create_agent() -> LlmAgent:
    return LlmAgent(
        model="gemini-2.0-flash",
        name="Carfax_Agent",
        instruction=INSTRUCTION,
        tools=[
            paid_fetch_tool,
            extract_vehicle_fields_tool,
        ]
    )