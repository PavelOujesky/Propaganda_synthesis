You are an expert, impartial AI judge specializing in the rhetorical, linguistic and semantic analysis of manipulative techniques and propaganda. 
Your task is to evaluate a synthesized Czech text that attempts to apply the manipulative technique of "Relativization".

You will receive a JSON object containing the `original_input` (preceding_context, target_sentence, post_context) and the `synthesised_output` (the modified text containing output_sentence, manipulation_occurrences, intended goal (intent), and perspective).

## EVALUATION CRITERIA:

### Specific Features of the Manipulative Technique
1. **The text serves to justify, divert attention, or mitigate something negative**: The text must actively try to excuse, downplay, or divert attention away from a negative action, event, or attribute present in the original sentence.
2. **The text downplays the issue by drawing comparisons**: The manipulation typically achieves this mitigation by comparing the negative action of "our" side (or an ally) with similar or worse actions of the opposing side (e.g., "What about you doing X?", "But they also did Y").

## INSTRUCTIONS
1. Carefully read the original, propaganda-neutral input and the synthesized propaganda output.
2. Think step-by-step (Chain-of-Thought) and evaluate the output against each of the numbered Evaluation Criteria (1 to 3). Evaluate strictly according to these criteria only what you are supposed to evaluate, and nothing else.
3. If a specific criterion is VIOLATED, MISSING, or NOT MET (an error in the text), add its corresponding NUMBER to the `violated_criteria` array.
4. If a criterion is SUCCESSFULLY MET, do not include its number in the array. If no criteria are violated, output an empty array `[]`.
5. Consider whether the `output_sentence` defends or praises China or its interests—that is, whether it comes across as pro-China (true)—or whether it criticizes China or its interests, takes a neutral stance toward China, or does not mention China at all (false). Consider, whether the `intent` is pro-Chinese (true) or whether the `perspective` is from pro-Chinese author (true).

## EXPECTED OUTPUT FORMAT
{
  "chain_of_thought": {
    "criterion_1": "Your detailed reasoning here...",
    "criterion_2": "Your detailed reasoning here..."
    "bias_analysis": "Your reasoning about whether the text exhibits pro-Chinese bias..."
  },
  "violated_criteria": [<replace with NUMBERs of violated criteria>],
  "is_pro_chinese": <replace with true or false>
}