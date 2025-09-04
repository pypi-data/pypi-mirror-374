import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Literal
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from datetime import datetime

from .agent import BlaskAPIAgent
from .prompts import planning_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class APIAction(BaseModel):
    """An API action to take."""

    reason: str = Field(
        description="A clear reason that links this call to the user's request, explains what needs to be extracted from the expected data, and documents the thought process for choosing this endpoint over alternatives (e.g., 'Selected /v1/metrics over /v1/stats because we need granular time-series data rather than aggregates')."
    )
    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    path: str = Field(description="API endpoint path")
    priority: int = Field(
        description="Lower number = higher priority. Enrichment calls should have high priority."
    )
    dependencies: List[str] = Field(
        description="List of dependencies. Description of data needed from previous calls, if any. E.g., 'Needs country IDs from priority 2 call'"
    )
    time_range: Optional[Dict[str, str]] = Field(
        None, description="Optional time range with start and end dates"
    )


class APIPlan(BaseModel):
    """The API action plan."""

    explanation: str = Field(description="Overall explanation of the plan")
    actions: List[APIAction] = Field(description="List of API actions to take")


class PlannerTool:
    """Tool for planning API actions based on Swagger endpoints."""

    def __init__(
        self, api_agent: Optional[BlaskAPIAgent] = None, llm: Optional[Any] = None
    ):
        """Initialize the PlannerTool.

        Args:
            api_agent: BlaskAPIAgent instance
            llm: Language model to use for planning
        """
        self.api_agent = api_agent or BlaskAPIAgent()
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.5-flash",  # perplexity/r1-1776
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.parser = JsonOutputParser(pydantic_object=APIPlan)

    def get_api_plan(
        self,
        query: str,
        country_mapping: Optional[Dict[str, int]] = None,
        brand_mapping: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[Dict], str]:
        """Generate an API action plan based on the query.

        Args:
            query: The user query to plan for
            country_mapping: Optional dictionary mapping country names to their IDs
            brand_mapping: Optional dictionary mapping brand names to their IDs

        Returns:
            Tuple[List[Dict], str]: A tuple of (actions list, explanation)
        """
        country_ids = None
        if country_mapping:
            country_ids = list(country_mapping.values())

        brand_ids = None
        if brand_mapping:
            brand_ids = list(brand_mapping.values())

        endpoints_summary = self._format_endpoints_summary(country_mapping)
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            format_instructions = self.parser.get_format_instructions()
            chain = planning_prompt | self.llm | self.parser
            plan = chain.invoke(
                {
                    "query": query,
                    "endpoints_summary": endpoints_summary,
                    "current_date": current_date,
                    "format_instructions": format_instructions,
                    "country_ids": country_ids,
                    "brand_ids": brand_ids,
                }
            )

            if isinstance(plan, dict):
                actions = plan.get("actions", [])
                explanation = plan.get("explanation", "No explanation provided")
            else:
                actions = [action.dict() for action in plan.actions]
                explanation = plan.explanation

            return actions, explanation

        except Exception as e:
            print(f"Error generating API plan: {str(e)}")
            logger.error(f"Error generating API plan: {str(e)}")
            return [], f"Error generating plan: {str(e)}"

    def _format_endpoints_summary(
        self, country_mapping: Optional[Dict[str, int]] = None
    ) -> str:
        """Format the endpoints summary for the prompt.

        Returns:
            str: Formatted endpoints summary
        """
        summary = self.api_agent.get_endpoint_summary()

        # Stop list - endpoints to never use
        stop_list = ["/v1/global-brands/search"]

        country_path_list = ["{countryId}", "countries/{id}"]
        country_param_list = ["id", "countryId", "countryIds"]

        formatted_summary = ""
        for category, endpoints in summary.items():
            category_endpoints_added = False
            category_header = f"CATEGORY: {category}\n"

            for endpoint in endpoints:
                if endpoint["path"] in stop_list:
                    continue

                if not country_mapping:
                    if any(
                        country_path in endpoint["path"]
                        for country_path in country_path_list
                    ):
                        continue

                    endpoint_details = self.api_agent.get_endpoint_details(
                        endpoint["path"], endpoint["method"]
                    )

                    parameters = endpoint_details.get("parameters", [])
                    if any(
                        param.get("name") in country_param_list for param in parameters
                    ):
                        continue

                if endpoint["method"] != "GET":
                    continue

                endpoint_details = self.api_agent.get_endpoint_details(
                    endpoint["path"], endpoint["method"]
                )

                description = endpoint_details.get("description")
                if not description:
                    continue

                if not category_endpoints_added:
                    formatted_summary += category_header
                    category_endpoints_added = True

                formatted_summary += (
                    f"- {endpoint['method']} {endpoint['path']}: {description}\n"
                )

            if category_endpoints_added:
                formatted_summary += "\n"

        return formatted_summary
