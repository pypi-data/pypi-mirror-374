"""WaveSpeed API client base class."""

import time
import requests
import logging
from typing import Dict, Any

from wavespeed_mcp.exceptions import (
    WavespeedAuthError,
    WavespeedRequestError,
    WavespeedTimeoutError,
)
from wavespeed_mcp.const import API_PREDICTION_ENDPOINT

logger = logging.getLogger("wavespeed-client")


class WavespeedAPIClient:
    """Base client for making requests to WaveSpeed API."""

    def __init__(self, api_key: str, api_host: str):
        """Initialize the API client.

        Args:
            api_key: The API key for authentication
            api_host: The API host URL
        """
        self.api_key = api_key
        self.api_host = api_host
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the WaveSpeed API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            API response data as dictionary

        Raises:
            WavespeedAuthError: If authentication fails
            WavespeedRequestError: If the request fails
        """
        host = self.api_host.rstrip("/")
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{host}{path}"

        logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)

            # Check for HTTP errors
            response.raise_for_status()

            data = response.json()

            # Check for API-specific errors
            if "error" in data:
                error_msg = data.get("error", "Unknown API error")
                raise WavespeedRequestError(f"API Error: {error_msg}")

            return data

        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                raise WavespeedAuthError(f"Authentication failed: {str(e)}")
            if response.text:
                raise WavespeedRequestError(f"Request failed: {response.text}")
            raise WavespeedRequestError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, **kwargs)

    def poll_result(
        self, request_id: str, max_retries: int = -1, poll_interval: float = 0.5
    ) -> Dict[str, Any]:
        """Poll for the result of an asynchronous API request.

        Args:
            request_id: The ID of the request to poll for
            max_retries: Maximum number of polling attempts. -1 for infinite retries.
            poll_interval: Time in seconds between polling attempts

        Returns:
            The final result of the API request

        Raises:
            WavespeedTimeoutError: If polling exceeds max_retries
            WavespeedRequestError: If the request fails
        """
        result_url = f"{API_PREDICTION_ENDPOINT}/{request_id}/result"

        attempt = 0

        logger.info(f"Starting API polling for request ID: {request_id}")

        start_time = time.time()

        while True:
            if max_retries != -1 and attempt >= max_retries:
                break

            try:
                if attempt % 10 == 0:
                    logger.debug(
                        f"Polling result attempt {attempt+1}/{max_retries if max_retries != -1 else '∞'}..."
                    )

                response = self.get(result_url)
                result = response.get("data", {})
                status = result.get("status")

                if attempt % 10 == 0:
                    logger.debug(f"Current status: {status}")

                if status == "completed":
                    elapsed = time.time() - start_time
                    logger.info(
                        f"API polling completed after {attempt} attempts ({elapsed:.1f}s)"
                    )
                    return result
                elif status == "failed":
                    elapsed = time.time() - start_time
                    logger.error(
                        f"API polling failed after {attempt} attempts ({elapsed:.1f}s)"
                    )
                    error = result.get("error", "unknown error")
                    raise WavespeedRequestError(f"API request failed: {error}")

                # If still processing, wait and try again
                time.sleep(poll_interval)
                attempt += 1

            except WavespeedRequestError as e:
                # If it's a request error, re-raise it
                elapsed = time.time() - start_time
                logger.error(f"Request failed: {str(e)}")
                raise
            except Exception as e:
                # For other exceptions, log and continue polling
                logger.warning(f"Error during polling: {str(e)}")

        # If we've exhausted all retries
        elapsed = time.time() - start_time
        logger.error(
            f"API polling timed out after {max_retries} attempts ({elapsed:.1f}s)"
        )
        raise WavespeedTimeoutError(f"Polling timed out after {max_retries} attempts")
