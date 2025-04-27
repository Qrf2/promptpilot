import logging
from typing import Any, Dict
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenRouter model configuration
MODEL_CONFIG = {
    "meta-llama/llama-3.1-8b-instruct:free": {
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY"),
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "max_tokens": 2048
    }
}

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    def __init__(self, config: Dict):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "PromptPilot"
        }
        logger.info(f"Initialized OpenRouter client with API key: {config['api_key'][:8]}...")

    def complete(self, prompt: str) -> str:
        """Sends a prompt to OpenRouter and returns the response."""
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config["max_tokens"]
        }
        try:
            logger.info(f"Sending request to OpenRouter: {payload}")
            response = requests.post(
                self.config["endpoint"],
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]
            logger.info(f"Received response: {result[:50]}...")
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            if response.status_code == 401:
                raise Exception("Unauthorized: Invalid or missing OpenRouter API key. Check your `.env` file.")
            raise
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise

def get_model_client(model: str) -> Any:
    """
    Retrieves the client for the specified OpenRouter model.
    
    Args:
        model: The model name (e.g., 'meta-llama/llama-3.1-8b-instruct:free').
    
    Returns:
        An OpenRouterClient instance.
    
    Raises:
        ValueError: If the model is not supported.
    """
    logger.info(f"Retrieving client for model: {model}")
    if model not in MODEL_CONFIG:
        logger.error(f"Unsupported model: {model}")
        raise ValueError(f"Model {model} is not supported.")

    config = MODEL_CONFIG[model]
    return OpenRouterClient(config)

def validate_api_keys() -> bool:
    """
    Validates the OpenRouter API key by making a test request.
    
    Returns:
        True if the API key is valid, False otherwise.
    
    Raises:
        Exception: If the validation request fails.
    """
    logger.info("Validating OpenRouter API key...")
    for model, config in MODEL_CONFIG.items():
        if config["api_key"] == "YOUR_OPENROUTER_API_KEY" or not config["api_key"]:
            logger.warning(f"API key not set for {model}")
            return False
        
        # Test the API key with a simple request
        try:
            client = OpenRouterClient(config)
            # Send a minimal test prompt
            client.complete("Test prompt to validate API key")
            logger.info(f"API key validated successfully for {model}")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            raise Exception(f"API key validation failed: {str(e)}")
    return False