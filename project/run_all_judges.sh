#!/bin/bash

# Exit immediately if a pipeline returns a non-zero status, 
# and treat unset variables as an error.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Path to the directory with generated JSON files
BASE_DIR="${SCRIPT_DIR}/results/1shot_examp/deepseek-v3.2"

# List of techniques. Comment the ones you don't want to evaluate.
TECHNIQUES=(
    "demon"
    "fabul" 
    "fear"
    "label"
    "relativ"
)

echo "=== START BATCH EVALUATION ==="

for TECH in "${TECHNIQUES[@]}"; do
    FILE_PATH="${BASE_DIR}/temp0.7_1shot_${TECH}_deepseek-v3.2_v1.json"
    
    # Check if the source JSON exists
    if [ ! -f "$FILE_PATH" ]; then
        echo "File not found, skipping: $FILE_PATH"
        continue
    fi

    echo ""
    echo "--------------------------------------------------------"
    echo "▶▶▶ STARTING EVALUATION FOR: ${TECH^^}"
    echo "--------------------------------------------------------"
    
    # Run the python evaluator script
    python run_judge.py --input_json "$FILE_PATH"

done

echo ""
echo "=== ALL EVALUATIONS COMPLETED! ==="