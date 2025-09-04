import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import clickhouse_connect

from .prompts import fetch_ids_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class IDMapping(BaseModel):
    """Dictionary mapping country and brand names to their IDs."""

    country_mapping: Dict[str, int] = Field(
        description="Dictionary mapping country names to their IDs. Empty dict if no location specified.",
        default={},
    )
    brand_mapping: Dict[str, int] = Field(
        description="Dictionary mapping brand names to their IDs. Empty dict if no brand specified.",
        default={},
    )


class IDExtractor:
    """Tool for extracting country and brand IDs from user queries."""

    def __init__(self, llm: Optional[Any] = None):
        """Initialize the IDExtractor.

        Args:
            llm: Language model to use for extraction
        """
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.parser = JsonOutputParser(pydantic_object=IDMapping)

    def extract_ids_from_query(
        self, query: str
    ) -> tuple[Dict[str, int], Dict[str, int], Dict[str, int], Dict[str, int]]:
        """Extract country and brand IDs from a user query.

        Args:
            query: The user query to extract IDs from

        Returns:
            A tuple containing:
                - Dictionary mapping all available country names to their IDs
                - Dictionary mapping extracted country names to their IDs
                - Dictionary mapping all available brand names to their IDs
                - Dictionary mapping extracted brand names to their IDs
        """
        try:
            client = clickhouse_connect.get_client(
                host=os.getenv("DB_CLICKHOUSE_HOST"),
                port=int(os.getenv("DB_CLICKHOUSE_PORT")),
                username=os.getenv("DB_CLICKHOUSE_USERNAME"),
                password=os.getenv("DB_CLICKHOUSE_PASSWORD"),
                database=os.getenv("DB_CLICKHOUSE_NAME"),
            )

            result_brands = client.query(os.getenv("QUERY_BRANDS"))
            result_countries = client.query(os.getenv("QUERY_COUNTRIES"))
            countries_map = {name: id for id, name in result_countries.result_rows}
            brands_map = {name: id for id, name in result_brands.result_rows}
        except Exception as e:
            logger.error(f"Error connecting to ClickHouse or fetching data: {str(e)}")
            return {}, {}, {}, {}

        try:
            chain = fetch_ids_prompt | self.llm | self.parser

            result = chain.invoke(
                {
                    "query": query,
                    "countries": countries_map,
                    "brands": brands_map,
                }
            )

            if isinstance(result, dict):
                extracted_countries = result.get("country_mapping", {})
                extracted_brands = result.get("brand_mapping", {})
            else:
                extracted_countries = result.country_mapping
                extracted_brands = result.brand_mapping

            return countries_map, extracted_countries, brands_map, extracted_brands

        except Exception as e:
            logger.error(f"Error extracting IDs: {str(e)}")
            return countries_map, {}, brands_map, {}
