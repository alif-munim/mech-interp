# Inspect
https://inspect.ai-safety-institute.org.uk/

 Inspect is a framework designed by UK AISI for large language model evaluations. It comes with tools for prompt engineering, tool usage, multi-turn dialog, and model graded evals.

 ### Setup
 Set your API key.
 ```bash
 export OPENAI_API_KEY=your-openai-api-key
 ```

Create your eval file, and then run the eval.
```bash
inspect eval theory.py --model openai/gpt-4o-mini
```

Open a log viewer in your browser.
```bash
inspect view
```


### Multi-Hop
To solve using chain-of-thought, run the following.
```bash
inspect eval hotpotqa.py --limit 5 --model=openai/gpt-4o-mini
```

To solve directly (without chain-of-thought), run the following:
```bash
inspect eval hotpotqa.py --limit 5 --model=openai/gpt-4o-mini -T solver_name=direct
```
