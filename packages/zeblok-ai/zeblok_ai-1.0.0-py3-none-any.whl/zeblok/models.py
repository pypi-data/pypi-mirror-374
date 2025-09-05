from .base.model import BaseModel
from .utils.constants import POST
import chromadb # import chromadb to use embeddings
from datetime import datetime

### TODO: not too sure what to do with this at the moment - it could be used with the
### EmbeddingModel for RAG implementation possibly?
# chroma_client = chromadb.HttpClient(host="zbl-ms-x4ieacwyf-0.baintelpublic", port=80) # initialize ChromaDB client
# collection = chroma_client.get_or_create_collection("newtext") # create vector store 

class GPTModel(BaseModel):
    def __init__(self, model_name, client, api_key):
        super().__init__(model_name, client)
        self.chat_history = []
        
    def completions(self, prompt, max_tokens=50, temperature=0.7, **kwargs):
        """
        Generate completions for the given prompt

        Args:
            prompt (str): The prompt to complete
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature
            **kwargs: Additional parameters

        Returns:
            dict: Completion response
        """
        params = {
            "modelName": self.model_name,
            "message": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "aiKey" : self.client.api_key,
            **kwargs
        }

        # API endpoint; host=app.cewit.zeblok.com in constants.py
        completions_endpoint = "/api/v1/spawnedInferences/sdk/chat/completion/"
        
        response = self.client._request(POST, completions_endpoint, params)
        if response.get("success", True) and response.get("status_code", 200):
                chat_data = response["data"]
                chat_response = chat_data["choices"][0]["message"]["content"].strip()
                self.chat_history.append({
                    "prompt": prompt,
                    "response": chat_response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                return chat_response
        elif response.status_code == 404:
            raise Exception(f"API Error: {response.status_code} - Model {model_name} not found.")
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    # create method instantiated from abstract class - should be removed
    # since this is done with the init method above
    def create():
        pass

    def get_chat_history(self):
        return self.chat_history

class EmbeddingModel(BaseModel):
    def __init__(self, model_name, client, api_key):
        super().__init__(model_name, client)
        self.chat_history = []
        
    def completions():
        pass
        
    def create(self, input_text, **kwargs):
        """
        Create embeddings for the given input text

        Args:
            input_text (str or list): Input text to embed
            **kwargs: Additional parameters

        Returns:
            dict: Embedding response
        """
        params = {
            "model": self.model_name,
            "input": input_text,
            **kwargs
        }
        # @Todo("Integration with vector store that gets embeddings")
        return self.client._request(POST, "/embeddings", params)