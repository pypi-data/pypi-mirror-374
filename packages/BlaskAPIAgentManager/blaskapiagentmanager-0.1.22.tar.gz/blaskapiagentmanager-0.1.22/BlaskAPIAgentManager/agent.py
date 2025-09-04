import os
import json
import requests
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)


class BlaskAPIAgent:
    """Agent for interacting with Blask API based on Swagger spec."""

    def __init__(
        self,
        swagger_url: str = None,
        login_url: str = None,
        base_url: str = None,
        username: str = None,
        password: str = None,
        llm: Optional[Any] = None,
    ):
        """Initialize the BlaskAPIAgent.

        Args:
            swagger_url: URL for the Swagger JSON specification
            login_url: URL for API authentication
            base_url: Base URL for API requests
            username: Username for API authentication
            password: Password for API authentication
            llm: Language model to use for agent operations
        """

        self.swagger_url = swagger_url or os.getenv(
            "SWAGGER_JSON_URL", "https://app.stage.blask.com/api/swagger-json"
        )
        self.login_url = login_url or os.getenv(
            "LOGIN_URL", "https://app.stage.blask.com/api/auth/sign-in"
        )
        self.base_url = base_url or os.getenv(
            "BASE_URL", "https://app.stage.blask.com/api"
        )
        self.username = username or os.getenv("BLASK_USERNAME")
        self.password = password or os.getenv("BLASK_PASSWORD")

        allowed_categories_str = os.getenv("ALLOWED_API_CATEGORIES", "[]")
        try:
            # First try JSON parse
            self.allowed_categories = json.loads(allowed_categories_str)
        except json.JSONDecodeError:
            try:
                categories = allowed_categories_str.strip("[]").split(",")
                self.allowed_categories = [
                    cat.strip().strip("\"'") for cat in categories if cat.strip()
                ]
            except Exception as e:
                logger.warning(f"Failed to parse ALLOWED_API_CATEGORIES: {str(e)}")
                self.allowed_categories = []

        self.session = requests.Session()
        self.is_authenticated = False

        self.llm = llm or ChatOpenAI(
            model="deepseek/deepseek-r1",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        self.swagger_data = None
        logger.info("BlaskAPIAgent initialized.")

    def authenticate(self, retries: int = 3, backoff_factor: float = 0.5) -> bool:
        """Authenticate with the Blask API.

        Args:
            retries: Number of retries for failed requests
            backoff_factor: Factor for exponential backoff between retries

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.is_authenticated:
            logger.debug("Already authenticated.")
            return True

        payload = {"identifier": self.username, "password": self.password}

        for attempt in range(retries + 1):
            try:
                response = self.session.post(self.login_url, json=payload)
                response.raise_for_status()

                if response.status_code in [200, 201]:
                    self.is_authenticated = True
                    logger.info("Authentication successful.")
                    return True

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Authentication attempt {attempt + 1}/{retries + 1} failed: {e}"
                )

                is_client_error = (
                    isinstance(e, requests.exceptions.HTTPError)
                    and e.response.status_code < 500
                )

                if attempt >= retries or is_client_error:
                    if is_client_error:
                        logger.error(
                            f"Authentication failed with client error {e.response.status_code}: {e.response.text}"
                        )
                    else:
                        logger.error(
                            f"Authentication failed after {retries + 1} attempts. Last error: {e}"
                        )
                    break
                else:
                    sleep_time = backoff_factor * (2**attempt)
                    logger.info(
                        f"Server or network error during authentication. Retrying in {sleep_time:.2f} seconds..."
                    )
                    time.sleep(sleep_time)
                    continue

            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during authentication: {str(e)}"
                )
                break

        self.is_authenticated = False
        return False

    def load_swagger_spec(self) -> Dict:
        """Load the Swagger specification.

        Returns:
            Dict: The Swagger specification as a dictionary
        """
        if self.swagger_data:
            return self.swagger_data

        try:
            logger.info(f"Loading Swagger spec from {self.swagger_url}")
            response = self.session.get(self.swagger_url)
            response.raise_for_status()
            self.swagger_data = response.json()
            logger.info("Swagger spec loaded successfully.")
            return self.swagger_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error loading Swagger spec: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding Swagger JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"An unexpected error occurred loading Swagger spec: {str(e)}")
            return {}

    def get_endpoint_summary(self) -> Dict[str, List[Dict[str, str]]]:
        """Get a summary of available API endpoints.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary of endpoint categories
                with endpoint names and descriptions
        """
        if not self.swagger_data:
            self.load_swagger_spec()

        if not self.swagger_data:
            return {}

        summary = {}

        for path, path_info in self.swagger_data.get("paths", {}).items():
            for method, method_info in path_info.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                tag = method_info.get("tags", ["Other"])[0]

                if self.allowed_categories and tag not in self.allowed_categories:
                    logger.debug(
                        f"Skipping endpoint in category '{tag}' due to allow list."
                    )
                    continue

                if tag not in summary:
                    summary[tag] = []
                summary[tag].append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "summary": method_info.get("summary", "No description"),
                        "operationId": method_info.get(
                            "operationId", f"{method}_{path}"
                        ),
                    }
                )

        return summary

    def get_endpoint_details(self, path: str, method: str) -> Dict:
        """Get detailed information about a specific endpoint.

        Args:
            path: The API path
            method: The HTTP method (GET, POST, etc.)

        Returns:
            Dict: Detailed information about the endpoint
        """
        if not self.swagger_data:
            self.load_swagger_spec()

        if not self.swagger_data:
            logger.warning("Swagger data not loaded, cannot get endpoint details.")
            return {}

        path_info = self.swagger_data.get("paths", {}).get(path, {})
        method_info = path_info.get(method.lower(), {})

        if not method_info:
            return {}

        parameters = method_info.get("parameters", [])
        logger.debug(f"Parameters for {method} {path}: {parameters}")

        request_body = {}
        if "requestBody" in method_info:
            content = method_info["requestBody"].get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                request_body = self._resolve_schema_ref(schema)

        responses = {}
        for status, response_info in method_info.get("responses", {}).items():
            content = response_info.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                responses[status] = {
                    "description": response_info.get("description", ""),
                    "schema": self._resolve_schema_ref(schema),
                }
            else:
                responses[status] = {
                    "description": response_info.get("description", ""),
                }

        return {
            "method": method.upper(),
            "path": path,
            "summary": method_info.get("summary", ""),
            "description": method_info.get("description", ""),
            "parameters": parameters,
            "requestBody": request_body,
            "responses": responses,
        }

    def _resolve_schema_ref(self, schema: Dict) -> Dict:
        """Resolve schema references.

        Args:
            schema: Schema with potentially nested references

        Returns:
            Dict: Resolved schema
        """
        if not schema:
            return {}

        logger.debug(
            f"Resolving schema reference: {schema.get('$ref', 'inline schema')}"
        )

        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.split("/")[-1]
                return (
                    self.swagger_data.get("components", {})
                    .get("schemas", {})
                    .get(schema_name, {})
                )

        return schema

    def execute_api_call(
        self,
        path: str,
        method: str,
        path_params: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> Dict:
        """Execute an API call with retry logic.

        Args:
            path: The API path
            method: The HTTP method (GET, POST, etc.)
            path_params: Parameters to substitute in the path
            query_params: Query parameters
            body: Request body for POST/PUT operations
            retries: Number of retries for failed requests
            backoff_factor: Factor for exponential backoff between retries

        Returns:
            Dict: API response
        """
        last_exception = None

        actual_path = path
        if path_params:
            logger.debug(f"Applying path parameters: {path_params}")
            for param, value in path_params.items():
                actual_path = actual_path.replace(f"{{{param}}}", str(value))
        url = f"{self.base_url}{actual_path}"

        if self.is_authenticated:
            if not self.authenticate():
                return {"error": "Initial authentication failed"}

        for attempt in range(retries + 1):
            try:
                logger.info(f"Executing API call: {method.upper()} {url}")

                method_lower = method.lower()
                response = self.session.request(
                    method_lower, url, params=query_params, json=body
                )

                logger.debug(f"API Response Status Code: {response.status_code}")
                response.raise_for_status()

                try:
                    response_json = response.json()
                    return response_json
                except json.JSONDecodeError:
                    return {"content": response.text}

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{retries + 1} failed with RequestException: {e}"
                )
                last_exception = e

                is_http_error = isinstance(e, requests.exceptions.HTTPError)

                # Handle 401 Unauthorized by re-authenticating
                if is_http_error and e.response.status_code == 401:
                    if attempt < retries:
                        logger.info(
                            "Authentication error (401). Attempting to re-authenticate..."
                        )
                        self.is_authenticated = False
                        if self.authenticate():
                            logger.info(
                                "Re-authentication successful. Retrying request..."
                            )
                            continue  # Retry immediately
                        else:
                            logger.error("Re-authentication failed. Aborting.")
                            break  # Exit retry loop
                    else:
                        break  # No retries left

                is_client_error = (
                    is_http_error
                    and e.response.status_code != 401
                    and e.response.status_code < 500
                )

                # Retry on "something went wrong" even for client error status codes
                should_retry_special_case = False
                if (
                    is_http_error
                    and e.response.text
                    and "something went wrong" in e.response.text.lower()
                ):
                    should_retry_special_case = True

                if attempt >= retries or (
                    is_client_error and not should_retry_special_case
                ):
                    if is_client_error:
                        logger.error(
                            f"API call failed with client error {e.response.status_code}: {e.response.text}"
                        )
                    else:
                        logger.error(
                            f"API call failed after {retries + 1} attempts. Last error: {e}"
                        )
                    break
                else:
                    sleep_time = backoff_factor * (2**attempt)
                    logger.info(
                        f"Server or network error during API call. Retrying in {sleep_time:.2f} seconds..."
                    )
                    time.sleep(sleep_time)
                    continue
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected exception during API call to {url}: {str(e)}")
                break

        # After the loop
        if last_exception:
            if isinstance(last_exception, requests.exceptions.HTTPError):
                return {
                    "error": f"API call failed after {retries + 1} attempts with status {last_exception.response.status_code}",
                    "details": last_exception.response.text,
                }
            return {
                "error": f"API call failed after {retries + 1} attempts. Last exception: {str(last_exception)}"
            }

        return {"error": f"API call failed after {retries + 1} attempts."}
