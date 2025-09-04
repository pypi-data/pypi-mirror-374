from pybiomedlink.linker import BM25Linker

def test_bm25_predict():
    corpus = [
    "Hello there good man!",
    "It is quite windy in London",
    "How is the weather today?"
    ]
    query = "windy London"

    bm25_linker = BM25Linker(corpus)
    top_k = 3
    predictions = bm25_linker.predict(query, top_k)
    print(f"Predictions for query '{query}': {predictions}")

    assert isinstance(predictions, list)
    assert len(predictions) == top_k, "Expected number of predictions does not match top_k"
    assert all(isinstance(pred, str) for pred in predictions)

def test_bm25_predict_aux():
    corpus = [
    "Hello there good man!",
    "It is quite windy in London",
    "How is the weather today?"
    ]
    query = "windy London"

    bm25_linker = BM25Linker(corpus)
    top_k = 3
    predictions = bm25_linker.predict_aux(query, top_k)
    print(f"Predictions for query '{query}': {predictions}")

    assert isinstance(predictions, dict)
    assert "labels" in predictions and "scores" in predictions, "Expected keys 'labels' and 'scores' in predictions"
    assert len(predictions["labels"]) == top_k, "Expected number of labels does not match top_k"
    assert len(predictions["scores"]) == top_k, "Expected number of scores does not match top_k"