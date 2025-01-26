from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import (
    solver, chain, prompt_template, generate, system_message
)
import datasets
import pandas as pd
import requests
from io import StringIO

# Define prompts for different approaches
DIRECT_PROMPT = """
Question: {prompt}

Context:
{context}

Provide your answer on its own line in the format "Answer: $ANSWER"
""".strip()

COT_PROMPT = """
Question: {prompt}

Context:
{context}

Break the question down step by step to answer the question.
Explain your reasoning through each step.
Your final answer should be on its own line in the format "Answer: $ANSWER"
""".strip()

def format_decomposition(decomp_list):
    """Format the question decomposition into a readable string"""
    steps = []
    for item in decomp_list:
        steps.append(f"Step {item['sub_id']}: {item['question']}\n"
                    f"- Answer: {item['answer']}\n"
                    f"- Supporting context: {item['paragraph_support_title']}")
    return "\n".join(steps)

def record_to_sample(row):
    # Extract decomposition safely
    try:
        decomposition = format_decomposition(row.get("question_decomposition", []))
    except:
        decomposition = "Decomposition not available"

    return Sample(
        input=row["question"],
        target=row["answer"],
        metadata={
            "context": row.get("context", ""),
            "previous_question": row.get("previous_question", ""),
            "previous_answer": row.get("previous_answer", ""),
            "ques_on_last_hop": row.get("ques_on_last_hop", ""),
            "decomposition": decomposition,
            "reasoning_type": row.get("reasoning_type", "General"),
            "answer_type": row.get("answer_type", "Unknown"),
            "no_of_hops": row.get("no_of_hops", 1)
        }
    )

def sample_to_fewshot(sample, use_cot=True):
    if use_cot:
        return (
            f"Question: {sample.input}\n\n"
            f"Context:\n{sample.metadata['context']}\n\n"
            f"Reasoning Chain:\n"
            f"1. First addressing: {sample.metadata['previous_question']}\n"
            f"   - Found answer: {sample.metadata['previous_answer']}\n\n"
            f"2. Question Decomposition:\n{sample.metadata['decomposition']}\n\n"
            f"3. Final Step ({sample.metadata['reasoning_type']} reasoning):\n"
            f"   Question: {sample.metadata['ques_on_last_hop']}\n\n"
            f"Answer: {sample.target}"
        )
    else:
        return (
            f"Question: {sample.input}\n\n"
            f"Context:\n{sample.metadata['context']}\n\n"
            f"Answer: {sample.target}"
        )

@solver
def direct():
    return chain(
        prompt_template(DIRECT_PROMPT),
        generate()
    )

@solver
def chain_of_thought():
    return chain(
        prompt_template(COT_PROMPT),
        generate()
    )

@task
def morehop_qa(fewshot=5, fewshot_seed=42, solver_name="chain_of_thought"):
    # Load data directly using pandas
    url = "https://huggingface.co/datasets/alabnii/morehopqa/resolve/main/data/with_human_verification.json"
    response = requests.get(url)
    df = pd.read_json(StringIO(response.text))

    # Convert all rows to samples
    all_samples = [record_to_sample(row) for _, row in df.iterrows()]

    # Split into train and validation (using seed for reproducibility)
    import random
    random.seed(fewshot_seed)
    random.shuffle(all_samples)
    split_point = len(all_samples)//2
    train_samples = all_samples[:split_point]
    validation_samples = all_samples[split_point:]

    # Build fewshot examples if needed
    system_msg = ""
    if fewshot:
        examples = train_samples[:fewshot]
        fewshots = [sample_to_fewshot(ex, use_cot=(solver_name=="chain_of_thought"))
                   for ex in examples]
        system_msg = "Here are some example questions and answers:\n\n" + "\n\n".join(fewshots)

    # Select solver based on parameter
    solver_fn = chain_of_thought if solver_name == "chain_of_thought" else direct

    # Add system message to solver if we have fewshot examples
    solver = solver_fn()
    if system_msg:
        solver = chain(system_message(system_msg), solver)

    return Task(
        dataset=validation_samples,  # Limit to 5 samples as requested
        solver=solver,
        scorer=match()
    )
