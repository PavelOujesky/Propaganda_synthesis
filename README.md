# Propaganda Detection Dataset Synthesis

This repository contains the source code and datasets for a Bachelor's thesis focused on synthesizing and evaluating propaganda data using Large Language Models (LLMs). The project consists of automated data generation scripts and an LLM-as-a-Judge evaluation pipeline.

## Attachments Structure

*   `docs/`: Generated HTML documentation of the Python code (using `pdoc`).
*   `project/`: Main source code directory.
    *   `datasets/`: Contains the original input datasets and synthesized outputs.
    *   `prompts/`: Contains system prompts for 0-shot, 1-shot, and 5-shot generation experiments and the prompt for generating the data set.
    *   `LLM_as_a_Judge/`: Contains prompts for the automated evaluation process.
    *   `results/`: Execution logs, generated outputs, and LLM evaluation results.
    *   `config.json`: Global configuration and experiment definitions.
    *   `main.py`: Main orchestrator for synthesizing propaganda data.
    *   `run_judge.py`: Python script for running the LLM-as-a-Judge evaluation.
    *   `run_all_judges.sh`: Bash script for batch execution of evaluations.
*   `temperature_experiments/`: Data and configurations from initial testing phases, focusing on evaluating different model temperatures and settings.
*   `requirements.txt`: List of required Python libraries to run the project.
*   `README.md`: This instruction manual.

## Prerequisites

Ensure you have Python 3.9+ installed.

1.  **Install dependencies:**
    Run the following command in the root directory to install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up Environment Variables:**
    Create a `.env` file inside the `project/` directory and add your API key:
    ```env
    E_INFRA_API_TOKEN=your_actual_api_token_here
    ```
    *Note: Never commit your `.env` file to version control.*

## How to Run

### 1. Data Synthesis
To generate synthesized propaganda text based on the configurations in `config.json`, navigate to the `project/` directory and run:
```bash
cd project
python main.py
```
This will read the `datasets/D_input.json` and generate new data in the `results/` folder, utilizing the prompts specified in the configuration.

### 2. LLM-as-a-Judge Evaluation
To evaluate a specific generated JSON file, use the `run_judge.py` script and provide the path to the file:
```bash
python run_judge.py --input_json results/1shot_examp/deepseek-v3.2/temp0.7_1shot_demon_deepseek-v3.2_v1.json
```

For batch evaluation of multiple manipulation techniques, use the provided bash script (Linux/macOS):
```bash
./run_all_judges.sh
```

## Configuration
The `config.json` file controls the global settings (dataset paths, output directories, used LLMs) and defines individual experiment parameters such as run names, few-shot examples, and paths to system prompts.

## Author
**Pavel František Oujeský**  
Bachelor's Thesis  
Masaryk University, Faculty of Arts & Faculty of Informatics – NLP Centre

## Acknowledgments
This work was supported by the Ministry of Education, Youth and Sports of the Czech Republic through the e-INFRA CZ (ID:90254). 

I also gratefully acknowledge the use of the Propaganda Corpus from the project "Manipulativní techniky propagandy v době internetu" at Masaryk University (MUNI).

## License
- **Code:** Licensed under the [Apache License 2.0](LICENSE).
- **Datasets:** The synthetic dataset and gold standard annotations are licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license.
