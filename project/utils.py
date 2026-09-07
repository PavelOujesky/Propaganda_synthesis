"""
Utility functions for file I/O operations and data parsing.
This module provides generalized helpers that are independent of specific experiments.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def load_json(filepath: Union[Path, str]) -> Any:
    """
    Safely loads a JSON file.
    
    Args:
        filepath: Path to the JSON file.
        
    Returns:
        The parsed JSON data, or None if the file is missing or invalid.
    """
    path = Path(filepath)
    if not path.exists():
        logger.error(f"CRITICAL ERROR: File '{path}' not found.")
        return None
        
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"CRITICAL ERROR: File '{path}' has invalid JSON format.")
        return None


def load_prompt_text(filepath: Union[Path, str]) -> str:
    """
    Loads the text content of a prompt file.
    
    Args:
        filepath: Path to the text/markdown file.
        
    Returns:
        The content of the file as a string.
        
    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file does not exist: {path}")
    
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def save_results_to_json(data: Union[List[Any], Dict[str, Any]], output_filepath: Union[Path, str]) -> None:
    """
    Saves a list or dictionary to a JSON file.
    Creates necessary parent directories if they don't exist.
    
    Args:
        data: The data structure to save.
        output_filepath: The target destination path.
    """
    path = Path(output_filepath)
    path.parent.mkdir(parents=True, exist_ok=True) 
        
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"  --> Saved to: {path}")


def parse_llm_json(response_text: Optional[str]) -> Dict[str, Any]:
    """
    Cleans markdown tags from LLM output and safely converts it to a dictionary.
    
    Args:
        response_text: The raw string response from the LLM.
        
    Returns:
        A dictionary containing the parsed data or an error dict if parsing fails.
    """
    if not response_text:
        logger.error("parse_llm_json received None or empty string.")
        return {
            "error": "EMPTY_API_RESPONSE", 
            "raw_output": None
        }

    cleaned_text = response_text.strip()
    
    # Strip common markdown wrappers
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
        
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    cleaned_text = cleaned_text.strip()
    
    try:
        return dict(json.loads(cleaned_text))
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {
            "error": "JSON_PARSE_FAILED", 
            "raw_output": response_text
        }
