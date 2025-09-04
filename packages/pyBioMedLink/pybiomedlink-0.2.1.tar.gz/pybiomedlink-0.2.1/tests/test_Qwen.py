from pybiomedlink.linker import Qwen3PromptLinker

def test_Qwen3Prompt_predict_aux():
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
    # enable thinking mode
    predictions = linker.predict_aux(query, top_k)
    print(f"Predictions for query '{query}': {predictions}")

    assert isinstance(predictions, dict)
    assert len(predictions["labels"]) == top_k, "Expected number of predictions does not match top_k"
    assert "labels" in predictions, "Expected keys 'labels' in predictions"

    # unable thinking mode
    predictions = linker.predict_aux(query, top_k, enable_thinking=False)
    print(f"[NO-Thinking] Predictions for query '{query}': {predictions}")
    assert isinstance(predictions, dict)
    assert len(predictions["labels"]) == top_k, "Expected number of predictions does not match top_k"
    assert "labels" in predictions, "Expected keys 'labels' in predictions"