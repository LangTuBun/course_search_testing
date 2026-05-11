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

DATA_FILE = os.path.join(os.path.dirname(__file__), "search_data.csv")


def expand_keyword(keyword):
    """Expand $REPEAT_<char>_<count> sentinels so CSVs stay readable."""
    if keyword.startswith("$REPEAT_"):
        char, count = keyword[8:].rsplit("_", 1)
        return char * int(count)
    return keyword


def page_text(driver):
    """Return visible text of the current page (strips HTML tags)."""
    return driver.execute_script("return document.body.textContent").lower()


class SearchTest(unittest.TestCase):
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

    def test_search(self):
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            with self.subTest(test_id=row["test_id"]):
                driver = self.driver
                base_url = row["base_url"]
                search_input_css = row["search_input_id"]
                search_button_css = row["search_button_css"]
                keyword = expand_keyword(row["keyword"])
                display_kw = keyword if len(keyword) <= 20 else f"{keyword[:10]}...({len(keyword)} chars)"
                print(f"\n  Running {row['test_id']}: keyword={display_kw!r}", flush=True)
                expected = row["expected_result"]

                driver.get(base_url)
                time.sleep(1)

                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, search_input_css))
                )
                search_box.clear()
                search_box.send_keys(keyword)
                driver.find_element(By.CSS_SELECTOR, search_button_css).click()
                time.sleep(2)

                text = page_text(driver)
                current_url = driver.current_url

                # Crash guard applied to every row
                self.assertNotIn("fatal error", text)

                if expected == "all_courses_or_prompt":
                    self.assertIn("courses", text)

                elif expected == "results_page_loaded":
                    self.assertIn(row["expected_url_fragment"], current_url)

                elif expected == "no_crash":
                    pass  # crash check above is sufficient

                elif expected == "No courses were found":
                    self.assertIn("no courses were found", text)

                elif expected == "MULTI_STEP_011":
                    # Step 1: QuantumXYZ returns no results
                    self.assertIn("no courses were found", text)
                    # Step 2: results page has no course search form; go back to index
                    driver.get(base_url)
                    time.sleep(1)
                    search_box = self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, search_input_css)
                        )
                    )
                    search_box.clear()
                    search_box.send_keys("English")
                    driver.find_element(By.CSS_SELECTOR, search_button_css).click()
                    time.sleep(2)
                    self.assertIn("english grammar", page_text(driver))

                else:
                    self.assertIn(expected.lower(), text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
