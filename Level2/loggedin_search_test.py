import csv
import os
import time
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

DATA_FILE = os.path.join(os.path.dirname(__file__), "loggedin_search_data.csv")


def page_text(driver):
    """Return visible text of the current page (strips HTML tags)."""
    return driver.execute_script("return document.body.textContent").lower()


def dismiss_cookie_popup(driver):
    """Hide cookie/policy popup containers (not the body) so they don't block form."""
    driver.execute_script(
        "document.querySelectorAll('.eupopup-container').forEach(function(e){"
        "e.style.display='none';})"
    )
    time.sleep(0.3)


class LoggedInSearchTest(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_loggedin_search(self):
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            print(f"\n  Running {row['test_id']}: user={row['username']!r} keyword={row['keyword']!r}", flush=True)
            with self.subTest(test_id=row["test_id"]):
                driver = self.driver
                driver.delete_all_cookies()

                login_url = row["login_url"]
                username_field_id = row["username_field_id"]
                password_field_id = row["password_field_id"]
                login_button_id = row["login_button_id"]
                course_index_url = row["course_index_url"]
                search_input_css = row["search_input_id"]
                search_button_css = row["search_button_css"]

                # Navigate to site root first to establish domain for cookies
                driver.get(row["base_url"])
                time.sleep(1)

                # Login
                driver.get(login_url)
                time.sleep(1)
                dismiss_cookie_popup(driver)

                self.wait.until(
                    EC.presence_of_element_located((By.ID, username_field_id))
                ).send_keys(row["username"])
                driver.find_element(By.ID, password_field_id).send_keys(row["password"])
                # Use JS click to avoid interception by any remaining overlay
                driver.execute_script(
                    "arguments[0].click()",
                    driver.find_element(By.ID, login_button_id),
                )
                # Wait for login redirect to complete before navigating further
                self.wait.until(lambda d: "login" not in d.current_url)

                # Navigate to course search after login
                driver.get(course_index_url)
                time.sleep(1)

                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, search_input_css))
                )
                search_box.clear()
                search_box.send_keys(row["keyword"])
                driver.find_element(By.CSS_SELECTOR, search_button_css).click()
                time.sleep(2)

                # Assert the expected course appears in results
                expected_course = row["expected_course"]
                self.assertIn(expected_course.lower(), page_text(driver))

                # Click the course link and verify landing on course page
                course_link = self.wait.until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, expected_course))
                )
                course_link.click()
                time.sleep(1)

                self.assertIn(row["expected_course_url_fragment"], driver.current_url)

                driver.delete_all_cookies()


if __name__ == "__main__":
    unittest.main(verbosity=2)
