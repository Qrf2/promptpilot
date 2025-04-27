import re
import logging
import random
from typing import Dict, List, Optional
import models_config as mc
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Few-shot examples for prompt analysis and optimization
FEW_SHOT_EXAMPLES = [
    {
        "bad_prompt": "Write a story",
        "issues": ["Vague task", "Lacks context", "No specificity"],
        "good_prompt": "Write a 500-word fantasy story about a young mage discovering their powers in a medieval village, including vivid descriptions of the setting and a key conflict."
    },
    {
        "bad_prompt": "Summarize this text",
        "issues": ["Missing text input", "Unclear length or style", "No audience specified"],
        "good_prompt": "Summarize the following 1000-word article into 200 words, focusing on key points for a general audience: [text]."
    }
]

def analyze_prompt(prompt: str) -> Dict:
    """
    Analyzes a prompt for common issues using chain-of-thought reasoning.
    
    Args:
        prompt: The input prompt to analyze.
    
    Returns:
        A dictionary containing identified issues and suggestions.
    """
    logger.info("Starting prompt analysis...")
    analysis = {"issues": [], "suggestions": [], "score": 0}

    # Chain-of-thought reasoning
    steps = []

    # Step 1: Check for clarity
    if len(prompt.split()) < 5 or not any(keyword in prompt.lower() for keyword in ["write", "summarize", "generate", "explain"]):
        steps.append("Prompt is too vague or lacks a clear task.")
        analysis["issues"].append("Vague or unclear task")
        analysis["suggestions"].append("Specify the task explicitly (e.g., 'write', 'summarize').")

    # Step 2: Check for context
    if not re.search(r"\b(context|background|setting)\b", prompt.lower()):
        steps.append("Prompt lacks context or background information.")
        analysis["issues"].append("Missing context")
        analysis["suggestions"].append("Provide context such as audience, purpose, or background.")

    # Step 3: Check for specificity
    if not re.search(r"\b(length|word count|style|tone|format)\b", prompt.lower()):
        steps.append("Prompt lacks specific requirements like length or style.")
        analysis["issues"].append("Lacks specificity")
        analysis["suggestions"].append("Include details like word count, tone, or format.")

    # Step 4: Check for examples or constraints
    if not re.search(r"\b(example|sample|constraint|limit)\b", prompt.lower()):
        steps.append("Prompt could benefit from examples or constraints.")
        analysis["issues"].append("No examples or constraints")
        analysis["suggestions"].append("Add examples or constraints to guide the model.")

    # Step 5: Few-shot learning comparison
    for example in FEW_SHOT_EXAMPLES:
        if any(issue in analysis["issues"] for issue in example["issues"]):
            steps.append(f"Similar to bad prompt: '{example['bad_prompt']}'. Suggest: '{example['good_prompt']}'")
            analysis["suggestions"].append(f"Model after: '{example['good_prompt']}'")

    # Calculate a simple score (0-100)
    max_issues = 4
    analysis["score"] = max(0, 100 - (len(analysis["issues"]) * 25))

    analysis["reasoning_steps"] = steps
    logger.info(f"Analysis complete: {analysis}")
    return analysis

def optimize_prompt(prompt: str, analysis: Dict) -> str:
    """
    Optimizes a prompt based on analysis results.
    
    Args:
        prompt: The original prompt.
        analysis: The analysis dictionary from analyze_prompt.
    
    Returns:
        An optimized version of the prompt.
    """
    logger.info("Starting prompt optimization...")
    optimized = prompt

    # Role-based prompt engineering
    role_prompt = "You are an expert AI prompt engineer tasked with improving prompts for clarity, specificity, and effectiveness."

    # Apply suggestions
    for suggestion in analysis["suggestions"]:
        if "Specify the task" in suggestion:
            optimized = f"{role_prompt} {optimized.strip()}."
        if "Provide context" in suggestion:
            optimized = f"{optimized} For a general audience, assuming no prior knowledge."
        if "Include details" in suggestion:
            optimized = f"{optimized} Aim for 200-500 words in a clear, professional tone."
        if "Add examples" in suggestion:
            optimized = f"{optimized} For example, include key details like [example detail]."

    # Few-shot optimization
    for example in FEW_SHOT_EXAMPLES:
        if any(issue in analysis["issues"] for issue in example["issues"]):
            optimized = f"{optimized} (Similar to: {example['good_prompt']})"

    logger.info(f"Optimized prompt: {optimized}")
    return optimized

def test_prompt(prompt: str, model: str, iterations: int = 1) -> str:
    """
    Tests a prompt using the OpenRouter API.
    
    Args:
        prompt: The prompt to test.
        model: The OpenRouter model to use (e.g., 'meta-llama/llama-3.1-8b-instruct:free').
        iterations: Number of test runs.
    
    Returns:
        The model output or aggregated outputs.
    """
    logger.info(f"Testing prompt with model {model} for {iterations} iterations...")
    try:
        client = mc.get_model_client(model)
        outputs = []

        for _ in range(iterations):
            response = client.complete(prompt)
            outputs.append(response)

        # Aggregate outputs
        result = "\n".join([f"Iteration {i+1}: {out}" for i, out in enumerate(outputs)])
        logger.info(f"Test completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error testing prompt: {str(e)}")
        raise

def get_example_prompts() -> List[Dict]:
    """
    Returns the few-shot example prompts.
    
    Returns:
        A list of example prompt dictionaries.
    """
    return FEW_SHOT_EXAMPLES