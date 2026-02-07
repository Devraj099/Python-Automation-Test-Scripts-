"""
Real ChatGPT Testing Script
Tests OpenAI's GPT models (GPT-3.5-turbo, GPT-4, etc.)
"""

import os
import time
from datetime import datetime
import json

try:
    from openai import OpenAI

    print("✓ OpenAI library loaded successfully")
except ImportError:
    print("❌ Error: openai library not installed")
    print("Install with: pip install openai")
    exit(1)


class ChatGPTTester:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        Initialize ChatGPT Tester

        Args:
            api_key: Your OpenAI API key (or set OPENAI_API_KEY env variable)
            model: Model to use (gpt-3.5-turbo, gpt-4, gpt-4-turbo, etc.)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Either:\n"
                "1. Pass api_key parameter, or\n"
                "2. Set OPENAI_API_KEY environment variable"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.test_results = []

    def _make_request(self, messages, **kwargs):
        """Make a request to ChatGPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def test_basic_response(self):
        """Test 1: Basic response generation"""
        print("\n" + "=" * 70)
        print("TEST 1: Basic Response Generation")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "Say 'Hello, I am ChatGPT!' and nothing else."}
        ]

        print(f"Prompt: {messages[0]['content']}")
        start_time = time.time()

        response = self._make_request(messages, max_tokens=50, temperature=0)

        if response:
            elapsed = time.time() - start_time
            result = response.choices[0].message.content

            print(f"Response: {result}")
            print(f"Response Time: {elapsed:.2f}s")
            print(f"Tokens Used: {response.usage.total_tokens}")
            print(f"Model: {response.model}")

            test_passed = len(result) > 0
            print(f"✓ PASSED" if test_passed else "❌ FAILED")

            self.test_results.append({
                "test": "Basic Response",
                "passed": test_passed,
                "response_time": elapsed,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_conversation_context(self):
        """Test 2: Multi-turn conversation with context"""
        print("\n" + "=" * 70)
        print("TEST 2: Conversation Context Memory")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "My name is John and I like pizza."},
            {"role": "assistant", "content": "Nice to meet you, John! Pizza is delicious."},
            {"role": "user", "content": "What is my name and what do I like?"}
        ]

        print("Conversation:")
        for msg in messages:
            print(f"  {msg['role'].upper()}: {msg['content']}")

        start_time = time.time()
        response = self._make_request(messages, max_tokens=100, temperature=0)

        if response:
            elapsed = time.time() - start_time
            result = response.choices[0].message.content

            print(f"\nResponse: {result}")
            print(f"Response Time: {elapsed:.2f}s")

            # Check if response contains context
            test_passed = "john" in result.lower() and "pizza" in result.lower()
            print(f"✓ PASSED - Context remembered" if test_passed else "❌ FAILED - Context lost")

            self.test_results.append({
                "test": "Conversation Context",
                "passed": test_passed,
                "response_time": elapsed,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_instruction_following(self):
        """Test 3: Following specific instructions"""
        print("\n" + "=" * 70)
        print("TEST 3: Instruction Following")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "List exactly 3 colors, separated by commas, nothing else."}
        ]

        print(f"Instruction: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=50, temperature=0)

        if response:
            result = response.choices[0].message.content.strip()

            print(f"Response: {result}")

            # Check if response follows format (3 items separated by commas)
            items = [item.strip() for item in result.split(',')]
            test_passed = len(items) == 3 and all(len(item) > 0 for item in items)

            print(f"Items found: {len(items)}")
            print(f"✓ PASSED - Followed instructions" if test_passed else "❌ FAILED - Did not follow format")

            self.test_results.append({
                "test": "Instruction Following",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_code_generation(self):
        """Test 4: Code generation capability"""
        print("\n" + "=" * 70)
        print("TEST 4: Code Generation")
        print("=" * 70)

        messages = [
            {"role": "user",
             "content": "Write a Python function to calculate factorial. Just the code, no explanation."}
        ]

        print(f"Request: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=200, temperature=0)

        if response:
            result = response.choices[0].message.content

            print(f"Generated Code:\n{result}")

            # Check if response contains Python code
            test_passed = ("def " in result or "return" in result) and "factorial" in result.lower()

            print(f"✓ PASSED - Code generated" if test_passed else "❌ FAILED - No valid code")

            self.test_results.append({
                "test": "Code Generation",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_creative_writing(self):
        """Test 5: Creative writing"""
        print("\n" + "=" * 70)
        print("TEST 5: Creative Writing")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "Write a 2-sentence story about a robot learning to paint."}
        ]

        print(f"Prompt: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=150, temperature=0.7)

        if response:
            result = response.choices[0].message.content

            print(f"Story: {result}")

            # Check if response is creative (has reasonable length)
            test_passed = len(result) > 50 and "." in result

            print(f"Story length: {len(result)} characters")
            print(f"✓ PASSED - Creative content generated" if test_passed else "❌ FAILED")

            self.test_results.append({
                "test": "Creative Writing",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_reasoning(self):
        """Test 6: Logical reasoning"""
        print("\n" + "=" * 70)
        print("TEST 6: Logical Reasoning")
        print("=" * 70)

        messages = [
            {"role": "user",
             "content": "If all cats are animals, and all animals need food, do cats need food? Answer with just 'Yes' or 'No' and a brief explanation."}
        ]

        print(f"Question: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=100, temperature=0)

        if response:
            result = response.choices[0].message.content

            print(f"Answer: {result}")

            # Check if response has correct reasoning
            test_passed = "yes" in result.lower()

            print(f"✓ PASSED - Correct reasoning" if test_passed else "❌ FAILED - Incorrect reasoning")

            self.test_results.append({
                "test": "Logical Reasoning",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_math_problem(self):
        """Test 7: Mathematical problem solving"""
        print("\n" + "=" * 70)
        print("TEST 7: Math Problem Solving")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "What is 15 * 7 + 23? Just give the number."}
        ]

        print(f"Problem: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=50, temperature=0)

        if response:
            result = response.choices[0].message.content.strip()

            print(f"Answer: {result}")

            # Correct answer is 128
            test_passed = "128" in result

            print(f"✓ PASSED - Correct answer" if test_passed else f"❌ FAILED - Wrong answer (expected 128)")

            self.test_results.append({
                "test": "Math Problem",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_multilingual(self):
        """Test 8: Multilingual capability"""
        print("\n" + "=" * 70)
        print("TEST 8: Multilingual Support")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "Translate 'Hello, how are you?' to Spanish."}
        ]

        print(f"Request: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=50, temperature=0)

        if response:
            result = response.choices[0].message.content

            print(f"Translation: {result}")

            # Check if response contains Spanish greeting
            test_passed = "hola" in result.lower() or "cómo" in result.lower()

            print(f"✓ PASSED - Translation successful" if test_passed else "❌ FAILED")

            self.test_results.append({
                "test": "Multilingual",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_json_output(self):
        """Test 9: Structured JSON output"""
        print("\n" + "=" * 70)
        print("TEST 9: Structured JSON Output")
        print("=" * 70)

        messages = [
            {"role": "user",
             "content": "Create a JSON object with name='Tesla', type='car', year=2024. Only output valid JSON."}
        ]

        print(f"Request: {messages[0]['content']}")

        response = self._make_request(messages, max_tokens=100, temperature=0)

        if response:
            result = response.choices[0].message.content.strip()

            print(f"JSON Output: {result}")

            # Try to parse as JSON
            try:
                # Remove markdown code blocks if present
                if "```" in result:
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                    result = result.strip()

                parsed = json.loads(result)
                test_passed = parsed.get("name") == "Tesla" and parsed.get("type") == "car"
                print(f"Parsed successfully: {parsed}")
                print(f"✓ PASSED - Valid JSON" if test_passed else "❌ FAILED - Incorrect data")
            except json.JSONDecodeError:
                test_passed = False
                print("❌ FAILED - Invalid JSON")

            self.test_results.append({
                "test": "JSON Output",
                "passed": test_passed,
                "response_time": 0,
                "tokens": response.usage.total_tokens
            })
            return test_passed
        return False

    def test_streaming_response(self):
        """Test 10: Streaming response"""
        print("\n" + "=" * 70)
        print("TEST 10: Streaming Response")
        print("=" * 70)

        messages = [
            {"role": "user", "content": "Count from 1 to 5."}
        ]

        print(f"Request: {messages[0]['content']}")
        print("Streaming response: ", end="", flush=True)

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                max_tokens=50
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content

            print()  # New line

            test_passed = len(full_response) > 0
            print(f"✓ PASSED - Streaming works" if test_passed else "❌ FAILED")

            self.test_results.append({
                "test": "Streaming",
                "passed": test_passed,
                "response_time": 0,
                "tokens": 0
            })
            return test_passed

        except Exception as e:
            print(f"\n❌ FAILED - Streaming error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "=" * 70)
        print(f"CHATGPT API TESTING - {self.model}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Run all tests
        tests = [
            self.test_basic_response,
            self.test_conversation_context,
            self.test_instruction_following,
            self.test_code_generation,
            self.test_creative_writing,
            self.test_reasoning,
            self.test_math_problem,
            self.test_multilingual,
            self.test_json_output,
            self.test_streaming_response
        ]

        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test failed with error: {e}")

        # Generate summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed / total * 100):.1f}%")

        print("\nDetailed Results:")
        print("-" * 70)
        for result in self.test_results:
            status = "✓ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} | {result['test']:25} | Tokens: {result.get('tokens', 'N/A')}")

        total_tokens = sum(r.get("tokens", 0) for r in self.test_results)
        print(f"\nTotal Tokens Used: {total_tokens}")
        print("=" * 70 + "\n")

        return passed, total


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("ChatGPT API Testing Tool")
    print("=" * 70)

    # Get API key
    api_key = input("\nEnter your OpenAI API key (or press Enter to use OPENAI_API_KEY env variable): ").strip()

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No API key provided!")
            print("\nOptions:")
            print("1. Set environment variable: export OPENAI_API_KEY='your-key'")
            print("2. Enter key when prompted")
            return

    # Choose model
    print("\nAvailable models:")
    print("1. gpt-3.5-turbo (Fast, Cheap)")
    print("2. gpt-4 (More capable, Expensive)")
    print("3. gpt-4-turbo (Fast GPT-4)")
    print("4. gpt-4o (Multimodal)")

    model_choice = input("\nSelect model (1-4) [default: 1]: ").strip() or "1"

    models = {
        "1": "gpt-3.5-turbo",
        "2": "gpt-4",
        "3": "gpt-4-turbo",
        "4": "gpt-4o"
    }

    model = models.get(model_choice, "gpt-3.5-turbo")
    print(f"\nUsing model: {model}")

    # Run tests
    try:
        tester = ChatGPTTester(api_key=api_key, model=model)
        tester.run_all_tests()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. API key is valid")
        print("2. You have API credits")
        print("3. Internet connection is active")


if __name__ == "__main__":
    main()