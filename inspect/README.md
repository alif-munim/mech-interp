# Inspect Framework  
[Inspect Framework Documentation](https://inspect.ai-safety-institute.org.uk/)  

**Inspect** is an evaluation framework designed by the UK AI Safety Institute (UK AISI) to analyze and benchmark large language models (LLMs). It provides robust tools for:
- **Prompt engineering**
- **Tool integration and usage**
- **Multi-turn dialogue handling**
- **Model-graded evaluations**

Inspect is particularly suited for tasks requiring detailed reasoning, such as multihop question answering, and supports datasets like **HotpotQA** and **MoreHopQA**.

---

## **Setup**
Before running any evaluations, set up your OpenAI API key:
```bash
export OPENAI_API_KEY=your-openai-api-key
```

Run an evaluation file:
```bash
inspect eval <evaluation_file>.py --model openai/gpt-4o-mini
```

Open the log viewer to analyze results in your browser:
```bash
inspect view
```

## Evaluating with Inspect

### HotpotQA
https://huggingface.co/datasets/hotpotqa/hotpot_qa
HotpotQA is a multihop reasoning dataset focusing on factual questions. Use the following commands to evaluate models with Inspect:

**Chain-of-Thought (CoT) Solver:**
Guides the model to answer questions by reasoning step-by-step.
```bash
inspect eval hotpotqa.py --limit 100 --model=openai/gpt-4o-mini
```

**Direct Solver:**
Answers questions without explicitly reasoning through intermediate steps.
```bash
inspect eval hotpotqa.py --limit 100 --model=openai/gpt-4o-mini -T solver_name=direct
```

### MoreHopQA
https://huggingface.co/datasets/alabnii/morehopqa
MoreHopQA is a more challenging dataset than HotpotQA. It introduces generative answers and tasks requiring advanced reasoning types like symbolic, arithmetic, and commonsense reasoning. It also includes metadata fields to enhance chain-of-thought prompting.

**Chain-of-Thought (CoT) Solver:**
Guides the model to answer questions by reasoning step-by-step.
```bash
inspect eval morehopqa.py --limit 100 --model=openai/gpt-4o-mini
```

**Direct Solver:**
Answers questions without explicitly reasoning through intermediate steps.
```bash
inspect eval morehopqa.py --limit 100 --model=openai/gpt-4o-mini -T solver_name=direct
```

## Results on MoreHopQA

| Solver            | Average Accuracy | Accuracy Range | Tokens Processed       | Total Time (Avg) |
|-------------------|------------------|----------------|------------------------|------------------|
| Chain-of-Thought (5-shot)  | 66%              | 63%-69%        | 399,621 (Input: 372,603, Output: 27,018) | 45.66 seconds     |
| Direct (5-shot)           | 41%              | 40%-43%        | 280,839 (Input: 280,203, Output: 636)    | 6.33 seconds    |
