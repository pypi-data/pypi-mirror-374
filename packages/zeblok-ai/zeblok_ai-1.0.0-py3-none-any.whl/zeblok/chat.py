import requests
import json
from datetime import datetime
from typing import List, Dict
from .utils.constants import VALIDATE_API_URL, REQUEST_FROM

### there is no real need for this class anymore, since models.py now is holding the 
### information such as chat history and call completions API
class InferenceChat():
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the InferenceChat with API key and model name.

        Args:
            api_key (str): API key for authentication.
            model_name (str): Name of the model to use for chat.
        """
        if not api_key or not model_name:
            raise ValueError("API key, model name and id are required.")
        self.api_key = api_key
        self.model_name = model_name
        self.chat_history = []
    
    def chat(self, prompt: str, max_tokens: int = 50, temperature: float = 0.7) -> str:
        """
        Generate a chat response using the completions API.

        Args:
            prompt (str): The prompt to send to the model.
            max_tokens (int): Maximum number of tokens to generate.
            temperature (float): Sampling temperature.

        Returns:
            str: The model's response.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty or None.")

        response = ''
        
        if response.status_code == 200 and response.get("success", True):
            chat_data = response["data"]
            chat_response = chat_data["choices"][0]["text"].strip()
            self.chat_history.append({
                "prompt": prompt,
                "response": chat_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return chat_response
        elif response.status_code == 404:
            raise Exception(f"API Error: {response.status_code} - Model {model_name} could not be found.")
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
            
    def get_chat_history(self) -> List[Dict]:
        """
        Retrieve the chat history.

        Returns:
            List[Dict]: List of chat history entries.
        """
        return self.chat_history