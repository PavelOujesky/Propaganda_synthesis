from pydantic import BaseModel
from typing import List

# ==========================================
# 1. MAIN OUTPUT MODEL
# ==========================================

class PropagandaOutput(BaseModel):
    """Data model for the synthesized propaganda output."""
    output_sentence: str
    manipulation_occurrences: List[str]
    intent: str
    perspective: str

class JudgeChainOfThought10(BaseModel):
    """Chain of thought reasoning for the 10-criteria evaluator."""
    criterion_1: str
    criterion_2: str
    criterion_3: str
    criterion_4: str
    criterion_5: str
    criterion_6: str
    criterion_7: str
    criterion_8: str
    criterion_9: str
    criterion_10: str
    bias_analysis: str

class JudgeOutput10(BaseModel):
    """Final output structure for the 10-criteria evaluator."""
    chain_of_thought: JudgeChainOfThought10
    violated_criteria: List[int]
    is_pro_chinese: bool

class JudgeChainOfThought11(BaseModel):
    """Chain of thought reasoning for the 11-criteria evaluator."""
    criterion_1: str
    criterion_2: str
    criterion_3: str
    criterion_4: str
    criterion_5: str
    criterion_6: str
    criterion_7: str
    criterion_8: str
    criterion_9: str
    criterion_10: str
    criterion_11: str
    bias_analysis: str

class JudgeOutput11(BaseModel):
    """Final output structure for the 11-criteria evaluator."""
    chain_of_thought: JudgeChainOfThought11
    violated_criteria: List[int]
    is_pro_chinese: bool


# ==========================================
# 2. EVALUATION (JUDGE) 10-CRITERIA MODELS
# ==========================================
class JudgeChainOfThought10_Chunk1(BaseModel):
    criterion_1: str
    criterion_2: str
    bias_analysis: str

class JudgeOutput10_Chunk1(BaseModel):
    chain_of_thought: JudgeChainOfThought10_Chunk1
    violated_criteria: List[int]
    is_pro_chinese: bool

class JudgeChainOfThought10_Chunk2(BaseModel):
    criterion_3: str
    criterion_4: str
    criterion_5: str
    criterion_6: str

class JudgeOutput10_Chunk2(BaseModel):
    chain_of_thought: JudgeChainOfThought10_Chunk2
    violated_criteria: List[int]

class JudgeChainOfThought10_Chunk3(BaseModel):
    criterion_7: str
    criterion_8: str
    criterion_9: str
    criterion_10: str

class JudgeOutput10_Chunk3(BaseModel):
    chain_of_thought: JudgeChainOfThought10_Chunk3
    violated_criteria: List[int]


# ==========================================
# EVALUATION (JUDGE) 11-CRITERIA MODELS
# ==========================================
class JudgeChainOfThought11_Chunk1(BaseModel):
    criterion_1: str
    criterion_2: str
    criterion_3: str
    bias_analysis: str

class JudgeOutput11_Chunk1(BaseModel):
    chain_of_thought: JudgeChainOfThought11_Chunk1
    violated_criteria: List[int]
    is_pro_chinese: bool

class JudgeChainOfThought11_Chunk2(BaseModel):
    criterion_4: str
    criterion_5: str
    criterion_6: str
    criterion_7: str

class JudgeOutput11_Chunk2(BaseModel):
    chain_of_thought: JudgeChainOfThought11_Chunk2
    violated_criteria: List[int]

class JudgeChainOfThought11_Chunk3(BaseModel):
    criterion_8: str
    criterion_9: str
    criterion_10: str
    criterion_11: str

class JudgeOutput11_Chunk3(BaseModel):
    chain_of_thought: JudgeChainOfThought11_Chunk3
    violated_criteria: List[int]

