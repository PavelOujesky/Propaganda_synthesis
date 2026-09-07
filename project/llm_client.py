import os
from typing import Any, Dict, List, Optional, Tuple

import openai
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a .env file
load_dotenv()


# ==========================================
# 1. CLIENT CONFIGURATION & CONSTANTS
# ==========================================

# Mapping of model names to their default temperature values for generation
TEMP_MAP: Dict[str, float] = {
    "gpt-oss-120b": 0.7,
    "deepseek-v3.2-thinking": 0.7,
    "deepseek-v3.2": 0.7,
    "glm-4.7": 0.7,
}

DEFAULT_SEED: int = 42

# Initialize the OpenAI client (Singleton pattern)
_client = openai.OpenAI(
    api_key=os.environ.get("E_INFRA_API_TOKEN", ""),
    base_url="https://llm.ai.e-infra.cz/v1/",
)


# ==========================================
# 2. CORE API LOGIC
# ==========================================

def _base_api_call(
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    response_format: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str, Optional[str], float, int]:
    """
    Private core function to handle the OpenAI API request.
    
    Args:
        system_prompt (str): The system prompt providing instructions.
        user_prompt (str): The user input to be processed.
        model (str): The specific LLM to use.
        temperature (float): Sampling temperature for generation.
        response_format (Optional[Dict[str, str]]): Format specification (e.g., JSON object).
        extra_body (Optional[Dict[str, Any]]): Additional parameters (e.g., guided decoding schema).
        
    Returns:
        Tuple[str, str, Optional[str], float, int]: Contains the generated text, 
        finish reason, reasoning content (if any), temperature used, and the seed.
    """
    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "seed": DEFAULT_SEED,
    }

    if response_format:
        kwargs["response_format"] = response_format
    if extra_body:
        kwargs["extra_body"] = extra_body

    response = _client.chat.completions.create(**kwargs)

    message = response.choices[0].message
    finish_reason = str(response.choices[0].finish_reason)
    
    result_text = message.content if message.content else ""
    reasoning = getattr(message, "reasoning_content", None)

    return result_text, finish_reason, reasoning, temperature, DEFAULT_SEED


# ==========================================
# 3. PUBLIC INTERFACES
# ==========================================

def call_openai_api_json(
    system_prompt: str, 
    user_prompt: str, 
    model: str, 
    temperature: float = 0.7
) -> str:
    """
    Calls the API using the standard JSON mode.
    """
    result_text, _, _, _, _ = _base_api_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return result_text


def call_openai_api_guided(
    system_prompt: str,
    user_prompt: str,
    model: str,
    pydantic_model: type[BaseModel],
    temperature: Optional[float] = None,
) -> Tuple[str, str, Optional[str], float, int]:
    """
    Calls the API enforcing a strict JSON schema via Guided Decoding.
    
    Args:
        system_prompt (str): The system instructions.
        user_prompt (str): The user input.
        model (str): The target model name.
        pydantic_model (type[BaseModel]): The Pydantic class defining the expected output.
        temperature (Optional[float]): Specific temperature. If None, falls back to TEMP_MAP.
        
    Returns:
        Tuple[str, str, Optional[str], float, int]: Output string, finish reason, 
        reasoning content, temperature used, and seed.
    """
    # If temperature is not explicitly provided, fetch it from TEMP_MAP or default to 0.7
    if temperature is None:
        temperature = next(
            (temp for key, temp in TEMP_MAP.items() if key in model), 0.7
        )
    
    json_schema = pydantic_model.model_json_schema()

    return _base_api_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        extra_body={"guided_json": json_schema},
    )
