from .utils.constants import VALIDATE_API_URL, POST
from .error import APIError, AuthenticationError, InvalidRequestError, RateLimitError, ServiceUnavailableError

class APIKeyAuth:
    def __init__(self, client):
        '''
        APIKeyAuth class.

        Args:
            client: The client instance to interact with the API.
        '''
        self.client = client

    def validate_api_key(self, api_key, **kwargs):
        '''
        Validate API key.

        Args:
            api_key (str): The API key to validate.

        Returns: json: Validation response from the API.
        '''
        params = {"aiKey": api_key}
        return self.client._request(POST, VALIDATE_API_URL, params)

    def set_api_key(self, api_key):
        '''
        Set the API key for the client.

        Args:
            api_key (str): The API key to set.
        '''
        self.client.api_key = api_key

class Completions:
    def __init__(self, client):
        self.client = client

    def create(self, model, prompt, **kwargs):
        '''
        Create a completion for the given prompt

        Args:

            model (str): Model name
            prompt (str): The prompt to complete
            **kwargs: Additional parameters

        Returns:
            dict: Completion response
        '''
        return self.client.models[model].completions(prompt, **kwargs)


class Embeddings:
    def __init__(self, client):
        self.client = client

    def create(self, model, input_text, **kwargs):
        '''
        Create embeddings for the given input text

        Args:
            model (str): Model name
            input_text (str or list): Input text to embed
            **kwargs: Additional parameters

        Returns:
            dict: Embedding response
        '''
        return self.client.models[model].create(input_text, **kwargs)