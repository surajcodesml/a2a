import os
import random
import requests
from datetime import date, datetime, timedelta
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

def generate_carfax_report(vin: str) -> str:
    """Generates a Carfax report for the given VIN."""
    

def generate_calendar() -> dict[str, list[str]]:
    """Generates a random calendar for the next 7 days."""
    calendar = {}
    today = date.today()
    possible_times = [f"{h:02}:00" for h in range(8, 21)]  # 8 AM to 8 PM

    for i in range(7):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        available_slots = sorted(random.sample(possible_times, 8))
        calendar[date_str] = available_slots
    print("---- Nate's Generated Calendar ----")
    print(calendar)
    print("---------------------------------")
    return calendar


MY_CALENDAR = generate_calendar()

class CarfaxToolInput(BaseModel):
    """Input schema for CarfaxTool."""
    
    vin: str = Field(
        ...,
        description="The Vehicle Identification Number (VIN) to get the Carfax report for. Should be a 17-character alphanumeric string.",
    )
    
class CarfaxTool(BaseTool):
    """Tool to fetch Carfax reports."""
    
    name: str = "Carfax Report Fetcher"
    description: str = (
        "Fetches a Carfax report for a given Vehicle Identification Number (VIN). "
        "Use this to get vehicle history and report details."
    )
    args_schema: Type[BaseModel] = CarfaxToolInput

    def _run(self, vin: str) -> str:
        """Fetches Carfax report for the given VIN."""
        try:
            # Validate VIN format (basic check)
            if not vin or len(vin) != 17:
                return "Invalid VIN format. VIN should be 17 characters long."
            
            # Make API call to the Carfax endpoint
            url = f"https://proxy402.com/rZ0Or4VKA9?vin={vin}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return f"Carfax report for VIN {vin}:\n{response.text}"
            else:
                return f"Failed to fetch Carfax report for VIN {vin}. Status code: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return f"Request timed out while fetching Carfax report for VIN {vin}."
        except requests.exceptions.RequestException as e:
            return f"Error fetching Carfax report for VIN {vin}: {str(e)}"
        except Exception as e:
            return f"Unexpected error occurred: {str(e)}"



class CarfaxTool:
    """Tool to fetch Carfax reports."""
    
    def __init__(self):
        self.name = "Carfax Report Fetcher"
        self.description = "Fetches a Carfax report for a given Vehicle Identification Number (VIN)."

    def run(self, vin: str) -> str:
        """Fetches Carfax report for the given VIN."""
        try:
            # Validate VIN format (basic check)
            if not vin or len(vin) != 17:
                return json.dumps({"error": "Invalid VIN format. VIN should be 17 characters long."})
            
            # Make API call to the Carfax endpoint
            url = f"https://proxy402.com/rZ0Or4VKA9?vin={vin}"
            
            # Headers for authentication (you'll need to add the actual auth values)
            headers = {
                "x402": "payment_response_from_paystabl_agent",  # This should come from PayStabl_Agent
                "Authorization": "Bearer agent_wallet_token"     # This should come from PayStabl_Agent
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Parse JSON response
                carfax_data = response.json()
                return json.dumps(carfax_data, indent=2)
            else:
                return json.dumps({
                    "error": f"Failed to fetch Carfax report for VIN {vin}. Status code: {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            return json.dumps({"error": f"Request timed out while fetching Carfax report for VIN {vin}."})
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Error fetching Carfax report for VIN {vin}: {str(e)}"})
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON response from Carfax API"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error occurred: {str(e)}"})


class CarfaxAgent:
    """Agent that handles Carfax report fetching."""

    SUPPORTED_CONTENT_TYPES = ["text/plain"]

    def __init__(self):
        """Initializes the CarfaxAgent."""
        self.carfax_tool = CarfaxTool()

    def invoke(self, query: str) -> str:
        """Processes the user query and extracts VIN to fetch Carfax report."""
        # Simple VIN extraction - you can make this more sophisticated
        vin = self._extract_vin_from_query(query)
        
        if not vin:
            return json.dumps({
                "error": "No valid VIN found in the query. Please provide a 17-character VIN number."
            })
        
        # Fetch the Carfax report
        result = self.carfax_tool.run(vin)
        return result

    def _extract_vin_from_query(self, query: str) -> str:
        """Extracts VIN from user query."""
        words = query.split()
        for word in words:
            # Basic VIN validation - 17 alphanumeric characters
            if len(word) == 17 and word.isalnum():
                return word.upper()
        return ""
'''
class AvailabilityToolInput(BaseModel):
    """Input schema for AvailabilityTool."""

    date_range: str = Field(
        ...,
        description="The date or date range to check for availability, e.g., '2024-07-28' or '2024-07-28 to 2024-07-30'.",
    )


class AvailabilityTool(BaseTool):
    name: str = "Calendar Availability Checker"
    description: str = (
        "Checks my availability for a given date or date range. "
        "Use this to find out when I am free."
    )
    args_schema: Type[BaseModel] = AvailabilityToolInput

    def _run(self, date_range: str) -> str:
        """Checks my availability for a given date range."""
        dates_to_check = [d.strip() for d in date_range.split("to")]
        start_date_str = dates_to_check[0]
        end_date_str = dates_to_check[-1]

        try:
            start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start > end:
                return (
                    "Invalid date range. The start date cannot be after the end date."
                )

            results = []
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                available_slots = MY_CALENDAR.get(date_str, [])
                if available_slots:
                    availability = f"On {date_str}, I am available at: {', '.join(available_slots)}."
                    results.append(availability)
                else:
                    results.append(f"I am not available on {date_str}.")

            return "\n".join(results)

        except ValueError:
            return (
                "I couldn't understand the date. "
                "Please ask to check availability for a date like 'YYYY-MM-DD'."
            )

'''