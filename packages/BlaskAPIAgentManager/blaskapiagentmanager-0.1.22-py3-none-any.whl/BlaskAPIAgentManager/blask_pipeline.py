import os
import logging
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from .agent import BlaskAPIAgent
from .fetch_id import IDExtractor
from .planner import PlannerTool
from .parameter_generator import ParameterGenerator, APICallConfig
from .api_executor import APIExecutor
from .processor import ProcessorTool
from .result_synthesizer import ResultSynthesizer

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BlaskPipeline:

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.getenv("BLASK_USERNAME")
        self.password = password or os.getenv("BLASK_PASSWORD")

        # Initialize API agent
        self.api_agent = BlaskAPIAgent(username=self.username, password=self.password)

        # Initialize pipeline components
        self.id_extractor = IDExtractor()
        self.planner = PlannerTool(api_agent=self.api_agent)
        self.parameter_generator = ParameterGenerator(api_agent=self.api_agent)
        self.api_executor = APIExecutor(api_agent=self.api_agent)
        self.processor = ProcessorTool(llm=self.api_agent.llm)
        self.synthesizer = ResultSynthesizer(llm=self.api_agent.llm)

    def process_query(self, query: str) -> Dict[str, Any]:
        logger.info(f"Processing query: {query}")

        # Step 1: Authenticate and load API specifications
        if not self.api_agent.authenticate():
            return {
                "error": "Authentication failed",
                "data": None,
                "summary": "Could not authenticate with Blask API",
            }

        self.api_agent.load_swagger_spec()

        # Step 2: Extract country and brand IDs from query
        all_countries_map, country_mapping, all_brands_map, brand_mapping = (
            self.id_extractor.extract_ids_from_query(query)
        )
        logger.info(f"Extracted country mapping: {country_mapping}")
        logger.info(f"Extracted brand mapping: {brand_mapping}")

        # Step 3: Create API call plan
        actions, explanation = self.planner.get_api_plan(
            query, country_mapping, brand_mapping
        )

        if not actions:
            return {
                "error": None,
                "data": None,
                "summary": "No relevant API endpoints found for this query",
            }

        logger.info(f"Generated API plan with {len(actions)} actions")

        # Step 4-9: Execute API calls and process results
        all_raw_results = {}
        complete_processor_results = {}

        # Sort actions by priority
        sorted_actions = sorted(actions, key=lambda x: x.get("priority", 999))

        # Execute each action
        for action in sorted_actions:
            method = action.get("method", "").upper()
            path = action.get("path", "")

            if not method or not path:
                continue

            logger.info(
                f"Processing action: {method} {path} (Priority: {action.get('priority')})"
            )

            # Create config for parameter generation
            config = APICallConfig(
                method=method,
                path=path,
                time_range=action.get("time_range"),
            )

            # Get endpoint details
            endpoint_info = self.api_agent.get_endpoint_details(path, method)

            # Extract country IDs for parameter generator
            country_ids_for_params = (
                list(country_mapping.values()) if country_mapping else None
            )

            # Generate parameters
            params = self.parameter_generator.generate_parameters(
                query=query,
                endpoint_info=endpoint_info,
                config=config,
                all_results=complete_processor_results,
                country_ids=country_ids_for_params,
            )

            # Sync entity trackers
            entity_tracker = self.parameter_generator.get_entity_tracker()
            self.api_executor.entity_id_tracker = entity_tracker.copy()

            # Execute API call
            result = self.api_executor.execute_api_call(method, path, params)

            # Update entity tracker
            self.parameter_generator.entity_id_tracker = (
                self.api_executor.get_entity_tracker()
            )

            # Create unique key for this API call
            result_key = f"{method} {path}"
            if config.time_range:
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
                if start_date and end_date:
                    start_date_part = (
                        start_date.split(" ")[0] if " " in start_date else start_date
                    )
                    end_date_part = (
                        end_date.split(" ")[0] if " " in end_date else end_date
                    )
                    result_key = (
                        f"{method} {path} ({start_date_part} to {end_date_part})"
                    )

            # Store raw result
            raw_result_data = result.get("data", result)
            all_raw_results[result_key] = raw_result_data

            # Convert parameters to dict for processor
            action_params = {}
            if params.path_params:
                for param in params.path_params:
                    action_params[f"path_{param.name}"] = param.value
            if params.query_params:
                for param in params.query_params:
                    action_params[f"query_{param.name}"] = param.value
            if params.body:
                action_params["body"] = params.body

            action["generated_params"] = action_params

            if config.time_range:
                action_params["time_range"] = config.time_range

            # Handle multiple executions
            if result.get("multiple_executions", False) and result.get(
                "individual_results"
            ):
                logger.info(
                    f"Processing {len(result['individual_results'])} individual results for {result_key}"
                )

                # Extract response structure from first result
                first_individual_result = result["individual_results"][0]["result"]
                api_response_structure = self._extract_response_structure(
                    first_individual_result
                )

                # Get processing plan
                processing_plan = self.processor.get_processing_plan(
                    query=query,
                    api_parameters=action_params,
                    api_response=api_response_structure,
                    reason=action.get("reason", ""),
                    dependencies=action.get("dependencies", ""),
                    explanation=explanation,
                    previous_processed_results=complete_processor_results,
                    country_ids=country_mapping,
                )

                # Process each individual result
                individual_processed_results = []
                combined_processed_data = []

                for individual_result_data in result["individual_results"]:
                    individual_raw_api_response = individual_result_data["result"]
                    id_info = {
                        k: v
                        for k, v in individual_result_data.items()
                        if k.startswith("_")
                    }

                    if individual_raw_api_response:
                        logger.debug(
                            f"Executing processing plan for an individual result. ID info: {id_info}. Plan has {len(processing_plan)} steps. Individual raw response keys: {list(individual_raw_api_response.keys()) if isinstance(individual_raw_api_response, dict) else 'N/A (list)'}"
                        )
                        if len(processing_plan) > 0:
                            logger.debug(
                                f"First step of processing plan: {processing_plan[0].function if processing_plan else 'N/A'}"
                            )

                        individual_processed = self.processor.execute_processing_plan(
                            processing_plan=processing_plan,
                            api_response=individual_raw_api_response,
                        )

                        # Add ID information to processed result
                        if individual_processed.get("processed_data"):
                            if isinstance(individual_processed["processed_data"], dict):
                                individual_processed["processed_data"].update(id_info)
                            elif isinstance(
                                individual_processed["processed_data"], list
                            ):
                                for item in individual_processed["processed_data"]:
                                    if isinstance(item, dict):
                                        item.update(id_info)

                        individual_processed_results.append(individual_processed)

                        # Collect processed data
                        if individual_processed.get("processed_data") is not None:
                            if isinstance(individual_processed["processed_data"], list):
                                combined_processed_data.extend(
                                    individual_processed["processed_data"]
                                )
                            else:
                                combined_processed_data.append(
                                    individual_processed["processed_data"]
                                )

                    else:
                        logger.warning(
                            f"No individual result to process for one of the {result_key} calls"
                        )

                processed_result = {
                    "processed_data": (
                        combined_processed_data if combined_processed_data else None
                    ),
                    "multiple_executions_metadata": {
                        "total_individual_results": len(individual_processed_results),
                        "execution_metadata": result.get("execution_metadata", {}),
                    },
                }

            else:
                # Single execution
                api_response_structure = self._extract_response_structure(
                    raw_result_data
                )

                # Get processing plan
                processing_plan = self.processor.get_processing_plan(
                    query=query,
                    api_parameters=action_params,
                    api_response=api_response_structure,
                    reason=action.get("reason", ""),
                    dependencies=action.get("dependencies", ""),
                    explanation=explanation,
                    previous_processed_results=complete_processor_results,
                    country_ids=country_mapping,
                )

                if raw_result_data:
                    logger.debug(
                        f"Executing processing plan for a single result. Plan has {len(processing_plan)} steps. Raw response keys: {list(raw_result_data.keys()) if isinstance(raw_result_data, dict) else 'N/A (list)'}"
                    )
                    if len(processing_plan) > 0:
                        logger.debug(
                            f"First step of processing plan: {processing_plan[0].function if processing_plan else 'N/A'}"
                        )

                    processed_result = self.processor.execute_processing_plan(
                        processing_plan=processing_plan, api_response=raw_result_data
                    )
                else:
                    processed_result = {"processed_data": None}
                    logger.warning(
                        f"No result to process for {result_key}, API call might have failed or returned empty."
                    )

            complete_processor_results[result_key] = processed_result

            if processed_result and processed_result.get("processed_data"):
                processed_data_for_ids = processed_result["processed_data"]
                extracted_brand_ids = self._extract_ids_from_processed_data(
                    processed_data_for_ids, "brandId"
                )
                if extracted_brand_ids:
                    current_brand_ids = self.parameter_generator.entity_id_tracker.get(
                        "brandId", []
                    )
                    # Ensure current_brand_ids is not None and properly handle different formats
                    if current_brand_ids is None:
                        current_brand_ids = []
                    elif isinstance(current_brand_ids, str):
                        if "," in current_brand_ids:
                            current_brand_ids = [
                                id.strip()
                                for id in current_brand_ids.split(",")
                                if id.strip()
                            ]
                        else:
                            current_brand_ids = (
                                [current_brand_ids] if current_brand_ids else []
                            )
                    elif not isinstance(current_brand_ids, list):
                        current_brand_ids = [current_brand_ids]

                    # Convert all IDs to strings first to ensure consistency
                    new_ids_str = [
                        str(bid)
                        for bid in extracted_brand_ids
                        if bid is not None and str(bid).strip()
                    ]
                    existing_ids_str = [
                        str(bid)
                        for bid in current_brand_ids
                        if bid is not None and str(bid).strip()
                    ]

                    updated_brand_ids = list(set(existing_ids_str + new_ids_str))
                    final_brand_ids = []
                    for bid_str in updated_brand_ids:
                        try:
                            if str(bid_str).strip().isdigit():
                                final_brand_ids.append(int(bid_str))
                            elif str(bid_str).strip() != "":
                                final_brand_ids.append(str(bid_str).strip())
                        except (ValueError, AttributeError):
                            continue

                    self.parameter_generator.entity_id_tracker["brandId"] = (
                        final_brand_ids
                    )
                    logger.info(
                        f"Updated entity_id_tracker with brandIds: {final_brand_ids}"
                    )

            action["processed"] = {
                "processed_data": processed_result.get("processed_data")
            }

        # Extract IDs from query before synthesizing results
        (
            _,
            updated_country_mapping,
            _,
            updated_brand_mapping,
        ) = self.id_extractor.extract_ids_from_query(str({"actions": sorted_actions}))

        # Merge any new mappings found
        country_mapping.update(updated_country_mapping)
        brand_mapping.update(updated_brand_mapping)

        # Step 10: Synthesize all results
        summary = self.synthesizer.synthesize_results(
            query=query,
            all_countries_map=all_countries_map,
            country_mapping=country_mapping,
            api_results={"actions": sorted_actions},
            explanation=explanation,
            brand_mapping=brand_mapping,
        )

        return {
            "error": None,
            "data": {
                "original_query": query,
                "api_plan": {"actions": actions, "explanation": explanation},
                "country_mapping": country_mapping,
                "raw_results": all_raw_results,
                "processed_results": complete_processor_results,
            },
            "summary": summary,
        }

    def _extract_response_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if not result:
            return {}

        if isinstance(result, list) and result:
            return result[0]

        if not isinstance(result, dict):
            return result

        if "data" in result and isinstance(result["data"], list) and result["data"]:
            structure = {
                key: (
                    value[0:1] if key == "data" and isinstance(value, list) else value
                )
                for key, value in result.items()
            }
            return structure

        for key, value in result.items():
            if isinstance(value, list) and value:
                structure = {
                    k: (v[0:1] if isinstance(v, list) and v else v)
                    for k, v in result.items()
                }
                return structure

        return {
            "_note": "This is a structure example. The actual response may contain multiple items.",
            **result,
        }

    def _extract_ids_from_processed_data(
        self, data: Any, key_to_extract: str
    ) -> List[Any]:
        found_ids = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key == key_to_extract and value is not None:
                    if isinstance(value, list):
                        found_ids.extend(item for item in value if item is not None)
                    else:
                        found_ids.append(value)
                elif isinstance(value, (dict, list)):
                    found_ids.extend(
                        self._extract_ids_from_processed_data(value, key_to_extract)
                    )
        elif isinstance(data, list):
            for item in data:
                found_ids.extend(
                    self._extract_ids_from_processed_data(item, key_to_extract)
                )

        unique_ids = []
        seen = set()
        for item_id in found_ids:
            if isinstance(item_id, (int, str)):
                if item_id not in seen:
                    unique_ids.append(item_id)
                    seen.add(item_id)
        return unique_ids
