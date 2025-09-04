# pyBioMedLink
[![PyPI version](https://img.shields.io/pypi/v/pyBioMedLink)](https://pypi.org/project/pyBioMedLink/)
![License](https://img.shields.io/pypi/l/pyBioMedLink)
![Python versions](https://img.shields.io/pypi/pyversions/pyBioMedLink)

*pyBioMedLink* is an open-source python library for bio-medical term linking.


## Usage

### Use Case 1 for BioDomain Linking using Qwen3
```Python
corpus = [
"Epigenetic",
"DNA Repair",
"Metal Binding and Homeostasis"
"Synapse",
"Immune System",
"Cell Cycle",
"Lipid Metabolism",
"Vasculature",
]
query = "aging"

linker = Qwen3PromptLinker(
    corpus,
    model_name="Qwen/Qwen3-0.6B"
    )
top_k = 3
predictions = linker.predict_aux(query, top_k)
print(f"Predictions for query '{query}': {predictions}")
# {'labels': ['Cell Cycle', 'DNA Repair', 'Epigenetic'], "thinking_content": ..., "content": ..., "error_msg": ...}
```

### Use Case 2 for IR baselines
```Python
from pybiomedlink.linker import BM25Linker

corpus = [
"Hello there good man!",
"It is quite windy in London",
"How is the weather today?"
]
query = "windy London"

bm25_linker = BM25Linker(corpus)
top_k = 2
predictions = bm25_linker.predict(query, top_k)
print(f"Predictions for query '{query}': {predictions}")
# ['It is quite windy in London', 'How is the weather today?']

pred_score_results = bm25_linker.predict_aux(query, top_k)
print(f"Predictions with scores for query '{query}': {pred_score_results}")
# {'labels': ['It is quite windy in London', 'How is the weather today?', 'Hello there good man!'], 'scores': [0.9372947225064051, 0.0, 0.0]}
```

## Supported Models

**Zero-shot models:**
- BM25Linker: A BM25-based linker
- LevenshteinLinker: A Levenshtein distance-based linker
- TransformerEmbLinker: A Transformer-based embedding linker
- Qwen3PromptLinker: A Qwen3-based prompt linker. **Note:** can only return a ranked list without scores.


## How to run tests
To run the tests, you can use the following command:
```bash
uv run python -m pytest -v tests/
uv run python -m pytest -v -s tests/test_Transformer.py
```