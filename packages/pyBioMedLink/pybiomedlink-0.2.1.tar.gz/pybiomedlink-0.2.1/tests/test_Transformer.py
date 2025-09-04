from pybiomedlink.linker import TransformerEmbLinker

def test_TransformerEmb_predict():
    corpus = [
    "Epigenetic",
    "DNA Repair",
    "Metal Binding and Homeostasis"
    ]
    query = "aging"

    linker = TransformerEmbLinker(
        corpus,
        model_name="cambridgeltl/SapBERT-from-PubMedBERT-fulltext"
        )
    top_k = 3
    predictions = linker.predict(query, top_k)
    print(f"Predictions for query '{query}': {predictions}")

    assert isinstance(predictions, list)
    assert len(predictions) == top_k, "Expected number of predictions does not match top_k"
    assert all(isinstance(pred, str) for pred in predictions)
