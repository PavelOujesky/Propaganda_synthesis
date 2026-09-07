"""
LLM-as-a-Judge Evaluator Script (Fragmented Version - FULL DATASET).

This module processes synthesized propaganda data and evaluates it using
a specified Large Language Model. It enforces the Single Responsibility Principle
by separating argument parsing, schema selection, evaluation logic, and orchestration.
It supports fragmented evaluation (prompts split into 3 parts) to avoid context window overload
and runs on the entire provided dataset.
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Type

from pydantic import BaseModel
from tqdm import tqdm

import utils
from llm_client import call_openai_api_guided
from schemas import (
    JudgeOutput10_Chunk1, JudgeOutput10_Chunk2, JudgeOutput10_Chunk3,
    JudgeOutput11_Chunk1, JudgeOutput11_Chunk2, JudgeOutput11_Chunk3
)

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================

CURRENT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = CURRENT_DIR / "LLM_as_a_Judge" / "fragmented_prompts"
TIME_REPORTS_DIR = CURRENT_DIR / "results" / "time_reports"

EVAL_MODEL: str = "kimi-k2.5"
SUFIX: str = "llm_eval_kimi"

TECHNIQUES_WITH_11_CRITERIA: List[str] = ["demon", "label"]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Silence the noisy httpx library used by the OpenAI client
logging.getLogger("httpx").setLevel(logging.WARNING)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def parse_arguments() -> Path:
    """Parses command-line arguments and returns the input file path."""
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge evaluator for propaganda")
    parser.add_argument(
        "--input_json", 
        type=str, 
        required=True, 
        help="Path to the input JSON file (e.g., temp0.7_1shot_fabul_deepseek-v3.2_v1.json)"
    )
    args = parser.parse_args()
    return Path(args.input_json)


def get_schema_for_chunk(technique: str, chunk_id: int) -> Type[BaseModel]:
    """Returns the appropriate Pydantic schema based on technique (10 or 11) and chunk number."""
    is_11_criteria = technique in TECHNIQUES_WITH_11_CRITERIA
    
    if is_11_criteria:
        if chunk_id == 1: return JudgeOutput11_Chunk1
        elif chunk_id == 2: return JudgeOutput11_Chunk2
        elif chunk_id == 3: return JudgeOutput11_Chunk3
    else:
        if chunk_id == 1: return JudgeOutput10_Chunk1
        elif chunk_id == 2: return JudgeOutput10_Chunk2
        elif chunk_id == 3: return JudgeOutput10_Chunk3
        
    raise ValueError(f"Invalid state for technique '{technique}' and chunk {chunk_id}")


def evaluate_items(
    synthetic_data: List[Dict[str, Any]], 
    system_prompt: str, 
    technique: str,
    chunk_id: int,
    selected_model: Type[BaseModel]
) -> List[Dict[str, Any]]:
    """
    Iterates through the data, calls the LLM, and parses responses for a specific prompt chunk.
    """
    results: List[Dict[str, Any]] = []

    # The first chunk prints the total count; the rest just run silently
    if chunk_id == 1:
        logger.info(f"-> Evaluating all {len(synthetic_data)} items in the dataset.")

    # Iterate through the entire dataset
    for item in tqdm(synthetic_data, desc=f"{technique.upper()} - Part {chunk_id} ({EVAL_MODEL})"):
        item_id = item.get("id")
        
        payload = {
            "original_input": item.get("original_input"),
            "synthesised_output": item.get("synthesised_output")
        }
        
        user_prompt = f"Please evaluate the following synthesized propaganda:\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"

        try:
            raw_response, _, _, _, _ = call_openai_api_guided(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=EVAL_MODEL,
                pydantic_model=selected_model,
                temperature=0.1
            )
            
            if not raw_response:
                raise ValueError("API returned an empty response.")

            llm_eval = utils.parse_llm_json(raw_response)

            # Basic structure common to all chunks
            parsed_result = {
                "id": item_id,
                "chain_of_thought": llm_eval.get("chain_of_thought", {}),
                "violated_criteria": sorted(llm_eval.get("violated_criteria", []))
            }
            
            # We only add the `is_pro_chinese` attribute if we are currently evaluating Chunk 1
            if chunk_id == 1:
                parsed_result["is_pro_chinese"] = llm_eval.get("is_pro_chinese", False)
                
            results.append(parsed_result)

        except Exception as e:
            logger.error(f"\nError at ID {item_id}: {e}", exc_info=True)

    return results


def save_time_report(technique: str, filename: str, items_count: int, duration: float, output_name: str) -> None:
    """Appends execution time and statistics to a unified log file."""
    TIME_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = TIME_REPORTS_DIR / "judge_time_report.txt"
    
    log_msg = (f"Technique: {technique.upper()} | Model: {EVAL_MODEL} | "
               f"File: {filename} | Items evaluated: {items_count} | "
               f"Time: {duration:.2f}s | Saved: {output_name}")
               
    try:
        with open(report_file, "a", encoding="utf-8") as rf:
            rf.write(log_msg + "\n")
    except Exception as e:
        logger.warning(f"-> Warning: Failed to save the time report. Error: {e}")


# ==========================================
# MAIN ORCHESTRATOR
# ==========================================

def main() -> None:
    """
    Main execution pipeline orchestrator.
    Handles the fragmentation logic: loops 3 times for each prompt chunk.
    """
    input_path = parse_arguments()
    
    # Find which known technique is in the filename
    all_known_techniques = TECHNIQUES_WITH_11_CRITERIA + ["fear", "fabul", "relativ"]
    technique = next((t for t in all_known_techniques if t in input_path.stem), None)
    
    if not technique:
        logger.error(f"Error: Could not identify a valid technique in filename '{input_path.name}'.")
        return

    logger.info(f"\n======================================")
    logger.info(f"-> Processing technique: {technique.upper()}")
    logger.info(f"-> Using evaluator model: {EVAL_MODEL}")
    logger.info(f"======================================\n")

    synthetic_data = utils.load_json(input_path)
    if not synthetic_data:
        logger.error("Error: Failed to load the input data.")
        return

    output_dir = input_path.parent / "llm_evals"
    # Ensure the evaluations directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Cycle for three separate prompts
    for chunk_id in range(1, 4):
        prompt_path = PROMPTS_DIR / f"{technique}_prompt{chunk_id}.md"
        output_json_path = output_dir / f"{input_path.stem}_{SUFIX}{chunk_id}.json"

        # Load input prompt
        try:
            system_prompt = utils.load_prompt_text(prompt_path)
        except FileNotFoundError:
            logger.error(f"Error: Prompt '{prompt_path}' does not exist. Skipping chunk {chunk_id}.")
            continue

        # Setup schema for this specific chunk
        selected_model = get_schema_for_chunk(technique, chunk_id)

        # Execute evaluation
        start_time = time.time()
        results_for_json = evaluate_items(synthetic_data, system_prompt, technique, chunk_id, selected_model)
        duration = time.time() - start_time

        # Save output data
        utils.save_results_to_json(results_for_json, output_json_path)

        # Save metrics
        save_time_report(technique, input_path.name, len(results_for_json), duration, output_json_path.name)
        logger.info(f"-> Chunk {chunk_id} Done! Saved to: {output_json_path.name}\n")


if __name__ == "__main__":
    main()