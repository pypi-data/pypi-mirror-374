import os
import json
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .prompts import create_dynamic_synthesis_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class ResultSynthesizer:
    """Synthesizes processed API results into a coherent summary."""

    def __init__(self, llm: Optional[Any] = None):
        """Initialize the ResultSynthesizer.

        Args:
            llm: Language model to use for synthesis
        """
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.5-flash-preview-05-20:thinking",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def synthesize_results(
        self,
        query: str,
        all_countries_map: dict,
        country_mapping: dict,
        api_results: Dict[str, List[Dict[str, Any]]],
        explanation: Optional[str] = None,
        brand_mapping: Optional[dict] = None,
    ) -> str:
        """Synthesize API results into a coherent summary.

        Args:
            query: The user query
            all_countries_map: Dictionary mapping all available country names to IDs
            country_mapping: Dictionary mapping extracted country names to IDs
            api_results: Processed API results structured as a plan
            explanation: Optional explanation of the API plan
            brand_mapping: Optional dictionary mapping extracted brand names to IDs

        Returns:
            str: Synthesized summary
        """
        try:
            # Create dynamic synthesis prompt based on available mappings
            brand_mapping = brand_mapping or {}
            synthesis_prompt = create_dynamic_synthesis_prompt(
                country_mapping=country_mapping,
                brand_mapping=brand_mapping,
                all_countries_map=all_countries_map,
            )

            # Create synthesis chain with dynamic prompt
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()

            api_results_str = json.dumps(api_results, indent=2)

            # Prepare template variables
            template_vars = {
                "query": query,
                "api_results": api_results_str,
                "explanation": explanation or "No explanation provided",
            }

            # Add country mapping (either extracted or all countries)
            if country_mapping and country_mapping != {}:
                template_vars["country_mapping"] = (
                    country_mapping or "No location provided"
                )
            else:
                template_vars["all_countries_map"] = (
                    all_countries_map or "No countries available"
                )

            # Add brand mapping if available
            if brand_mapping and brand_mapping != {}:
                template_vars["brand_mapping"] = brand_mapping

            response_text = synthesis_chain.invoke(template_vars)

            return response_text.strip()
        except Exception as e:
            logger.error(f"Error synthesizing results: {str(e)}")
            return f"Failed to synthesize API results: {str(e)}"
