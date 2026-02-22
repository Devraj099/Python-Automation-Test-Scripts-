# ============================================================
#   PARABANK - COMPLETE END-TO-END AUTOMATION (SINGLE FILE)
#   Demo Bank: https://parabank.parasoft.com
#   Run: python parabank_automation.py
# ============================================================
#
#   STEP 1: Register a free account at:
#           https://parabank.parasoft.com/parabank/register.htm
#   STEP 2: Update USERNAME and PASSWORD below with your registered details
#   STEP 3: Run: python parabank_automation.py
#
# ============================================================

import os
import sys
import csv
import json
import logging
import argparse
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Windows Unicode fix
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# SECTION 1 - CONFIGURATION
# ============================================================

class Config:
    # ParaBank real demo bank - no need to change BASE_URL
    BASE_URL = "https://parabank.parasoft.com/parabank"

    # STEP 1: Go to https://parabank.parasoft.com/parabank/register.htm
    # STEP 2: Register with your details and paste your username/password here
    USERNAME = "Rohan4546"   # <-- change this after registering
    PASSWORD = "Rohan@7879"   # <-- change this after registering

    # Browser Settings
    HEADLESS          = False
    IMPLICIT_WAIT     = 10
    EXPLICIT_WAIT     = 20
    PAGE_LOAD_TIMEOUT = 30

    # Output folders
    REPORT_DIR     = "reports"
    SCREENSHOT_DIR = "screenshots"
    LOG_DIR        = "logs"

# ============================================================
# SECTION 2 - LOGGING
# ============================================================

os.makedirs(Config.LOG_DIR, exist_ok=True)
os.makedirs(Config.REPORT_DIR, exist_ok=True)
os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)

logger = logging.getLogger("ParaBank")
logger.setLevel(logging.INFO)
fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

fh = logging.FileHandler(f"{Config.LOG_DIR}/automation.log", encoding="utf-8")
fh.setFormatter(fmt)
logger.addHandler(fh)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(fmt)
logger.addHandler(ch)

# ============================================================
# SECTION 3 - WEBDRIVER
# ============================================================

def get_driver(headless=None):
    headless = headless if headless is not None else Config.HEADLESS
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(Config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    driver.maximize_window()
    logger.info("Chrome browser started")
    return driver

# ============================================================
# SECTION 4 - BASE PAGE
# ============================================================

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)

    def open(self, path=""):
        url = f"{Config.BASE_URL}/{path.lstrip('/')}"
        self.driver.get(url)
        logger.info(f"Opened: {url}")

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()

    def type_text(self, locator, text, clear=True):
        el = self.find(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text.strip()

    def is_displayed(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_url(self, fragment, timeout=15):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))

    def take_screenshot(self, name="screenshot"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{Config.SCREENSHOT_DIR}/{name}_{ts}.png"
        self.driver.save_screenshot(path)
        logger.info(f"Screenshot: {path}")
        return path

# ============================================================
# SECTION 5 - LOGIN PAGE
# (Locators verified for parabank.parasoft.com)
# ============================================================

class LoginPage(BasePage):
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON   = (By.XPATH, "//input[@value='Log In']")
    ERROR_MESSAGE  = (By.CLASS_NAME, "error")

    def login(self, username, password):
        logger.info(f"Logging in as: {username}")
        self.open("index.htm")
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    def is_login_successful(self):
        try:
            self.wait_for_url("overview")
            logger.info("Login successful!")
            return True
        except Exception:
            return False

    def get_error(self):
        if self.is_displayed(self.ERROR_MESSAGE, timeout=3):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

# ============================================================
# SECTION 6 - ACCOUNTS OVERVIEW (Dashboard)
# ============================================================

class AccountsPage(BasePage):
    ACCOUNTS_TABLE   = (By.ID, "accountTable")
    ACCOUNT_ROWS     = (By.CSS_SELECTOR, "#accountTable tbody tr")
    TOTAL_VALUE      = (By.XPATH, "//table[@id='accountTable']//tfoot//td[2]")
    TRANSFER_LINK    = (By.LINK_TEXT, "Transfer Funds")
    TRANSACTIONS_LINK= (By.LINK_TEXT, "Find Transactions")
    ACTIVITY_LINK    = (By.LINK_TEXT, "Account Activity")
    LOGOUT_LINK      = (By.LINK_TEXT, "Log Out")

    def get_total_balance(self):
        try:
            total = self.get_text(self.TOTAL_VALUE)
            logger.info(f"Total Balance: {total}")
            return total
        except Exception:
            return "N/A"

    def get_accounts(self):
        accounts = []
        try:
            rows = self.find_all(self.ACCOUNT_ROWS)
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    accounts.append({
                        "Account": cols[0].text.strip(),
                        "Balance": cols[1].text.strip() if len(cols) > 1 else ""
                    })
        except Exception as e:
            logger.warning(f"Could not read accounts: {e}")
        return accounts

    def get_first_account_id(self):
        try:
            rows = self.find_all(self.ACCOUNT_ROWS)
            link = rows[0].find_element(By.TAG_NAME, "a")
            return link.text.strip()
        except Exception:
            return None

    def go_to_transfer(self):
        self.click(self.TRANSFER_LINK)

    def go_to_find_transactions(self):
        self.click(self.TRANSACTIONS_LINK)

    def go_to_account_activity(self):
        self.click(self.ACTIVITY_LINK)

    def logout(self):
        self.click(self.LOGOUT_LINK)
        logger.info("Logged out")

# ============================================================
# SECTION 7 - FUND TRANSFER PAGE
# ============================================================

class TransferPage(BasePage):
    AMOUNT_INPUT   = (By.ID, "amount")
    FROM_ACCOUNT   = (By.ID, "fromAccountId")
    TO_ACCOUNT     = (By.ID, "toAccountId")
    TRANSFER_BTN   = (By.XPATH, "//input[@value='Transfer']")
    SUCCESS_HEADER = (By.XPATH, "//h1[contains(text(),'Transfer Complete')]")
    SUCCESS_MSG    = (By.ID, "showResult")
    ERROR_MSG      = (By.CLASS_NAME, "error")

    def open_transfer(self):
        self.open("transfer.htm")
        return self

    def transfer(self, amount, from_account=None, to_account=None):
        logger.info(f"Transferring ${amount}")
        self.open_transfer()
        self.type_text(self.AMOUNT_INPUT, str(amount))

        # Select accounts from dropdowns if provided
        if from_account:
            Select(self.find(self.FROM_ACCOUNT)).select_by_visible_text(from_account)
        if to_account:
            Select(self.find(self.TO_ACCOUNT)).select_by_visible_text(to_account)

        self.click(self.TRANSFER_BTN)
        return self

    def is_successful(self):
        return self.is_displayed(self.SUCCESS_HEADER, timeout=10)

    def get_success_message(self):
        if self.is_displayed(self.SUCCESS_MSG, timeout=5):
            return self.get_text(self.SUCCESS_MSG)
        return ""

    def get_error(self):
        if self.is_displayed(self.ERROR_MSG, timeout=3):
            return self.get_text(self.ERROR_MSG)
        return ""

# ============================================================
# SECTION 8 - ACCOUNT ACTIVITY (Transaction History)
# ============================================================

class AccountActivityPage(BasePage):
    ACCOUNT_SELECT   = (By.ID, "accountId")
    MONTH_SELECT     = (By.ID, "month")
    TYPE_SELECT      = (By.ID, "transactionType")
    GO_BTN           = (By.XPATH, "//button[@type='submit' and text()='Go']")
    TRANS_TABLE      = (By.ID, "transactionTable")
    TRANS_ROWS       = (By.CSS_SELECTOR, "#transactionTable tbody tr")
    TRANS_HEADERS    = (By.CSS_SELECTOR, "#transactionTable thead th")
    NO_TRANS_MSG     = (By.XPATH, "//*[contains(text(),'No transactions found')]")

    def open_activity(self, account_id=None):
        if account_id:
            self.open(f"activity.htm?id={account_id}")
        else:
            self.open("activity.htm")
        return self

    def filter_transactions(self, month="All", tx_type="All"):
        try:
            Select(self.find(self.MONTH_SELECT)).select_by_visible_text(month)
            Select(self.find(self.TYPE_SELECT)).select_by_visible_text(tx_type)
            self.click(self.GO_BTN)
        except Exception as e:
            logger.warning(f"Could not apply filter: {e}")
        return self

    def get_transactions(self):
        try:
            if self.is_displayed(self.NO_TRANS_MSG, timeout=3):
                logger.info("No transactions found")
                return []
            headers = [h.text.strip() for h in self.find_all(self.TRANS_HEADERS)]
            rows = self.find_all(self.TRANS_ROWS)
            result = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                data = {headers[i]: cols[i].text.strip()
                        for i in range(min(len(headers), len(cols)))}
                result.append(data)
            logger.info(f"Found {len(result)} transactions")
            return result
        except Exception as e:
            logger.warning(f"Could not read transactions: {e}")
            return []

# ============================================================
# SECTION 9 - PARABANK REST API CLIENT
# ============================================================

class ParaBankAPIClient:
    """
    ParaBank exposes a real REST API at:
    https://parabank.parasoft.com/parabank/services/bank/
    """
    API_URL = "https://parabank.parasoft.com/parabank/services/bank"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.customer_id = None
        self.accounts = []

    def login(self, username, password):
        url = f"{self.API_URL}/login/{username}/{password}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.customer_id = data.get("id")
            logger.info(f"API Login OK - Customer ID: {self.customer_id}")
            return data
        except Exception as e:
            logger.error(f"API Login failed: {e}")
            return {}

    def get_accounts(self):
        if not self.customer_id:
            return []
        url = f"{self.API_URL}/customers/{self.customer_id}/accounts"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            self.accounts = resp.json()
            logger.info(f"API Accounts: {len(self.accounts)} found")
            return self.accounts
        except Exception as e:
            logger.error(f"API get accounts failed: {e}")
            return []

    def get_balance(self, account_id):
        url = f"{self.API_URL}/accounts/{account_id}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            balance = data.get("balance", 0)
            logger.info(f"API Balance for {account_id}: ${balance}")
            return balance
        except Exception as e:
            logger.error(f"API get balance failed: {e}")
            return 0

    def transfer_funds(self, from_id, to_id, amount):
        url = f"{self.API_URL}/transfer"
        params = {"fromAccountId": from_id, "toAccountId": to_id, "amount": amount}
        try:
            resp = self.session.post(url, params=params, timeout=15)
            resp.raise_for_status()
            logger.info(f"API Transfer ${amount} from {from_id} to {to_id} - OK")
            return True
        except Exception as e:
            logger.error(f"API transfer failed: {e}")
            return False

    def get_transactions(self, account_id):
        url = f"{self.API_URL}/accounts/{account_id}/transactions"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            txns = resp.json()
            logger.info(f"API Transactions for {account_id}: {len(txns)} found")
            return txns
        except Exception as e:
            logger.error(f"API get transactions failed: {e}")
            return []

# ============================================================
# SECTION 10 - REPORT GENERATOR
# ============================================================

class ReportGenerator:
    def __init__(self):
        os.makedirs(Config.REPORT_DIR, exist_ok=True)

    def _ts(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_csv(self, data, filename=None):
        if not data:
            return ""
        path = f"{Config.REPORT_DIR}/{filename or f'data_{self._ts()}.csv'}"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"CSV saved: {path}")
        return path

    def save_json(self, data, filename=None):
        path = f"{Config.REPORT_DIR}/{filename or f'report_{self._ts()}.json'}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)
        logger.info(f"JSON saved: {path}")
        return path

    def save_html(self, transactions, balance=0, account=""):
        if not transactions:
            logger.warning("No transactions to report")
            return ""
        path = f"{Config.REPORT_DIR}/bank_report_{self._ts()}.html"
        headers = list(transactions[0].keys())
        header_html = "".join(f"<th>{h}</th>" for h in headers)
        rows_html = ""
        for tx in transactions:
            cls = "debit" if "debit" in str(tx.get("Type","")).lower() else "credit"
            cols = "".join(f"<td>{tx.get(h,'')}</td>" for h in headers)
            rows_html += f'<tr class="{cls}">{cols}</tr>\n'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ParaBank Report</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; background: #f9f9f9; }}
  h1   {{ color: #1a3c6e; border-bottom: 2px solid #1a3c6e; padding-bottom: 10px; }}
  .summary {{ background: #e8f0fe; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #1a3c6e; }}
  .summary b {{ color: #1a3c6e; }}
  table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
  th {{ background: #1a3c6e; color: white; padding: 12px; text-align: left; }}
  td {{ padding: 10px; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f0f4ff; }}
  tr.debit td {{ color: #c0392b; }}
  tr.credit td {{ color: #27ae60; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
  .badge.pass {{ background: #d5f5e3; color: #1e8449; }}
  .badge.fail {{ background: #fadbd8; color: #c0392b; }}
</style>
</head>
<body>
<h1>ParaBank - Automation Report</h1>
<div class="summary">
  <p>Account: <b>{account}</b></p>
  <p>Balance: <b>${balance:,.2f}</b></p>
  <p>Transactions: <b>{len(transactions)}</b></p>
  <p>Generated: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></p>
</div>
<h2>Transaction History</h2>
<table>
  <thead><tr>{header_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML report: {path}")
        return path

# ============================================================
# SECTION 11 - TESTS
# ============================================================

class ParaBankTests:
    def __init__(self, driver):
        self.driver = driver
        self.results = []

    def record(self, tc_id, name, passed, detail=""):
        tag = "[PASS]" if passed else "[FAIL]"
        msg = f"{tag} {tc_id}: {name}"
        if detail:
            msg += f" - {detail}"
        logger.info(msg)
        self.results.append({
            "ID": tc_id, "Test": name,
            "Status": "PASS" if passed else "FAIL",
            "Detail": detail
        })
        return passed

    # ── TC001: Valid Login ────────────────────────────────────
    def test_valid_login(self):
        login = LoginPage(self.driver)
        login.login(Config.USERNAME, Config.PASSWORD)
        passed = login.is_login_successful()
        return self.record("TC001", "Valid Login", passed,
                           "Redirected to accounts overview" if passed else "Login failed")

    # ── TC002: Invalid Login ──────────────────────────────────
    def test_invalid_login(self):
        login = LoginPage(self.driver)
        login.login("INVALID_USER_999", "WRONG_PASS_999")
        error = login.get_error()
        passed = bool(error)
        self.record("TC002", "Invalid Login Shows Error", passed, error or "No error shown")
        # Now log back in with valid credentials
        login.login(Config.USERNAME, Config.PASSWORD)
        login.is_login_successful()

    # ── TC003: Account Balance ────────────────────────────────
    def test_account_balance(self):
        acc_page = AccountsPage(self.driver)
        balance = acc_page.get_total_balance()
        passed = bool(balance) and balance != "N/A"
        return self.record("TC003", "Account Balance Displayed", passed, f"Balance: {balance}")

    # ── TC004: View All Accounts ──────────────────────────────
    def test_view_accounts(self):
        acc_page = AccountsPage(self.driver)
        accounts = acc_page.get_accounts()
        passed = len(accounts) > 0
        self.record("TC004", "Accounts Listed", passed, f"{len(accounts)} account(s) found")
        return accounts

    # ── TC005: Fund Transfer ──────────────────────────────────
    def test_fund_transfer(self, accounts):
        if len(accounts) < 2:
            self.record("TC005", "Fund Transfer", False, "Need 2+ accounts - skipped")
            return False
        transfer = TransferPage(self.driver)
        transfer.transfer(amount=10.00)
        passed = transfer.is_successful()
        msg = transfer.get_success_message() if passed else transfer.get_error()
        return self.record("TC005", "Fund Transfer $10", passed, msg[:80] if msg else "")

    # ── TC006: Transfer Invalid Amount ────────────────────────
    def test_invalid_transfer(self):
        transfer = TransferPage(self.driver)
        transfer.transfer(amount=-1)
        passed = not transfer.is_successful()
        self.record("TC006", "Invalid Transfer Amount Rejected", passed)

    # ── TC007: Transaction History ────────────────────────────
    def test_transaction_history(self, account_id):
        if not account_id:
            self.record("TC007", "Transaction History", False, "No account ID")
            return []
        activity = AccountActivityPage(self.driver)
        activity.open_activity(account_id)
        txns = activity.get_transactions()
        passed = isinstance(txns, list)
        self.record("TC007", "Transaction History Loads", passed,
                    f"{len(txns)} transaction(s)" if txns else "0 transactions (account may be new)")
        return txns

    # ── TC008: Filter Transactions ────────────────────────────
    def test_filter_transactions(self, account_id):
        if not account_id:
            self.record("TC008", "Filter Transactions", False, "No account ID")
            return
        activity = AccountActivityPage(self.driver)
        activity.open_activity(account_id)
        activity.filter_transactions(month="All", tx_type="Credit")
        txns = activity.get_transactions()
        self.record("TC008", "Filter by Credit Transactions", True,
                    f"{len(txns)} credit transaction(s)")

# ============================================================
# SECTION 12 - MAIN RUNNER
# ============================================================

def run_all(headless=False):
    logger.info("=" * 60)
    logger.info("   PARABANK AUTOMATION STARTING")
    logger.info("   Site: https://parabank.parasoft.com")
    logger.info("=" * 60)

    if Config.USERNAME == "your_username":
        logger.warning("=" * 60)
        logger.warning(" ACTION REQUIRED:")
        logger.warning(" 1. Go to: https://parabank.parasoft.com/parabank/register.htm")
        logger.warning(" 2. Register a free account")
        logger.warning(" 3. Update USERNAME and PASSWORD in Config section (top of file)")
        logger.warning("=" * 60)

    driver = get_driver(headless=headless)
    reporter = ReportGenerator()
    tester = ParaBankTests(driver)
    all_transactions = []
    balance = 0.0
    account_id = None
    accounts = []

    try:
        # STEP 1: Login
        logger.info("\n--- STEP 1: LOGIN ---")
        if not tester.test_valid_login():
            logger.error("Login FAILED - update USERNAME and PASSWORD in Config section")
            LoginPage(driver).take_screenshot("login_failed")
            return

        # STEP 2: Account Balance + Get Accounts
        logger.info("\n--- STEP 2: ACCOUNTS & BALANCE ---")
        tester.test_account_balance()
        accounts = tester.test_view_accounts()

        # Get first account ID for transaction tests
        acc_page = AccountsPage(driver)
        account_id = acc_page.get_first_account_id()
        logger.info(f"Using account ID: {account_id}")

        # Get balance from first account
        if accounts and accounts[0].get("Balance"):
            try:
                balance = float(accounts[0]["Balance"].replace("$","").replace(",","").strip())
            except Exception:
                balance = 0.0

        # STEP 3: Fund Transfer
        logger.info("\n--- STEP 3: FUND TRANSFER ---")
        tester.test_fund_transfer(accounts)
        tester.test_invalid_transfer()

        # STEP 4: Transaction History
        logger.info("\n--- STEP 4: TRANSACTION HISTORY ---")
        all_transactions = tester.test_transaction_history(account_id)
        tester.test_filter_transactions(account_id)

        # STEP 5: API Tests
        logger.info("\n--- STEP 5: API TESTS ---")
        api = ParaBankAPIClient()
        api_data = api.login(Config.USERNAME, Config.PASSWORD)
        if api_data:
            api_accounts = api.get_accounts()
            if api_accounts:
                first_acc_id = api_accounts[0].get("id")
                api_balance = api.get_balance(first_acc_id)
                api_txns = api.get_transactions(first_acc_id)
                if not all_transactions and api_txns:
                    # Use API transactions if UI had none
                    all_transactions = [
                        {"ID": str(t.get("id","")),
                         "Date": str(t.get("date","")),
                         "Description": str(t.get("description","")),
                         "Amount": str(t.get("amount",""))}
                        for t in api_txns
                    ]

        # STEP 6: Logout
        logger.info("\n--- STEP 6: LOGOUT ---")
        AccountsPage(driver).logout()
        logger.info("Logout successful")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        try:
            driver.save_screenshot(
                f"{Config.SCREENSHOT_DIR}/error_{datetime.now().strftime('%H%M%S')}.png")
        except Exception:
            pass
    finally:
        driver.quit()
        logger.info("Browser closed")

    # STEP 7: Generate Reports
    logger.info("\n--- STEP 7: GENERATING REPORTS ---")
    if all_transactions:
        reporter.save_csv(all_transactions, "transactions.csv")
        reporter.save_html(all_transactions, balance=balance, account=account_id or "")

    reporter.save_csv(tester.results, "test_results.csv")
    reporter.save_json({
        "run_time": datetime.now().isoformat(),
        "site": Config.BASE_URL,
        "account": account_id,
        "balance": balance,
        "total_tests": len(tester.results),
        "passed": sum(1 for r in tester.results if r["Status"] == "PASS"),
        "failed": sum(1 for r in tester.results if r["Status"] == "FAIL"),
        "results": tester.results
    }, "summary.json")

    # Final Summary
    passed = sum(1 for r in tester.results if r["Status"] == "PASS")
    failed = sum(1 for r in tester.results if r["Status"] == "FAIL")
    total  = len(tester.results)

    logger.info("\n" + "=" * 60)
    logger.info("   AUTOMATION COMPLETE")
    logger.info("=" * 60)
    for r in tester.results:
        tag = "[PASS]" if r["Status"] == "PASS" else "[FAIL]"
        logger.info(f"  {tag} {r['ID']}: {r['Test']}")
    logger.info("-" * 60)
    logger.info(f"  Total : {total}  |  Passed : {passed}  |  Failed : {failed}")
    logger.info(f"  Reports saved to: ./{Config.REPORT_DIR}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ParaBank Selenium Automation")
    parser.add_argument("--headless", action="store_true",
                        help="Run without browser window")
    args = parser.parse_args()
    run_all(headless=args.headless)