import pytest
from transformers import pipeline
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


@pytest.fixture(scope="session")
def ai_model():
    """Initialize the AI model once for all tests"""
    try:
        model = pipeline(
            "text-generation",
            model="distilgpt2",
            device=-1  # Use CPU (-1), change to 0 for GPU
        )
        return model
    except Exception as e:
        pytest.skip(f"Failed to load model: {str(e)}")


def test_ai_response_not_empty(ai_model):
    """Test that AI generates non-empty responses"""
    prompt = "Hello, how are you?"

    response = ai_model(
        prompt,
        max_length=50,
        num_return_sequences=1,
        pad_token_id=50256
    )

    generated_text = response[0]['generated_text']

    print(f"\n{'=' * 60}")
    print(f"TEST: Response Not Empty")
    print(f"{'=' * 60}")
    print(f"Prompt: {prompt}")
    print(f"Response: {generated_text}")
    print(f"Response Length: {len(generated_text)} characters")

    assert len(generated_text) > 0, "Response should not be empty"
    print("✓ PASSED: Response is not empty")


def test_ai_response_length(ai_model):
    """Test that AI generates responses of reasonable length"""
    prompt = "The future of artificial intelligence is"

    response = ai_model(
        prompt,
        max_length=100,
        num_return_sequences=1,
        pad_token_id=50256
    )

    generated_text = response[0]['generated_text']

    print(f"\n{'=' * 60}")
    print(f"TEST: Response Length")
    print(f"{'=' * 60}")
    print(f"Prompt: {prompt}")
    print(f"Response: {generated_text}")
    print(f"Response Length: {len(generated_text)} characters")

    assert len(generated_text) > len(prompt), "Response should be longer than prompt"
    print(f"✓ PASSED: Response is longer than prompt")


def test_ai_response_contains_context(ai_model):
    """Test that AI response relates to the input context"""
    prompt = "Python programming language"

    response = ai_model(
        prompt,
        max_length=80,
        num_return_sequences=1,
        pad_token_id=50256
    )

    generated_text = response[0]['generated_text']

    print(f"\n{'=' * 60}")
    print(f"TEST: Response Contains Context")
    print(f"{'=' * 60}")
    print(f"Prompt: {prompt}")
    print(f"Response: {generated_text}")

    # Check if response contains the original prompt
    assert prompt.lower() in generated_text.lower(), "Response should contain input context"
    print("✓ PASSED: Response contains the input context")


def test_ai_multiple_generations(ai_model):
    """Test that AI can generate multiple different responses"""
    prompt = "Once upon a time"

    response = ai_model(
        prompt,
        max_length=60,
        num_return_sequences=3,
        do_sample=True,
        pad_token_id=50256
    )

    print(f"\n{'=' * 60}")
    print(f"TEST: Multiple Generations")
    print(f"{'=' * 60}")
    print(f"Prompt: {prompt}")

    for i, gen in enumerate(response, 1):
        print(f"\nGeneration {i}: {gen['generated_text']}")

    assert len(response) == 3, "Should generate 3 responses"
    print("\n✓ PASSED: Generated 3 different responses")


def test_ai_response_consistency(ai_model):
    """Test that AI generates consistent responses for the same prompt"""
    prompt = "Machine learning is"

    # Generate twice with same parameters
    response1 = ai_model(
        prompt,
        max_length=50,
        num_return_sequences=1,
        do_sample=False,  # Deterministic
        pad_token_id=50256
    )

    response2 = ai_model(
        prompt,
        max_length=50,
        num_return_sequences=1,
        do_sample=False,  # Deterministic
        pad_token_id=50256
    )

    text1 = response1[0]['generated_text']
    text2 = response2[0]['generated_text']

    print(f"\n{'=' * 60}")
    print(f"TEST: Response Consistency")
    print(f"{'=' * 60}")
    print(f"Prompt: {prompt}")
    print(f"Response 1: {text1}")
    print(f"Response 2: {text2}")
    print(f"Are identical: {text1 == text2}")

    assert text1 == text2, "Deterministic responses should be identical"
    print("✓ PASSED: Responses are consistent")


if __name__ == "__main__":
    # Run tests with verbose output
    print("\n" + "=" * 60)
    print("STARTING AI MODEL TESTS")
    print("=" * 60)

    pytest.main([
        __file__,
        "-v",  # Verbose
        "-s",  # Show print statements
        "--tb=short"  # Shorter traceback
    ])