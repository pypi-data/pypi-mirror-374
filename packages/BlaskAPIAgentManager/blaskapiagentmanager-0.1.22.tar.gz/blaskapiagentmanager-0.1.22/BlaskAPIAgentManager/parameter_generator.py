import os
import json
import logging
from typing import Dict, List, Optional, Any, Literal
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from datetime import datetime

from .agent import BlaskAPIAgent
from .prompts import parameter_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class APIParam(BaseModel):
    """API parameter for API call."""

    name: str = Field(description="Parameter name")
    value: Any = Field(description="Parameter value")


class APIParams(BaseModel):
    """Parameters for API call."""

    path_params: Optional[List[APIParam]] = Field(
        default=None, description="Path parameters"
    )
    query_params: Optional[List[APIParam]] = Field(
        default=None, description="Query parameters"
    )
    body: Optional[Dict[str, Any]] = Field(default=None, description="Request body")


class APICallConfig(BaseModel):
    """Configuration for an API call."""

    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    path: str = Field(description="API endpoint path")
    time_range: Optional[Dict[str, str]] = Field(
        None, description="Optional time range with start and end dates"
    )
    granularity: Optional[Literal["hour", "day", "month"]] = Field(
        "month", description="Optional granularity for time-based data"
    )
    sort_by: Optional[Literal["ggr", "ftd", "yoy", "mom", "market_share"]] = Field(
        "ggr", description="Optional sort parameter with predefined values"
    )
    sort_order: Optional[Literal["ASC", "DESC"]] = Field(
        None, description="Optional sort order (ASC or DESC)"
    )
    sort: Optional[Literal["ggr", "ftd", "yoy", "mom", "market_share"]] = Field(
        "ggr", description="Optional sort parameter with predefined values"
    )
    search: Optional[str] = Field(
        None, description="Optional search parameter for brand name"
    )
    page: Optional[int] = Field(None, description="Optional page number for pagination")
    per_page: Optional[int] = Field(
        None, description="Optional number of items per page"
    )
    brands_ids: Optional[str] = Field(
        None, description="Optional comma-separated list of brand IDs"
    )
    brands_id: Optional[int] = Field(None, description="Optional brand ID")
    country_id: Optional[int] = Field(None, description="Optional country ID")
    country_ids: Optional[str] = Field(
        None, description="Optional comma-separated list of country IDs"
    )


class ParameterGenerator:
    """Tool for generating parameters for API endpoints."""

    def __init__(
        self, api_agent: Optional[BlaskAPIAgent] = None, llm: Optional[Any] = None
    ):
        """Initialize the ParameterGenerator.

        Args:
            api_agent: BlaskAPIAgent instance
            llm: Language model to use for parameter generation
        """
        self.api_agent = api_agent or BlaskAPIAgent()
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.5-flash",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.param_parser = JsonOutputParser(pydantic_object=APIParams)
        self.entity_id_tracker = {
            "countryId": None,
            "brandId": None,
            "countryIds": None,
            "brandsIds": None,
        }

    def generate_parameters(
        self,
        query: str,
        endpoint_info: Dict,
        config: APICallConfig,
        all_results: Optional[Dict] = None,
        country_ids: Optional[List[int]] = None,
    ) -> APIParams:
        """Generate parameters for an API call.

        Args:
            query: The user query
            endpoint_info: Detailed information about the endpoint
            config: Configuration for the API call
            all_results: Previous API results
            country_ids: Optional list of country IDs extracted from the query

        Returns:
            APIParams: Parameters for the API call
        """
        try:
            endpoint_info_str = self._prepare_endpoint_info(endpoint_info, config)
            current_date = datetime.now().strftime("%Y-%m-%d")

            all_results_str = "No previous results available."
            if all_results:
                all_results_str = (
                    f"Previous API results:\n{json.dumps(all_results, indent=2)}"
                )
            endpoint_info_with_tracking = json.loads(endpoint_info_str)

            if country_ids:
                endpoint_info_with_tracking["country_ids"] = country_ids

            endpoint_info_str = json.dumps(endpoint_info_with_tracking, indent=2)
            format_instructions = self.param_parser.get_format_instructions()

            chain = parameter_prompt | self.llm | self.param_parser
            params = chain.invoke(
                {
                    "query": query,
                    "endpoint_info": endpoint_info_str,
                    "current_date": current_date,
                    "previous_results": all_results_str,
                    "format_instructions": format_instructions,
                }
            )

            # Pass endpoint_info so that _process_parameters can choose correct date param naming
            result_params = self._process_parameters(
                params, config, endpoint_info, query
            )

            if country_ids and not any(
                p.name == "countryIds" for p in result_params.query_params
            ):
                country_ids_str = ",".join(map(str, country_ids))

                single_id_endpoints = ["/v1/brands", "/v1/countries/{countryId}/brands"]

                if any(endpoint in config.path for endpoint in single_id_endpoints):
                    result_params.query_params.append(
                        APIParam(name="countryId", value=country_ids_str)
                    )
                else:
                    result_params.query_params.append(
                        APIParam(name="countryIds", value=country_ids_str)
                    )

            if "{countryId}" in config.path and not any(
                p.name == "countryId" for p in result_params.path_params
            ):
                if self.entity_id_tracker["countryId"]:
                    result_params.path_params.append(
                        APIParam(
                            name="countryId", value=self.entity_id_tracker["countryId"]
                        )
                    )
                elif any(p.name == "countryIds" for p in result_params.query_params):
                    for param in result_params.query_params:
                        if param.name == "countryIds":
                            # Use the first ID from the comma-separated list
                            first_id = str(param.value).split(",")[0].strip()
                            result_params.path_params.append(
                                APIParam(name="countryId", value=first_id)
                            )
                            break
                elif country_ids:
                    result_params.path_params.append(
                        APIParam(name="countryId", value=str(country_ids[0]))
                    )

            if "{brandId}" in config.path and not any(
                p.name == "brandId" for p in result_params.path_params
            ):
                if self.entity_id_tracker["brandId"]:
                    brand_id_value = self.entity_id_tracker["brandId"]
                    if isinstance(brand_id_value, list):
                        brand_ids_str = ",".join(map(str, brand_id_value))
                    elif "," in str(brand_id_value):
                        brand_ids_str = str(brand_id_value)
                    else:
                        brand_ids_str = str(brand_id_value)
                    result_params.path_params.append(
                        APIParam(name="brandId", value=brand_ids_str)
                    )
                elif any(p.name == "brandsIds" for p in result_params.query_params):
                    for param in result_params.query_params:
                        if param.name == "brandsIds":
                            result_params.path_params.append(
                                APIParam(name="brandId", value=str(param.value))
                            )
                            break
                elif self.entity_id_tracker["brandsIds"]:
                    result_params.path_params.append(
                        APIParam(
                            name="brandId", value=self.entity_id_tracker["brandsIds"]
                        )
                    )

            self._update_entity_tracker_from_params(result_params)
            return result_params

        except Exception as e:
            logger.error(f"Error generating parameters: {str(e)}")
            return APIParams(path_params=[], query_params=[], body={})

    def _prepare_endpoint_info(self, endpoint_info: Dict, config: APICallConfig) -> str:
        """Prepare endpoint info for LLM input.

        Args:
            endpoint_info: Endpoint information
            config: API call configuration

        Returns:
            str: Formatted endpoint info
        """
        endpoint_info_with_context = endpoint_info.copy()

        additional_context = {}
        if config.time_range:
            additional_context["time_range"] = config.time_range
        if config.granularity:
            additional_context["granularity"] = config.granularity
        if config.sort_by:
            additional_context["sort_by"] = config.sort_by
        if config.sort_order:
            additional_context["sort_order"] = config.sort_order
        if config.sort:
            additional_context["sort"] = config.sort
        if config.search:
            additional_context["search"] = config.search
        if config.page is not None:
            additional_context["page"] = config.page
        if config.per_page is not None:
            additional_context["per_page"] = config.per_page
        if config.brands_ids:
            additional_context["brands_ids"] = config.brands_ids

        if additional_context:
            endpoint_info_with_context["additional_context"] = additional_context

        return json.dumps(endpoint_info_with_context, indent=2)

    def _process_parameters(
        self, params: Any, config: APICallConfig, endpoint_info: Dict, query: str = None
    ) -> APIParams:
        """Process and normalize parameters.

        Args:
            params: Raw parameters from LLM
            config: API call configuration

        Returns:
            APIParams: Processed parameters
        """
        result_params = APIParams(path_params=[], query_params=[], body={})

        if isinstance(params, dict):
            if "path_params" in params and params["path_params"]:
                for param in params["path_params"]:
                    if isinstance(param, dict) and "name" in param and "value" in param:
                        result_params.path_params.append(
                            APIParam(name=param["name"], value=param["value"])
                        )

            if "query_params" in params and params["query_params"]:
                # Track parameter names to avoid duplicates
                existing_param_names = set()

                for param in params["query_params"]:
                    if isinstance(param, dict) and "name" in param and "value" in param:
                        param_name = param["name"]
                        param_value = param["value"]

                        # Skip duplicate parameters (keep only the first occurrence)
                        if param_name in existing_param_names:
                            logger.warning(
                                f"Skipping duplicate parameter: {param_name}={param_value}"
                            )
                            continue

                        existing_param_names.add(param_name)

                        single_id_endpoints = [
                            "/v1/brands",
                            "/v1/countries/{countryId}/brands",
                        ]
                        is_single_id_endpoint = any(
                            endpoint in config.path for endpoint in single_id_endpoints
                        )

                        if (
                            param_name == "countryId"
                            and "," in str(param_value)
                            and not is_single_id_endpoint
                        ):
                            result_params.query_params.append(
                                APIParam(name="countryIds", value=param_value)
                            )
                            continue

                        elif param_name == "brandId" and "," in str(param_value):
                            result_params.query_params.append(
                                APIParam(name="brandsIds", value=param_value)
                            )
                            continue

                        result_params.query_params.append(
                            APIParam(name=param_name, value=param_value)
                        )

            if "body" in params and params["body"]:
                result_params.body = params["body"]

        elif isinstance(params, APIParams):
            if params.path_params:
                result_params.path_params = params.path_params
            if params.query_params:
                # Track parameter names to avoid duplicates
                existing_param_names = set()

                for param in params.query_params:
                    param_name = param.name
                    param_value = param.value

                    # Skip duplicate parameters (keep only the first occurrence)
                    if param_name in existing_param_names:
                        logger.warning(
                            f"Skipping duplicate parameter: {param_name}={param_value}"
                        )
                        continue

                    existing_param_names.add(param_name)

                    single_id_endpoints = [
                        "/v1/brands",
                        "/v1/countries/{countryId}/brands",
                    ]
                    is_single_id_endpoint = any(
                        endpoint in config.path for endpoint in single_id_endpoints
                    )

                    if (
                        param_name == "countryId"
                        and "," in str(param_value)
                        and not is_single_id_endpoint
                    ):
                        result_params.query_params.append(
                            APIParam(name="countryIds", value=param_value)
                        )
                        continue

                    elif param_name == "brandId" and "," in str(param_value):
                        result_params.query_params.append(
                            APIParam(name="brandsIds", value=param_value)
                        )
                        continue

                    result_params.query_params.append(param)
            if params.body:
                result_params.body = params.body

        # Determine which date parameter naming style the endpoint expects
        endpoint_param_names = {
            param.get("name")
            for param in endpoint_info.get("parameters", [])
            if isinstance(param, dict) and param.get("name")
        }

        # Prefer snake_case if the endpoint defines it, otherwise default to camelCase
        use_snake_case_dates = any(
            name in endpoint_param_names for name in ["date_from", "date_to"]
        )

        date_param_names_present = [p.name for p in result_params.query_params]

        # Process time range from config if not already present in LLM-generated params
        if config.time_range and not any(
            name in date_param_names_present
            for name in ["date_from", "date_to", "dateFrom", "dateTo"]
        ):
            start_date = (
                config.time_range.get("dateFrom")
                or config.time_range.get("start_date")
                or config.time_range.get("start")
            )
            end_date = (
                config.time_range.get("dateTo")
                or config.time_range.get("end_date")
                or config.time_range.get("end")
            )

            if start_date:
                if " " not in start_date:
                    start_datetime = f"{start_date} 00:00:00"
                else:
                    start_datetime = start_date
                result_params.query_params.append(
                    APIParam(
                        name="date_from" if use_snake_case_dates else "dateFrom",
                        value=start_datetime,
                    )
                )

            if end_date:
                if " " not in end_date:
                    end_datetime = f"{end_date} 23:59:59"
                else:
                    end_datetime = end_date
                result_params.query_params.append(
                    APIParam(
                        name="date_to" if use_snake_case_dates else "dateTo",
                        value=end_datetime,
                    )
                )

        param_names = [p.name for p in result_params.query_params]

        # Add default parameters if not already present
        if (
            "/brands/tops" in config.path
            or "/ggr" in config.path
            or "/market-share" in config.path
            or "/trends" in config.path
        ):
            if "granularity" not in param_names:
                # Default to "month" if not specified
                granularity_value = config.granularity or "month"
                result_params.query_params.append(
                    APIParam(name="granularity", value=granularity_value)
                )
        elif config.granularity and "granularity" not in param_names:
            result_params.query_params.append(
                APIParam(name="granularity", value=config.granularity)
            )

        if config.sort_by and "sort_by" not in param_names:
            result_params.query_params.append(
                APIParam(name="sort_by", value=config.sort_by)
            )

        if config.sort_order and "sort_order" not in param_names:
            result_params.query_params.append(
                APIParam(name="sort_order", value=config.sort_order)
            )

        if config.sort and "sort" not in param_names:
            result_params.query_params.append(APIParam(name="sort", value=config.sort))

        if config.search and "search" not in param_names:
            result_params.query_params.append(
                APIParam(name="search", value=config.search)
            )

        if config.page is not None and "page" not in param_names:
            result_params.query_params.append(APIParam(name="page", value=config.page))

        if config.per_page is not None and "per_page" not in param_names:
            result_params.query_params.append(
                APIParam(name="per_page", value=config.per_page)
            )

        if config.brands_ids and "brands_ids" not in param_names:
            result_params.query_params.append(
                APIParam(name="brands_ids", value=config.brands_ids)
            )

        return result_params

    def _update_entity_tracker_from_params(self, params: APIParams) -> None:
        """Update entity ID tracker based on generated parameters.

        Args:
            params: Generated parameters
        """
        try:
            if params.path_params:
                for param in params.path_params:
                    if param.name == "countryId" and param.value:
                        self.entity_id_tracker["countryId"] = str(param.value)
                    elif param.name == "brandId" and param.value:
                        self.entity_id_tracker["brandId"] = str(param.value)

            if params.query_params:
                for param in params.query_params:
                    if param.name == "countryId" and param.value:
                        self.entity_id_tracker["countryId"] = str(param.value)
                    elif param.name == "countryIds" and param.value:
                        self.entity_id_tracker["countryIds"] = str(param.value)
                    elif param.name == "brandId" and param.value:
                        self.entity_id_tracker["brandId"] = str(param.value)
                    elif param.name == "brandsIds" and param.value:
                        self.entity_id_tracker["brandsIds"] = str(param.value)

        except Exception as e:
            logger.error(f"Error updating entity tracker from params: {str(e)}")

    def get_entity_tracker(self) -> Dict[str, Optional[str]]:
        """Get the current entity ID tracker.

        Returns:
            Dict of entity ID tracking information
        """
        return self.entity_id_tracker
