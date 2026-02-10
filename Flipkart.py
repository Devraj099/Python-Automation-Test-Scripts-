"""
Flipkart iPhone Shopping Automation (Selenium Only - No AI Required)
This script uses traditional Selenium to navigate Flipkart and add iPhone 17 Pro Max to cart
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class FlipkartBot:
    def __init__(self):
        """Initialize the bot with Selenium"""
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Initialize driver
        print("🚀 Initializing Chrome WebDriver...")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def go_to_flipkart(self):
        """Navigate to Flipkart"""
        print("\n🌐 Opening Flipkart...")
        self.driver.get("https://www.flipkart.com")
        time.sleep(3)

        # Close login popup if present
        try:
            # Try multiple selectors for the close button
            close_selectors = [
                "//button[contains(@class, '_2KpZ6l') and contains(@class, '_2doB4z')]",
                "//button[contains(text(), '✕')]",
                "//button[@class='_2KpZ6l _2doB4z']",
                "//span[@role='button' and text()='✕']"
            ]

            for selector in close_selectors:
                try:
                    close_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    close_button.click()
                    print("✅ Closed login popup")
                    time.sleep(1)
                    break
                except:
                    continue

        except Exception as e:
            print("ℹ️ No login popup found or already closed")

    def search_product(self, product_name):
        """Search for a product on Flipkart"""
        print(f"\n🔍 Searching for: {product_name}")

        try:
            # Find and use the search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys(product_name)
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN)
            print("✅ Search query submitted")
            time.sleep(4)  # Wait for results to load

        except Exception as e:
            print(f"❌ Error searching: {e}")

            # Try alternative search button method
            try:
                search_box = self.driver.find_element(By.XPATH,
                                                      "//input[@type='text' and @title='Search for Products, Brands and More']")
                search_box.clear()
                search_box.send_keys(product_name)

                search_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                search_button.click()
                print("✅ Search via button click")
                time.sleep(4)
            except Exception as e2:
                print(f"❌ Alternative search method failed: {e2}")
                raise

    def select_product(self):
        """Select the iPhone from search results"""
        print("\n📱 Looking for iPhone 17 Pro Max in search results...")

        try:
            # Wait for search results to load
            time.sleep(3)

            # Try to find product cards/links
            product_selectors = [
                "//div[contains(@class, '_1AtVbE')]//a",
                "//a[contains(@class, '_1fQZEK')]",
                "//a[contains(@class, 'IRpwTa')]",
                "//div[contains(@class, '_2kHMtA')]//a",
                "//div[@class='_1AtVbE col-12-12']//a",
                "//a[contains(@href, '/p/')]"
            ]

            product_clicked = False

            for selector in product_selectors:
                try:
                    products = self.driver.find_elements(By.XPATH, selector)
                    print(f"ℹ️ Found {len(products)} products with selector: {selector}")

                    if products:
                        # Try to find iPhone 17 Pro Max specifically
                        for product in products[:10]:  # Check first 10 products
                            try:
                                product_text = product.text.lower()
                                if 'iphone' in product_text and ('17' in product_text or 'pro' in product_text):
                                    print(f"✅ Found matching product: {product.text[:50]}...")

                                    # Store original window
                                    original_window = self.driver.current_window_handle

                                    # Click the product
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", product)
                                    time.sleep(1)
                                    self.driver.execute_script("arguments[0].click();", product)
                                    time.sleep(3)

                                    # Switch to new window if opened
                                    windows = self.driver.window_handles
                                    if len(windows) > 1:
                                        for window in windows:
                                            if window != original_window:
                                                self.driver.switch_to.window(window)
                                                print("✅ Switched to product page")
                                                break

                                    product_clicked = True
                                    break
                            except Exception as e:
                                continue

                        if product_clicked:
                            break

                        # If no specific match, click first product
                        if not product_clicked and products:
                            print("⚠️ Clicking first product as fallback...")
                            first_product = products[0]

                            original_window = self.driver.current_window_handle
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_product)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", first_product)
                            time.sleep(3)

                            windows = self.driver.window_handles
                            if len(windows) > 1:
                                for window in windows:
                                    if window != original_window:
                                        self.driver.switch_to.window(window)
                                        break

                            product_clicked = True
                            break

                except Exception as e:
                    continue

            if not product_clicked:
                raise Exception("Could not find any products to click")

            time.sleep(3)
            print("✅ Product page loaded")

        except Exception as e:
            print(f"❌ Error selecting product: {e}")
            self.driver.save_screenshot("/home/claude/select_product_error.png")
            raise

    def add_to_cart(self):
        """Add the product to cart"""
        print("\n🛒 Adding product to cart...")

        try:
            # Wait for page to load
            time.sleep(2)

            # Try multiple selectors for Add to Cart button
            cart_button_selectors = [
                "//button[contains(text(), 'Add to cart') or contains(text(), 'ADD TO CART')]",
                "//button[contains(@class, '_2KpZ6l') and contains(text(), 'Add')]",
                "//li[contains(@class, '_2KpZ6l')]//button[contains(text(), 'ADD TO CART')]",
                "//button[contains(@class, '_2KpZ6l _2U9uOA _3v1-ww')]",
            ]

            button_found = False

            for selector in cart_button_selectors:
                try:
                    add_to_cart_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )

                    if add_to_cart_button:
                        print(f"✅ Found Add to Cart button with selector: {selector}")

                        # Scroll to button
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", add_to_cart_button)
                        time.sleep(1)

                        # Try to click
                        try:
                            add_to_cart_button.click()
                        except:
                            # JavaScript click as fallback
                            self.driver.execute_script("arguments[0].click();", add_to_cart_button)

                        print("✅ Successfully clicked Add to Cart!")
                        button_found = True
                        time.sleep(3)
                        break

                except Exception as e:
                    continue

            if not button_found:
                print("⚠️ Could not find Add to Cart button, trying to locate all buttons...")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                print(f"Found {len(all_buttons)} buttons on page")

                for button in all_buttons:
                    button_text = button.text.lower()
                    if 'cart' in button_text or 'add' in button_text:
                        print(f"Found button with text: {button.text}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", button)
                        print("✅ Clicked button")
                        button_found = True
                        time.sleep(3)
                        break

            if button_found:
                # Verify cart
                try:
                    # Check if we're on cart page or see cart confirmation
                    cart_indicators = [
                        "//div[contains(text(), 'Cart')]",
                        "//span[contains(text(), 'item') and contains(text(), 'cart')]",
                        "//div[contains(@class, 'cart')]"
                    ]

                    for indicator in cart_indicators:
                        try:
                            element = self.driver.find_element(By.XPATH, indicator)
                            if element:
                                print("✅ Product successfully added to cart!")
                                break
                        except:
                            continue

                except Exception as e:
                    print("✅ Add to cart clicked (verification unavailable)")
            else:
                print("❌ Could not find or click Add to Cart button")
                self.driver.save_screenshot("/home/claude/add_to_cart_error.png")

        except Exception as e:
            print(f"❌ Error adding to cart: {e}")
            self.driver.save_screenshot("/home/claude/cart_error.png")
            raise

    def run(self):
        """Main execution flow"""
        try:
            print("=" * 70)
            print("🚀 Starting Flipkart Automation (Selenium Only)")
            print("=" * 70)

            # Step 1: Go to Flipkart
            self.go_to_flipkart()

            # Step 2: Search for iPhone 17 Pro Max
            self.search_product("iPhone 17 Pro Max")

            # Step 3: Select the product
            self.select_product()

            # Step 4: Add to cart
            self.add_to_cart()

            print("\n" + "=" * 70)
            print("✨ Automation completed!")
            print("=" * 70)
            print("\n📌 Browser will remain open for 10 seconds so you can see the result...")

            # Keep browser open for a while
            time.sleep(10)

        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            print("📸 Error screenshot saved for debugging")
            time.sleep(5)

        finally:
            print("\n🔒 Closing browser...")
            self.driver.quit()
            print("✅ Done!")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Flipkart iPhone Shopping Bot (No AI - Selenium Only)          ║
║   Simple Automation Without API Keys                            ║
╚══════════════════════════════════════════════════════════════════╝

ℹ️  This version doesn't require Claude AI or any API keys!
    It uses traditional Selenium automation to:
    1. Open Flipkart
    2. Search for iPhone 17 Pro Max
    3. Click on a product
    4. Add it to cart

    Note: Since iPhone 17 Pro Max doesn't exist yet, the script
    will search for it and click on iPhone products it finds.
    """)

    input("Press Enter to start the automation...")

    # Create and run the bot
    bot = FlipkartBot()
    bot.run()


if __name__ == "__main__":
    main()
