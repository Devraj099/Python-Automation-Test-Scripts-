import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import openai


class AIBrowserTester:
    def __init__(self, openai_api_key):
        """Initialize the AI Browser Tester with OpenAI API key"""
        self.api_key = openai_api_key
        openai.api_key = self.api_key
        self.driver = None
        self.test_results = []

    def setup_browser(self, headless=False):
        """Setup Chrome browser with options"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        print("✓ Browser initialized successfully")

    def ask_chatgpt(self, prompt, model="gpt-4"):
        """Send a prompt to ChatGPT and get response"""
        try:
            from openai import OpenAI  # ✅ NEW WAY
            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert QA automation engineer helping with web testing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"✗ Error communicating with ChatGPT: {e}")
            return None

    def generate_test_cases(self, website_description):
        """Use ChatGPT to generate test cases for a website"""
        prompt = f"""
        Generate 5 critical test cases for the following website:
        {website_description}

        Return the test cases in JSON format with the following structure:
        {{
            "test_cases": [
                {{
                    "name": "test case name",
                    "description": "what to test",
                    "steps": ["step 1", "step 2"],
                    "expected_result": "what should happen"
                }}
            ]
        }}
        """

        response = self.ask_chatgpt(prompt)
        if response:
            try:
                # Extract JSON from response
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
            except:
                print("✗ Could not parse test cases from ChatGPT response")
                return None
        return None

    def analyze_page_elements(self):
        """Get current page elements and ask ChatGPT for testing recommendations"""
        try:
            # Get page title and URL
            page_title = self.driver.title
            page_url = self.driver.current_url

            # Get all interactive elements
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")

            element_summary = f"""
            Page: {page_title}
            URL: {page_url}
            Buttons found: {len(buttons)}
            Links found: {len(links)}
            Input fields found: {len(inputs)}
            """

            prompt = f"""
            I'm on a webpage with these elements:
            {element_summary}

            What are the top 3 most important things I should test on this page?
            Provide specific, actionable test scenarios.
            """

            recommendations = self.ask_chatgpt(prompt)
            return recommendations

        except Exception as e:
            print(f"✗ Error analyzing page: {e}")
            return None

    def execute_test_with_ai_verification(self, test_name, actions):
        """Execute a test and use AI to verify the results"""
        print(f"\n{'=' * 60}")
        print(f"Executing Test: {test_name}")
        print(f"{'=' * 60}")

        test_result = {
            "name": test_name,
            "status": "PASS",
            "steps": [],
            "ai_analysis": ""
        }

        try:
            for action in actions:
                step_result = self._execute_action(action)
                test_result["steps"].append(step_result)

            # Take screenshot for AI analysis
            screenshot_path = f"/home/claude/screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)

            # Get page state for AI verification
            page_state = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "visible_text": self.driver.find_element(By.TAG_NAME, "body").text[:500]
            }

            # Ask AI to verify the test result
            verification_prompt = f"""
            Test Name: {test_name}
            Final Page State:
            - URL: {page_state['url']}
            - Title: {page_state['title']}
            - Visible Text: {page_state['visible_text']}

            Based on this information, does the test appear to have executed successfully?
            Provide a brief analysis (2-3 sentences).
            """

            ai_analysis = self.ask_chatgpt(verification_prompt)
            test_result["ai_analysis"] = ai_analysis

            print(f"\n🤖 AI Analysis: {ai_analysis}")

        except Exception as e:
            test_result["status"] = "FAIL"
            test_result["error"] = str(e)
            print(f"✗ Test failed: {e}")

        self.test_results.append(test_result)
        return test_result

    def _execute_action(self, action):
        """Execute a single test action"""
        action_type = action.get("type")
        print(f"\n→ Executing: {action_type}")

        try:
            if action_type == "navigate":
                url = action.get("url")
                self.driver.get(url)
                print(f"  Navigated to: {url}")
                return {"action": action_type, "status": "success", "url": url}

            elif action_type == "click":
                locator = action.get("locator")
                element = self._find_element(locator)
                element.click()
                time.sleep(1)
                print(f"  Clicked element: {locator}")
                return {"action": action_type, "status": "success", "locator": locator}

            elif action_type == "input":
                locator = action.get("locator")
                text = action.get("text")
                element = self._find_element(locator)
                element.clear()
                element.send_keys(text)
                print(f"  Entered text into: {locator}")
                return {"action": action_type, "status": "success", "locator": locator, "text": text}

            elif action_type == "wait":
                seconds = action.get("seconds", 2)
                time.sleep(seconds)
                print(f"  Waited {seconds} seconds")
                return {"action": action_type, "status": "success", "seconds": seconds}

            elif action_type == "verify_text":
                text = action.get("text")
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if text in body_text:
                    print(f"  ✓ Verified text present: {text}")
                    return {"action": action_type, "status": "success", "text": text}
                else:
                    print(f"  ✗ Text not found: {text}")
                    return {"action": action_type, "status": "fail", "text": text}

        except Exception as e:
            print(f"  ✗ Action failed: {e}")
            return {"action": action_type, "status": "error", "error": str(e)}

    def _find_element(self, locator):
        """Find element using various strategies"""
        by_type = locator.get("by", "css")
        value = locator.get("value")

        locator_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }

        by = locator_map.get(by_type, By.CSS_SELECTOR)
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        )

    def generate_bug_report(self, error_description):
        """Use ChatGPT to generate a detailed bug report"""
        prompt = f"""
        Generate a professional bug report for the following issue:
        {error_description}

        Include:
        - Summary
        - Steps to Reproduce
        - Expected Result
        - Actual Result
        - Severity
        - Additional Notes
        """

        bug_report = self.ask_chatgpt(prompt)
        return bug_report

    def generate_test_summary(self):
        """Generate a comprehensive test summary using AI"""
        summary_data = {
            "total_tests": len(self.test_results),
            "passed": sum(1 for t in self.test_results if t["status"] == "PASS"),
            "failed": sum(1 for t in self.test_results if t["status"] == "FAIL"),
            "test_names": [t["name"] for t in self.test_results]
        }

        prompt = f"""
        Generate a professional test execution summary report:

        Total Tests: {summary_data['total_tests']}
        Passed: {summary_data['passed']}
        Failed: {summary_data['failed']}
        Tests Executed: {', '.join(summary_data['test_names'])}

        Provide insights, recommendations, and next steps.
        """

        summary = self.ask_chatgpt(prompt)
        print(f"\n{'=' * 60}")
        print("TEST SUMMARY REPORT")
        print(f"{'=' * 60}")
        print(summary)
        return summary

    def cleanup(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            print("\n✓ Browser closed successfully")


# Example usage
def main():
    # Set your OpenAI API key
    API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    # Initialize the AI tester
    tester = AIBrowserTester(API_KEY)

    try:
        # Setup browser
        tester.setup_browser(headless=False)

        # Example 1: Generate test cases for a website
        print("\n" + "=" * 60)
        print("GENERATING TEST CASES WITH AI")
        print("=" * 60)

        test_cases = tester.generate_test_cases(
            "An e-commerce website selling electronics with product search, cart, and checkout"
        )

        if test_cases:
            print("\n🤖 AI Generated Test Cases:")
            print(json.dumps(test_cases, indent=2))

        # Example 2: Navigate and analyze a page
        print("\n" + "=" * 60)
        print("ANALYZING PAGE WITH AI")
        print("=" * 60)

        tester.driver.get("https://www.example.com")
        recommendations = tester.analyze_page_elements()
        print(f"\n🤖 AI Recommendations:\n{recommendations}")

        # Example 3: Execute a test with AI verification
        test_actions = [
            {"type": "navigate", "url": "https://www.example.com"},
            {"type": "wait", "seconds": 2},
            {"type": "verify_text", "text": "Example Domain"}
        ]

        tester.execute_test_with_ai_verification("Homepage Load Test", test_actions)

        # Generate final summary
        tester.generate_test_summary()

    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()