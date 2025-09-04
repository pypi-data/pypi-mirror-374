import logging
from typing import Dict, Any, Optional, List
from .agent import BlaskAPIAgent
from .parameter_generator import APIParams

logger = logging.getLogger(__name__)


class APIExecutor:
    """Executes API calls using generated parameters."""

    def __init__(self, api_agent: Optional[BlaskAPIAgent] = None):
        """Initialize the APIExecutor.

        Args:
            api_agent: BlaskAPIAgent instance for executing API calls
        """
        self.api_agent = api_agent or BlaskAPIAgent()
        self.entity_id_tracker = {
            "countryId": None,
            "brandId": None,
            "countryIds": None,
            "brandsIds": None,
        }

    def execute_api_call(
        self, method: str, path: str, params: APIParams
    ) -> Dict[str, Any]:
        """Execute a single API call.

        Args:
            method: HTTP method
            path: API endpoint path
            params: API parameters

        Returns:
            Dict[str, Any]: API call result with metadata about multiple executions
        """
        path_params = {}
        query_params = {}
        body = {}

        if params.path_params:
            for param in params.path_params:
                path_params[param.name] = param.value

        if params.query_params:
            for param in params.query_params:
                query_params[param.name] = param.value

        if params.body:
            body = params.body

        # Remove singular ID parameters with comma-separated values
        if "countryId" in query_params and "countryIds" in query_params:
            del query_params["countryId"]
        elif "countryId" in query_params and "," in str(query_params["countryId"]):
            query_params["countryIds"] = query_params["countryId"]
            del query_params["countryId"]

        if "brandId" in query_params and "brandsIds" in query_params:
            del query_params["brandId"]
        elif "brandId" in query_params and "," in str(query_params["brandId"]):
            query_params["brandsIds"] = query_params["brandId"]
            del query_params["brandId"]

        # Handle multiple countryIds in query parameters for path-based endpoints
        if "countryIds" in query_params and "{countryId}" in path:
            country_ids_str = str(query_params["countryIds"])
            del query_params["countryIds"]
            if "," in country_ids_str:
                country_ids = [id.strip() for id in country_ids_str.split(",")]
                return self._execute_multiple_calls_for_path_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "countryId",
                    country_ids,
                )
            else:
                path_params["countryId"] = country_ids_str

        # Handle multiple brandsIds in query parameters for path-based endpoints
        if "brandsIds" in query_params and "{brandId}" in path:
            brand_ids_str = str(query_params["brandsIds"])
            del query_params["brandsIds"]
            if "," in brand_ids_str:
                brand_ids = [id.strip() for id in brand_ids_str.split(",")]
                return self._execute_multiple_calls_for_path_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "brandId",
                    brand_ids,
                )
            else:
                path_params["brandId"] = brand_ids_str

        # Handle endpoints that only accept single IDs
        single_id_endpoints = ["/v1/brands", "/v1/countries/{countryId}/brands"]

        if any(endpoint in path for endpoint in single_id_endpoints):
            if "countryIds" in query_params:
                country_ids_str = str(query_params["countryIds"])
                if "," in country_ids_str:
                    country_ids = [id.strip() for id in country_ids_str.split(",")]
                    del query_params["countryIds"]
                    return self._execute_multiple_calls_for_query_param(
                        method,
                        path,
                        path_params,
                        query_params,
                        body,
                        "countryId",
                        country_ids,
                    )
                else:
                    query_params["countryId"] = query_params["countryIds"]
                    del query_params["countryIds"]

        # Set countryId from tracker if needed
        if "{countryId}" in path and "countryId" not in path_params:
            if self.entity_id_tracker["countryId"]:
                path_params["countryId"] = self.entity_id_tracker["countryId"]
            elif "countryIds" in query_params:
                country_ids = str(query_params["countryIds"]).split(",")
                if country_ids:
                    path_params["countryId"] = country_ids[0].strip()

        # Set brandId from tracker if needed
        if "{brandId}" in path and "brandId" not in path_params:
            if self.entity_id_tracker["brandId"]:
                path_params["brandId"] = self.entity_id_tracker["brandId"]
            elif "brandsIds" in query_params:
                brand_ids = str(query_params["brandsIds"]).split(",")
                if brand_ids:
                    path_params["brandId"] = brand_ids[0].strip()

        if "{id}" in path and "id" not in path_params:
            if "countryId" in path_params:
                path_params["id"] = path_params["countryId"]
            elif "brandId" in path_params:
                path_params["id"] = path_params["brandId"]

        # Handle multiple countryIds in path parameters
        if "{countryId}" in path and "countryId" in path_params:
            country_ids_str = str(path_params["countryId"])
            if "," in country_ids_str:
                country_ids = [id.strip() for id in country_ids_str.split(",")]
                return self._execute_multiple_calls_for_path_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "countryId",
                    country_ids,
                )

        # Handle multiple brandIds in path parameters
        if "{brandId}" in path and "brandId" in path_params:
            brand_ids_str = str(path_params["brandId"])
            if "," in brand_ids_str:
                brand_ids = [id.strip() for id in brand_ids_str.split(",")]
                return self._execute_multiple_calls_for_path_param(
                    method, path, path_params, query_params, body, "brandId", brand_ids
                )

        # Handle multiple countryIds in query parameters
        if "countryId" in query_params:
            country_ids_str = str(query_params["countryId"])
            if "," in country_ids_str and "{countryId}" in path:
                country_ids = [id.strip() for id in country_ids_str.split(",")]
                return self._execute_multiple_calls_for_query_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "countryId",
                    country_ids,
                )

        # Handle multiple countryIds in query parameters (plural form)
        if "countryIds" in query_params:
            country_ids_str = str(query_params["countryIds"])
            if "," in country_ids_str and "{countryId}" in path:
                country_ids = [id.strip() for id in country_ids_str.split(",")]
                return self._execute_multiple_calls_for_query_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "countryIds",
                    country_ids,
                )

        # Handle multiple brandIds in query parameters
        if "brandId" in query_params:
            brand_ids_str = str(query_params["brandId"])
            if "," in brand_ids_str and "{brandId}" in path:
                brand_ids = [id.strip() for id in brand_ids_str.split(",")]
                return self._execute_multiple_calls_for_query_param(
                    method, path, path_params, query_params, body, "brandId", brand_ids
                )

        # Handle multiple brandsIds in query parameters (plural form)
        if "brandsIds" in query_params:
            brand_ids_str = str(query_params["brandsIds"])
            if "," in brand_ids_str and "{brandId}" in path:
                brand_ids = [id.strip() for id in brand_ids_str.split(",")]
                return self._execute_multiple_calls_for_query_param(
                    method,
                    path,
                    path_params,
                    query_params,
                    body,
                    "brandsIds",
                    brand_ids,
                )

        # Execute single API call
        result = self.api_agent.execute_api_call(
            path=path,
            method=method,
            path_params=path_params,
            query_params=query_params,
            body=body,
        )

        self._update_entity_tracker_from_results(result)

        # Return single result with metadata
        return {
            "data": result.get("data", result),
            "multiple_executions": False,
            "individual_results": None,
            "execution_metadata": {"total_calls": 1, "id_type": None, "ids_used": None},
        }

    def _execute_multiple_calls_for_path_param(
        self,
        method: str,
        path: str,
        path_params: Dict,
        query_params: Dict,
        body: Dict,
        param_name: str,
        ids: List[str],
    ) -> Dict[str, Any]:
        """Execute multiple API calls for different path parameter values."""
        individual_results = []
        combined_results = []

        for id_value in ids:
            single_path_params = path_params.copy()
            single_path_params[param_name] = id_value

            result = self.api_agent.execute_api_call(
                path=path,
                method=method,
                path_params=single_path_params,
                query_params=query_params,
                body=body,
            )

            # Extract data part from result
            data_only = result.get("data", result)

            # Store individual result with metadata
            individual_result = {
                "result": data_only,
                "parameters": {
                    "path_params": single_path_params,
                    "query_params": query_params,
                    "body": body,
                },
                f"_{param_name}": id_value,
            }
            individual_results.append(individual_result)

            # Combine data for backward compatibility
            if isinstance(data_only, list):
                combined_results.extend(data_only)
            elif isinstance(data_only, dict) and not data_only.get("error"):
                data_only[f"_{param_name}"] = id_value
                combined_results.append(data_only)

        combined_result = {"data": combined_results}
        self._update_entity_tracker_from_results(combined_result)

        return {
            "data": combined_results,
            "multiple_executions": True,
            "individual_results": individual_results,
            "execution_metadata": {
                "total_calls": len(ids),
                "id_type": param_name,
                "ids_used": ids,
            },
        }

    def _execute_multiple_calls_for_query_param(
        self,
        method: str,
        path: str,
        path_params: Dict,
        query_params: Dict,
        body: Dict,
        param_name: str,
        ids: List[str],
    ) -> Dict[str, Any]:
        """Execute multiple API calls for different query parameter values."""
        individual_results = []
        combined_results = []

        for id_value in ids:
            single_query_params = query_params.copy()
            single_query_params[param_name] = id_value

            result = self.api_agent.execute_api_call(
                path=path,
                method=method,
                path_params=path_params,
                query_params=single_query_params,
                body=body,
            )

            # Extract data part from result
            data_only = result.get("data", result)

            # Store individual result with metadata
            individual_result = {
                "result": data_only,
                "parameters": {
                    "path_params": path_params,
                    "query_params": single_query_params,
                    "body": body,
                },
                f"_{param_name}": id_value,
            }
            individual_results.append(individual_result)

            # Combine data for backward compatibility
            if isinstance(data_only, list):
                combined_results.extend(data_only)
            elif isinstance(data_only, dict) and not data_only.get("error"):
                data_only[f"_{param_name}"] = id_value
                combined_results.append(data_only)

        combined_result = {"data": combined_results}
        self._update_entity_tracker_from_results(combined_result)

        return {
            "data": combined_results,
            "multiple_executions": True,
            "individual_results": individual_results,
            "execution_metadata": {
                "total_calls": len(ids),
                "id_type": param_name,
                "ids_used": ids,
            },
        }

    def _update_entity_tracker_from_results(self, result: Dict[str, Any]) -> None:
        """Extract and store entity IDs from API results.

        Args:
            result: API call result
        """
        try:
            if isinstance(result, dict) and "data" in result:
                data = result["data"]
                if isinstance(data, list) and data:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        if "countryId" in first_item:
                            country_ids = [
                                str(item.get("countryId"))
                                for item in data
                                if item.get("countryId")
                            ]
                            if country_ids:
                                self.entity_id_tracker["countryId"] = ",".join(
                                    country_ids
                                )

                        if "brandId" in first_item:
                            brand_ids = [
                                str(item.get("brandId"))
                                for item in data
                                if item.get("brandId")
                            ]
                            if brand_ids:
                                self.entity_id_tracker["brandId"] = ",".join(brand_ids)
        except Exception as e:
            logger.error(f"Error updating entity tracker from results: {str(e)}")

    def get_entity_tracker(self) -> Dict[str, Optional[str]]:
        """Get the current entity ID tracker.

        Returns:
            Dict of entity ID tracking information
        """
        return self.entity_id_tracker
