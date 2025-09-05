from typing import Dict

import requests
from .models import GPTModel, EmbeddingModel
from .utils.constants import VALIDATE_API_URL, REQUEST_FROM
from .api import Completions, Embeddings, APIKeyAuth
from .error import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServiceUnavailableError
)


class Client:
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize the client with API key and base URL

        Args:
            api_key (str): Secret API key for authentication
            base_url (str): Base URL for the API
        """
        if not base_url:
            raise AuthenticationError("Base URL is required")
        if not api_key:
            raise AuthenticationError("API key is required")

        # Ensure base_url starts with http or https
        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "https://" + base_url

        self.api_key = api_key
        self.base_url = base_url
        self.api_auth = APIKeyAuth(self)  # Initialize APIKeyAuth
        self._authenticate_api_key()  # Validate the API key
        self.models = {}
        self._setup_resources()
        self._setup_default_models()

    def _authenticate_api_key(self):
        """Authenticate the API key using APIKeyAuth"""
        response = self.api_auth.validate_api_key(self.api_key)
        # setting the base URL is already done when the client is created
        # self.base_url = response['baseUrl'] # set base URL after API key is validated
        if not response.get("success", False):
            raise AuthenticationError("Invalid API key")

    def _setup_resources(self):
        """Initialize API resources"""
        self.completions = Completions(self)
        self.embeddings = Embeddings(self)

    def _setup_default_models(self):
        """Setup default available models"""
        self._register_model("llama", GPTModel)
        self._register_model("gpt-4", GPTModel)
        self._register_model("embedding-v1", EmbeddingModel)

    def _register_model(self, model_name, model_class):
        """Register a new model type"""
        self.models[model_name] = model_class(model_name, self, self.api_key)

    def _request(self, method, endpoint, params=None):
        """
        Make an API request

        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            params (dict): Request parameters

        Returns:
            dict: API response

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "request-from": REQUEST_FROM, # add request-from header in request
        }
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=params
            )

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError(response.json().get("error", "Invalid API key"))
            elif response.status_code == 400:
                raise InvalidRequestError(response.json().get("error", "Invalid request"))
            elif response.status_code == 429:
                raise RateLimitError(response.json().get("error", "Rate limit exceeded"))
            elif response.status_code >= 500:
                raise ServiceUnavailableError(response.json().get("error", "Service unavailable"))
            else:
                if not response.ok:
                    raise APIError(f"Unexpected error: {response.status_code} - {response.text}")
                    
            return response.json()

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def list_models(self):
        """List all available models"""
        return list(self.models.keys())

