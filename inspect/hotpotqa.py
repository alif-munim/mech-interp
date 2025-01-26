from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import (
    solver, chain, prompt_template, generate, system_message
)
import datasets

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

Let's solve this step by step:
1. First, identify the key information we need
2. Find the relevant pieces in the context
3. Connect the information to reach the answer

Explain your reasoning clearly.
Your final answer should be on its own line in the format "Answer: $ANSWER"
""".strip()

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

def record_to_sample(record):
    input = record["question"]
    target = record["answer"]
    context = []
    for i, title in enumerate(record["context"]["title"]):
        sentences = record["context"]["sentences"][i]
        context.append(f"Title: {title}\n" + "\n".join(sentences))
    return Sample(
        input=input,
        target=target,
        metadata={
            "context": "\n\n".join(context),
        }
    )

@task
def hotpot_qa(fewshot=5, fewshot_seed=42, solver_name="chain_of_thought"):
    # Build fewshot examples if needed
    system_msg = ""
    if fewshot:
        dataset = datasets.load_dataset("hotpot_qa", "distractor", split="train", trust_remote_code=True)
        examples = [record_to_sample(record) for record in dataset.select(range(fewshot))]
        fewshots = []
        for ex in examples:
            fewshots.append(
                f"Question: {ex.input}\n\n"
                f"Context:\n{ex.metadata['context']}\n\n"
                f"Answer: {ex.target}"
            )
        system_msg = "Here are some example questions and answers:\n\n" + "\n\n".join(fewshots)

    # Select solver based on parameter
    solver_fn = chain_of_thought if solver_name == "chain_of_thought" else direct

    # Add system message to solver if we have fewshot examples
    solver = solver_fn()
    if system_msg:
        solver = chain(system_message(system_msg), solver)

    # Load validation dataset
    dataset = datasets.load_dataset(
        "hotpot_qa",
        "distractor",
        split="validation",
        trust_remote_code=True
    )
    validation_samples = [record_to_sample(record) for record in dataset]

    return Task(
        dataset=validation_samples,
        solver=solver,
        scorer=match()
    )
