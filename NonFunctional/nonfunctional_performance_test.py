import time
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://school.moodledemo.net/course/index.php"
SEARCH_INPUT_CSS = "input[name='search']"
SEARCH_BUTTON_CSS = "button.search-icon"
PERFORMANCE_THRESHOLD_SECONDS = 5.0

TEST_CASES = [
    ("TC-PERF-001", "Biology", "valid keyword — expects results"),
    ("TC-PERF-002", "xyznonexistent", "no-result keyword"),
    ("TC-PERF-003", "", "empty search"),
]


class PerformanceTest(unittest.TestCase):
    """
    Non-functional performance test: measures elapsed time from Search button
    click to the results page body being present.  Threshold: 5 seconds.
    """

    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.wait = WebDriverWait(self.driver, 15)

    def tearDown(self):
        self.driver.quit()

    def test_search_response_time(self):
        for tc_id, keyword, description in TEST_CASES:
            kw_display = repr(keyword) if keyword else "'(empty)'"
            print(f"\n  Running {tc_id}: keyword={kw_display}", flush=True)
            with self.subTest(test_id=tc_id, keyword=keyword or "(empty)"):
                driver = self.driver

                driver.get(BASE_URL)
                time.sleep(1)

                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_CSS))
                )
                search_box.clear()
                search_box.send_keys(keyword)

                start = time.perf_counter()
                driver.find_element(By.CSS_SELECTOR, SEARCH_BUTTON_CSS).click()
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                elapsed = time.perf_counter() - start

                print(
                    f"\n  [{tc_id}] {description!r}: {elapsed:.3f}s "
                    f"(threshold: {PERFORMANCE_THRESHOLD_SECONDS}s)"
                )

                self.assertLess(
                    elapsed,
                    PERFORMANCE_THRESHOLD_SECONDS,
                    f"{description} response time {elapsed:.3f}s exceeded "
                    f"{PERFORMANCE_THRESHOLD_SECONDS}s threshold",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
