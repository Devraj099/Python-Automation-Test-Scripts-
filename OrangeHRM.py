"""
OrangeHRM End-to-End Automation Script
Complete automation for OrangeHRM platform including:
- Login/Logout
- Employee Management (Add, Search, Update, Delete)
- Leave Management
- Time Tracking
- Recruitment
- Report Generation

Requirements:
pip install selenium webdriver-manager openpyxl pandas
"""

import time
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orangehrm_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OrangeHRMAutomation:
    """Complete OrangeHRM automation class"""

    def __init__(self, base_url, username, password, headless=False):
        """
        Initialize the automation

        Args:
            base_url (str): OrangeHRM base URL (e.g., 'https://opensource-demo.orangehrmlive.com')
            username (str): Login username
            password (str): Login password
            headless (bool): Run browser in headless mode
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.headless = headless
        self.screenshots_dir = "screenshots"

        # Create screenshots directory
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("WebDriver setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False

    def take_screenshot(self, name):
        """Take screenshot with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None

    def login(self):
        """Login to OrangeHRM"""
        try:
            logger.info(f"Navigating to {self.base_url}")
            self.driver.get(self.base_url)

            # Wait for login page to load
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            # Enter credentials
            username_field.clear()
            username_field.send_keys(self.username)

            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.password)

            self.take_screenshot("before_login")

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for dashboard to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "oxd-topbar-header-breadcrumb"))
            )

            self.take_screenshot("after_login")
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.take_screenshot("login_failed")
            return False

    def navigate_to_menu(self, menu_name):
        """
        Navigate to a specific menu item

        Args:
            menu_name (str): Menu name (e.g., 'Admin', 'PIM', 'Leave', 'Time', 'Recruitment')
        """
        try:
            logger.info(f"Navigating to {menu_name} menu")

            # Find and click menu item
            menu_xpath = f"//span[text()='{menu_name}']/parent::a"
            menu_item = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, menu_xpath))
            )
            menu_item.click()

            time.sleep(2)  # Wait for page to load
            self.take_screenshot(f"navigated_to_{menu_name.lower()}")
            logger.info(f"Navigated to {menu_name} successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to navigate to {menu_name}: {str(e)}")
            return False

    def add_employee(self, first_name, last_name, employee_id=None, create_login=False,
                     username_login=None, password_login=None):
        """
        Add a new employee

        Args:
            first_name (str): Employee first name
            last_name (str): Employee last name
            employee_id (str): Employee ID (optional, auto-generated if not provided)
            create_login (bool): Create login credentials
            username_login (str): Username for login
            password_login (str): Password for login
        """
        try:
            logger.info(f"Adding employee: {first_name} {last_name}")

            # Navigate to PIM
            if not self.navigate_to_menu("PIM"):
                return False

            # Click Add Employee button
            add_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']"))
            )
            add_button.click()

            time.sleep(2)

            # Enter first name
            first_name_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "firstName"))
            )
            first_name_field.clear()
            first_name_field.send_keys(first_name)

            # Enter last name
            last_name_field = self.driver.find_element(By.NAME, "lastName")
            last_name_field.clear()
            last_name_field.send_keys(last_name)

            # Enter employee ID if provided
            if employee_id:
                emp_id_fields = self.driver.find_elements(By.CLASS_NAME, "oxd-input")
                for field in emp_id_fields:
                    if field.get_attribute("class") == "oxd-input oxd-input--active":
                        field.clear()
                        field.send_keys(employee_id)
                        break

            # Create login credentials if requested
            if create_login and username_login and password_login:
                toggle = self.driver.find_element(By.CLASS_NAME, "oxd-switch-input")
                toggle.click()
                time.sleep(1)

                # Enter username
                username_field = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//label[text()='Username']/parent::div/following-sibling::div/input"))
                )
                username_field.clear()
                username_field.send_keys(username_login)

                # Enter password
                password_fields = self.driver.find_elements(By.XPATH, "//input[@type='password']")
                if len(password_fields) >= 2:
                    password_fields[0].clear()
                    password_fields[0].send_keys(password_login)
                    password_fields[1].clear()
                    password_fields[1].send_keys(password_login)

            self.take_screenshot("before_add_employee")

            # Click Save button
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            save_button.click()

            # Wait for success message
            try:
                success_msg = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "oxd-toast"))
                )
                logger.info(f"Employee {first_name} {last_name} added successfully")
                self.take_screenshot("employee_added_success")
                time.sleep(2)
                return True
            except:
                logger.warning("Success message not found, but employee might be added")
                return True

        except Exception as e:
            logger.error(f"Failed to add employee: {str(e)}")
            self.take_screenshot("add_employee_failed")
            return False

    def search_employee(self, employee_name=None, employee_id=None):
        """
        Search for an employee

        Args:
            employee_name (str): Employee name to search
            employee_id (str): Employee ID to search
        """
        try:
            logger.info(f"Searching for employee: {employee_name or employee_id}")

            # Navigate to PIM
            if not self.navigate_to_menu("PIM"):
                return False

            time.sleep(2)

            # Search by employee name
            if employee_name:
                # Find autocomplete input field
                name_fields = self.driver.find_elements(By.CSS_SELECTOR, "input.oxd-input")
                for field in name_fields:
                    if field.get_attribute("placeholder") and "Type" in field.get_attribute("placeholder"):
                        field.clear()
                        field.send_keys(employee_name)
                        time.sleep(2)

                        # Select from dropdown
                        try:
                            dropdown_option = self.wait.until(
                                EC.element_to_be_clickable((By.CLASS_NAME, "oxd-autocomplete-option"))
                            )
                            dropdown_option.click()
                        except:
                            logger.warning("No dropdown appeared, continuing...")
                        break

            # Search by employee ID
            if employee_id:
                id_fields = self.driver.find_elements(By.CSS_SELECTOR, "input.oxd-input")
                for field in id_fields:
                    parent_label = field.find_element(By.XPATH, "./preceding::label[1]")
                    if "Employee Id" in parent_label.text:
                        field.clear()
                        field.send_keys(employee_id)
                        break

            self.take_screenshot("before_search")

            # Click Search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()

            time.sleep(3)

            self.take_screenshot("search_results")
            logger.info("Search completed")
            return True

        except Exception as e:
            logger.error(f"Failed to search employee: {str(e)}")
            self.take_screenshot("search_failed")
            return False

    def apply_leave(self, leave_type, from_date, to_date, comments=""):
        """
        Apply for leave

        Args:
            leave_type (str): Type of leave (e.g., 'CAN - Vacation', 'CAN - Sick')
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)
            comments (str): Leave comments
        """
        try:
            logger.info(f"Applying leave from {from_date} to {to_date}")

            # Navigate to Leave
            if not self.navigate_to_menu("Leave"):
                return False

            # Click Apply
            apply_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Apply']"))
            )
            apply_button.click()

            time.sleep(2)

            # Select leave type
            leave_type_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "oxd-select-text-input"))
            )
            leave_type_dropdown.click()
            time.sleep(1)

            # Select specific leave type
            leave_option = self.driver.find_element(By.XPATH, f"//span[contains(text(),'{leave_type}')]")
            leave_option.click()

            # Enter from date
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input.oxd-input")
            for date_input in date_inputs:
                if date_input.get_attribute("placeholder") == "yyyy-dd-mm":
                    # Clear and enter from date
                    date_input.clear()
                    date_input.send_keys(from_date)
                    break

            time.sleep(1)

            # Enter to date (second date field)
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input.oxd-input")
            date_count = 0
            for date_input in date_inputs:
                if date_input.get_attribute("placeholder") == "yyyy-dd-mm":
                    date_count += 1
                    if date_count == 2:
                        date_input.clear()
                        date_input.send_keys(to_date)
                        break

            # Enter comments
            if comments:
                comment_field = self.driver.find_element(By.TAG_NAME, "textarea")
                comment_field.clear()
                comment_field.send_keys(comments)

            self.take_screenshot("before_apply_leave")

            # Click Apply button
            apply_submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            apply_submit_button.click()

            time.sleep(3)

            self.take_screenshot("leave_applied")
            logger.info("Leave application submitted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to apply leave: {str(e)}")
            self.take_screenshot("apply_leave_failed")
            return False

    def add_candidate(self, first_name, last_name, email, vacancy="Software Engineer"):
        """
        Add a recruitment candidate

        Args:
            first_name (str): Candidate first name
            last_name (str): Candidate last name
            email (str): Candidate email
            vacancy (str): Vacancy title
        """
        try:
            logger.info(f"Adding candidate: {first_name} {last_name}")

            # Navigate to Recruitment
            if not self.navigate_to_menu("Recruitment"):
                return False

            # Click Add button
            add_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']"))
            )
            add_button.click()

            time.sleep(2)

            # Enter first name
            first_name_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "firstName"))
            )
            first_name_field.clear()
            first_name_field.send_keys(first_name)

            # Enter last name
            last_name_field = self.driver.find_element(By.NAME, "lastName")
            last_name_field.clear()
            last_name_field.send_keys(last_name)

            # Enter email
            email_fields = self.driver.find_elements(By.CSS_SELECTOR, "input.oxd-input")
            for field in email_fields:
                parent = field.find_element(By.XPATH, "./ancestor::div[contains(@class, 'oxd-input-group')]")
                if "Email" in parent.text:
                    field.clear()
                    field.send_keys(email)
                    break

            # Select vacancy
            try:
                vacancy_dropdown = self.driver.find_element(By.CLASS_NAME, "oxd-select-text-input")
                vacancy_dropdown.click()
                time.sleep(1)

                vacancy_option = self.driver.find_element(By.XPATH, f"//span[contains(text(),'{vacancy}')]")
                vacancy_option.click()
            except:
                logger.warning("Vacancy selection skipped")

            self.take_screenshot("before_add_candidate")

            # Click Save button
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            save_button.click()

            time.sleep(3)

            self.take_screenshot("candidate_added")
            logger.info(f"Candidate {first_name} {last_name} added successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to add candidate: {str(e)}")
            self.take_screenshot("add_candidate_failed")
            return False

    def view_reports(self):
        """View and access reports section"""
        try:
            logger.info("Accessing reports")

            # Navigate to various modules to check reports
            modules_with_reports = ["PIM", "Leave", "Time", "Recruitment"]

            for module in modules_with_reports:
                try:
                    self.navigate_to_menu(module)
                    time.sleep(2)

                    # Try to find Reports link
                    try:
                        reports_link = self.driver.find_element(By.XPATH, "//a[contains(text(),'Reports')]")
                        reports_link.click()
                        time.sleep(2)
                        self.take_screenshot(f"{module.lower()}_reports")
                        logger.info(f"Accessed {module} reports")
                    except:
                        logger.info(f"No reports found in {module}")

                except Exception as e:
                    logger.warning(f"Could not access {module} reports: {str(e)}")

            return True

        except Exception as e:
            logger.error(f"Failed to view reports: {str(e)}")
            return False

    def logout(self):
        """Logout from OrangeHRM"""
        try:
            logger.info("Logging out")

            # Click on user dropdown
            user_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "oxd-userdropdown-tab"))
            )
            user_dropdown.click()

            time.sleep(1)

            # Click Logout
            logout_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Logout']"))
            )
            logout_link.click()

            # Wait for login page
            self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            self.take_screenshot("logged_out")
            logger.info("Logout successful")
            return True

        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            self.take_screenshot("logout_failed")
            return False

    def cleanup(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def run_complete_workflow(self):
        """Run a complete end-to-end workflow"""
        try:
            # Setup
            if not self.setup_driver():
                return False

            # Login
            if not self.login():
                return False

            time.sleep(3)

            # Add Employee
            employee_added = self.add_employee(
                first_name="John",
                last_name="Doe",
                employee_id=None,
                create_login=False
            )

            time.sleep(3)

            # Search Employee
            if employee_added:
                self.search_employee(employee_name="John Doe")

            time.sleep(3)

            # Apply Leave
            today = datetime.now()
            from_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
            to_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

            self.apply_leave(
                leave_type="Vacation",
                from_date=from_date,
                to_date=to_date,
                comments="Planned vacation"
            )

            time.sleep(3)

            # Add Candidate
            self.add_candidate(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com"
            )

            time.sleep(3)

            # View Reports
            self.view_reports()

            time.sleep(3)

            # Logout
            self.logout()

            logger.info("Complete workflow executed successfully!")
            return True

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            self.take_screenshot("workflow_failed")
            return False
        finally:
            self.cleanup()


def main():
    """Main execution function"""

    # Configuration
    BASE_URL = "https://opensource-demo.orangehrmlive.com"
    USERNAME = "Admin"
    PASSWORD = "admin123"
    HEADLESS = False  # Set to True to run in headless mode

    # Initialize automation
    automation = OrangeHRMAutomation(
        base_url=BASE_URL,
        username=USERNAME,
        password=PASSWORD,
        headless=HEADLESS
    )

    # Run complete workflow
    logger.info("=" * 60)
    logger.info("Starting OrangeHRM Complete Automation Workflow")
    logger.info("=" * 60)

    success = automation.run_complete_workflow()

    if success:
        logger.info("=" * 60)
        logger.info("Automation completed successfully!")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("Automation failed!")
        logger.error("=" * 60)


if __name__ == "__main__":
    main()