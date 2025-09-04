from pybiomedlink.linker import LevenshteinLinker

def test_levenshtein_dist():
    s1 = "rain"
    s2 = "shine"
    expected_distance = 3  # “rain” -> “sain” -> “shin” -> “shine”.
    distance = LevenshteinLinker.edit_distance(s1, s2)
    print(f"Levenshtein distance between '{s1}' and '{s2}': {distance}")
    assert distance == expected_distance, f"Expected {expected_distance}, got {distance}"

    s3 = "train"
    expected_distance2 = 1  # “rain” -> “train”
    distance2 = LevenshteinLinker.edit_distance(s1, s3)
    print(f"Levenshtein distance between '{s1}' and '{s3}': {distance2}")
    assert distance2 == expected_distance2, f"Expected {expected_distance2}, got {distance2}"

    s4 = "rainbows"
    expected_distance3 = 4  # “rain” -> “rainb” -> “rainbo” -> “rainbow” -> “rainbows”
    distance3 = LevenshteinLinker.edit_distance(s1, s4)
    print(f"Levenshtein distance between '{s1}' and '{s4}': {distance3}")
    assert distance3 == expected_distance3, f"Expected {expected_distance3}, got {distance3}"

def test_levenshtein_predict():
    labels = ["rain", "shine", "train", "rainbows"]
    linker = LevenshteinLinker(labels)
    
    query = "rain"
    top_k = 2
    predictions = linker.predict(query, top_k)
    print(f"Predictions for query '{query}': {predictions}")
    assert isinstance(predictions, list)
    assert len(predictions) == top_k, "Expected number of predictions does not match top_k"
    assert all(isinstance(pred, str) for pred in predictions)

def test_levenshtein_predict_aux():
    labels = ["rain", "shine", "train", "rainbows"]
    linker = LevenshteinLinker(labels)
    
    query = "rain"
    top_k = 2
    predictions = linker.predict_aux(query, top_k)
    print(f"Auxiliary predictions for query '{query}': {predictions}")
    
    assert isinstance(predictions, dict)
    assert "labels" in predictions and "scores" in predictions, "Expected keys 'labels' and 'scores' in predictions"
    assert len(predictions["labels"]) == top_k, "Expected number of labels does not match top_k"
    assert len(predictions["scores"]) == top_k, "Expected number of scores does not match top_k"