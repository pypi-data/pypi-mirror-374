import requests
import json
import os

# --- Custom Exception Classes ---
class OrionacAIError(Exception):
    """Base exception class for all orionac-ai errors."""
    pass

class AuthenticationError(OrionacAIError):
    """Raised when authentication fails."""
    pass

class APIError(OrionacAIError):
    """Raised for non-200 API responses."""
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

# --- Response Object ---
class APIResponse:
    """
    A container for the API response data.
    """
    def __init__(self, response_json):
        self._data = response_json
        self.text = self._data.get("generated_text", "")
        self.model_used = self._data.get("model", "")
        self.prompt_tokens = self._data.get("usage", {}).get("prompt_tokens")
        self.completion_tokens = self._data.get("usage", {}).get("completion_tokens")
        self.total_tokens = self._data.get("usage", {}).get("total_tokens")

    def __repr__(self):
        return f"<APIResponse text='{self.text[:50]}...'>"
        
    @property
    def raw_data(self):
        """Returns the raw JSON response from the API."""
        return self._data


# --- Main Client Class ---
class Theta:
    """
    The main client for interacting with the Orionac AI Theta models.
    """
    def __init__(self, api_key: str = None, base_url: str = "https://api.orionac.com/v1"):
        """
        Initializes the Theta client.

        Args:
            api_key (str, optional): Your Orionac AI API key. 
                                     If not provided, it will check the ORIONAC_API_KEY environment variable.
            base_url (str, optional): The base URL for the API. Defaults to the official endpoint.
        """
        if api_key is None:
            api_key = os.environ.get("ORIONAC_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "No API key provided. You can pass it to the client or set the ORIONAC_API_KEY environment variable."
            )
        
        # --- Core Properties ---
        self.api_key = api_key
        self.api_base_url = base_url
        
        # --- Configurable Properties ---
        self.timeout = 60  # Default timeout for API requests in seconds
        self.retry_attempts = 2 # Default number of retries
        self.default_model = "theta-1.0-sl"
        
        # --- Informational Properties ---
        self.last_response = None # Stores the last raw response from requests
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "orionac-ai-python/0.1.0"
        })

    def generate(
        self,
        prompt: str,
        context: dict = None,
        # --- 20+ Attributes & Properties for fine-tuning ---
        model: str = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop_sequences: list = None,
        stream: bool = False, # For future implementation
        user_id: str = None,
        metadata: dict = None,
        best_of: int = 1,
        echo_prompt: bool = False,
        logprobs: int = None,
        tone: str = "professional", # custom attribute
        output_format: str = "text", # custom attribute: 'text' or 'json'
        language: str = "en-US", # custom attribute
        creativity_level: float = 0.5, # custom attribute: 0.0 to 1.0
        response_length: str = "medium" # custom attribute: 'short', 'medium', 'long'
    ) -> APIResponse:
        """
        Generates content based on a prompt and context.

        Args:
            prompt (str): The main instruction or question for the model.
            context (dict, optional): A dictionary of key-value pairs providing context.
            model (str, optional): The model to use. Defaults to `self.default_model`.
            max_tokens (int, optional): The maximum number of tokens to generate.
            temperature (float, optional): Controls randomness. Lower is more deterministic.
            top_p (float, optional): Nucleus sampling parameter.
            frequency_penalty (float, optional): Penalizes new tokens based on their existing frequency.
            presence_penalty (float, optional): Penalizes new tokens based on whether they appear in the text so far.
            stop_sequences (list, optional): A list of strings where the API will stop generating further tokens.
            user_id (str, optional): A unique identifier for the end-user.
            metadata (dict, optional): Any additional metadata to associate with the request.
            tone (str, optional): The desired tone of the response (e.g., 'professional', 'casual', 'witty').
            ... and other parameters.

        Returns:
            APIResponse: An object containing the generated text and other metadata.
        
        Raises:
            APIError: If the API returns a non-200 status code.
        """
        generation_url = f"{self.api_base_url}/generate"
        
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "context": context or {},
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop_sequences,
            "stream": stream,
            "user": user_id,
            "metadata": metadata,
            "best_of": best_of,
            "echo": echo_prompt,
            "logprobs": logprobs,
            "custom_params": {
                "tone": tone,
                "output_format": output_format,
                "language": language,
                "creativity_level": creativity_level,
                "response_length": response_length
            }
        }
        
        try:
            # --- THIS IS A MOCK API CALL for demonstration ---
            # In a real scenario, this would make a live HTTP request.
            # We will simulate a successful response based on the example.
            if prompt == "Draft a follow-up email to a prospect we spoke with." and context.get("prospect_name") == "Jane Doe":
                mock_response_data = {
                    "generated_text": "Subject: Following Up\n\nHi Jane Doe,\n\nJust wanted to quickly follow up on our conversation from 2 days ago regarding our new AI analytics platform. Let me know if you have any further questions!\n\nBest regards,\n[Your Name]",
                    "model": payload["model"],
                    "usage": {"prompt_tokens": 30, "completion_tokens": 55, "total_tokens": 85}
                }
                self.last_response = mock_response_data # Store mock response
                return APIResponse(mock_response_data)
            else:
                # Generic mock response
                mock_response_data = {
                    "generated_text": "This is a generated response to your prompt.",
                    "model": payload["model"],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
                }
                self.last_response = mock_response_data
                return APIResponse(mock_response_data)

            # --- REAL API CALL LOGIC (commented out) ---
            # response = self._session.post(generation_url, json=payload, timeout=self.timeout)
            # self.last_response = response
            # response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            # return APIResponse(response.json())
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 401:
                raise AuthenticationError("Authentication failed. Please check your API key.")
            else:
                raise APIError(f"API request failed: {e.response.text}", status_code)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error occurred: {e}", status_code=None)
