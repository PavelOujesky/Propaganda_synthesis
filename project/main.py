import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

# Import our custom modules and the Pydantic data model
import utils
from schemas import PropagandaOutput
from llm_client import call_openai_api_guided

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config.json"


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def read_dataset(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Reads data from a JSON file and unifies it into a standard format.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary containing dataset settings.
        
    Returns:
        List[Dict[str, Any]]: A list of normalized data items ready for processing.
    """
    dataset_rel_path = config.get("dataset_path", "datasets/D_input.json")
    dataset_path = PROJECT_ROOT / dataset_rel_path

    raw_data = utils.load_json(dataset_path)
    
    if not raw_data: 
        return []
        
    normalized_data: List[Dict[str, Any]] = []
    for item in raw_data:
        content = item.get("content", {})
        # ensure_ascii=False is crucial here to preserve Czech diacritics in the input payload
        json_input_for_model = json.dumps(content, ensure_ascii=False, indent=2)
        
        normalized_data.append({
            "id": item.get("id"),
            "text": json_input_for_model,
            "theme": item.get("theme"),
            # Extract any remaining keys dynamically so metadata is not lost in final output
            "metadata": {k: v for k, v in item.items() if k not in ["id", "content", "theme"]}
        })
        
    return normalized_data


def record_experiment_time(
    start_time: float, 
    end_time: float, 
    config: Dict[str, Any], 
    output_filepath: Path, 
    base_dir: Path
) -> None:
    """
    Calculates the execution duration and appends the experiment log to a batch report file.
    
    Args:
        start_time (float): The timestamp when the experiment started.
        end_time (float): The timestamp when the experiment finished.
        config (Dict[str, Any]): The configuration dictionary containing experiment metadata.
        output_filepath (Path): The path where the final experiment results were saved.
        base_dir (Path): The base directory for generating the 'time_reports' folder.
        
    Returns:
        None
    """
    duration = end_time - start_time
    
    run_name = config.get("run_name", "unnamed")
    model = config.get("model", "unknown")
    dataset_path = config.get("dataset_path", "unknown")
    run_id = config.get("run_id", "0")

    log_msg = (
        f"Experiment: {run_name} | Model: {model} | "
        f"Dataset: {dataset_path} | Time: {duration:.2f}s | "
        f"Saved: {output_filepath.name}"
    )

    report_dir = base_dir / "time_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"batch_report_{run_id}.txt"

    try:
        # Append mode ('a') ensures we don't overwrite previous timing logs in the same batch
        with report_file.open("a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
        logger.info(f"  --> Time recorded in: {report_file}")
    except Exception as e:
        logger.warning(f"  WARNING: Could not append to time log. Error: {e}")


def run_experiment(config: Dict[str, Any], dataset: List[Dict[str, Any]]) -> None:
    """
    Processes an experiment loop, calls the LLM, measures time, and saves results.
    
    Args:
        config (Dict[str, Any]): Configuration specific to this experiment run.
        dataset (List[Dict[str, Any]]): The preprocessed dataset to iterate over.
    """
    start_time = time.time()

    # Extract configs
    run_id = config.get("run_id", "0")
    run_name = config.get("run_name", "unnamed")
    model = config.get("model")
    
    if not model:
        logger.error("  SKIPPING: The model specification is missing from the configuration.")
        return
        
    cleaned_model_name = config.get("cleaned_model_name", "unknown_model")
    prompt_path = PROJECT_ROOT / config.get("system_prompt_path", "")
    dataset_path = config.get("dataset_path", "unknown")
    base_result_dir = PROJECT_ROOT / config.get("base_result_dir", "results/")
    few_shot_name = config.get("few_shot_name", "unnamed")
    
    logger.info(f"--> Starting experiment: {run_name} (Model: {model})")

    try:
        system_prompt = utils.load_prompt_text(prompt_path)
        if system_prompt is None:
            logger.error(f"  SKIPPING: system_prompt from {prompt_path} is None.")
            return
    except FileNotFoundError as e:
        logger.error(f"  SKIPPING: {e}")
        return

    results: List[Dict[str, Any]] = []
    logger.info(f"  Processing {len(dataset)} items from {dataset_path}...")
    
    with logging_redirect_tqdm():
        for item in tqdm(dataset, desc=f"Generating {run_name}"):
            try:
                # Call the guided decoding API and enforce the PropagandaOutput schema
                raw_response, finish_reason, reasoning_text, temperature, seed = call_openai_api_guided(
                    system_prompt=system_prompt,
                    user_prompt=item["text"], 
                    model=model,
                    pydantic_model=PropagandaOutput
                )
                
                # Handle None: if the API does not return text, we'll throw an error
                if raw_response is None:
                    raise ValueError("The API returned an empty response (None).")
                    
                parsed_output = utils.parse_llm_json(raw_response)
                
            except Exception as e:
                # Catch-all exception ensures that one failed API call (e.g., timeout, rate limit) 
                # doesn't crash the entire batch processing.
                logger.error(f"  Error at ID {item['id']}: {e}", exc_info=True)
                parsed_output = {"error": "API_CALL_FAILED", "details": str(e)}
                finish_reason = "error"
                temperature = None  # type: ignore
                seed = None  # type: ignore
                reasoning_text = None

            results.append({
                "id": item["id"],
                "theme": item["theme"],
                "original_input": json.loads(item["text"]), 
                "synthesised_output": parsed_output,
                "finish_reason": finish_reason,
                "temperature": temperature,
                "seed": seed,
                "reasoning": reasoning_text,
                "config_used": config,
                **item["metadata"] 
            })

    output_filename = f"{run_name}_v{run_id}.json"
    output_filepath = base_result_dir / few_shot_name / cleaned_model_name / output_filename
    
    utils.save_results_to_json(results, output_filepath)

    end_time = time.time()
    record_experiment_time(
        start_time=start_time,
        end_time=end_time,
        config=config,
        output_filepath=output_filepath,
        base_dir=base_result_dir
    )


def main() -> None:
    """Main execution function that orchestrates the configuration and experiment runs."""
    config_data = utils.load_json(CONFIG_FILE)
    if not config_data:
        return

    # Extract global settings and experiments to enforce DRY principle
    global_settings = config_data.get("global_settings", {})
    experiments = config_data.get("experiments", [])

    logger.info(f"--- START: Found {len(experiments)} experiments ---")

    for experiment in experiments:
        # Merge dictionaries using unpacking operator (**). 
        # Specific experiment settings will overwrite global settings if keys overlap.
        master_config = {**global_settings, **experiment}
        
        dataset = read_dataset(master_config)
        if not dataset:
            logger.warning(f"  WARNING: No data for config '{master_config.get('run_name')}', skipping.")
            continue

        system_prompt_paths = master_config.get("system_prompt_paths", [])
        models = master_config.get("models", [])

        for prompt_path_str in system_prompt_paths:
            prompt_path = Path(prompt_path_str)
            
            # Extract technique name dynamically from the prompt file name (e.g., 'demon_system_prompt.txt' -> 'demon')
            manipul_technique_name = prompt_path.name.split("_")[0] 
            
            for model in models:
                # Sanitize model name for filesystem paths to prevent directory traversal issues
                cleaned_model_name = model.replace("/", "-").replace(":", "-")
                
                dynamic_run_name = f"{master_config.get('run_name')}_{manipul_technique_name}_{cleaned_model_name}"

                sub_config = {
                    "run_id": master_config.get("run_id", "0"),
                    "run_name": dynamic_run_name,
                    "few_shot_name": master_config.get("few_shot_name", "unnamed"),
                    "system_prompt_path": str(prompt_path),
                    "dataset_path": master_config.get("dataset_path"),
                    "base_result_dir": master_config.get("base_result_dir", "results/"),
                    "model": model,
                    "cleaned_model_name": cleaned_model_name
                }

                run_experiment(sub_config, dataset)

    logger.info("\n--- ALL DONE ---")


if __name__ == "__main__":
    main()
