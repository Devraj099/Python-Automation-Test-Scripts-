# --- Mock AI function (replace with real API later) ---
def get_ai_response(prompt: str) -> str:
    """
    Simulates an AI response.
    In real projects, this will call OpenAI / internal AI API.
    """
    mock_responses = {
        "What is AI?": "AI stands for Artificial Intelligence.",
        "Define testing": "Testing is the process of finding defects in software."
    }
    return mock_responses.get(prompt, "")


# --- Basic AI Tests ---

def test_ai_response_not_empty():
    response = get_ai_response("What is AI?")
    assert response != "", "AI response is empty"


def test_ai_response_length():
    response = get_ai_response("What is AI?")
    assert len(response) < 200, "AI response is too long"


def test_ai_response_contains_expected_keyword():
    response = get_ai_response("What is AI?")
    assert "Artificial Intelligence" in response


def test_ai_response_no_hallucination():
    response = get_ai_response("What is AI?")
    forbidden_words = ["unicorn", "magic", "alien"]

    for word in forbidden_words:
        assert word not in response.lower(), f"Hallucination detected: {word}"
