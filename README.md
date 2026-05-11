# Course Search – Automated Testing Suite

A data-driven Selenium test suite for the **Course Search** feature on the [Mount Orange Moodle Demo](https://school.moodledemo.net) (`/course/index.php`).

---

## Overview

The suite covers TC-004-001 through TC-004-011 across two abstraction levels plus a non-functional performance test.

| Level | What's hardcoded | What comes from CSV |
|---|---|---|
| Level 1 | Base URL, element selectors | Keywords, expected results |
| Level 2 | Nothing site-specific | URL, selectors, keywords, expected results |
| Non-functional | — | Inline test cases (3 performance scenarios) |

---

## Prerequisites

- Python 3.8+
- Google Chrome (any recent version)
- Internet connection to `school.moodledemo.net`

---

## Setup

```bash
pip install -r requirements.txt
```

`webdriver-manager` automatically downloads the matching ChromeDriver on first run — no manual driver setup needed.

---

## Running the tests

All commands should be run from the project root directory.

### Level 1

```bash
python -m unittest Level1/search_test.py -v          # TC-004-001 to 008, 010, 011
python -m unittest Level1/loggedin_search_test.py -v # TC-004-009 (logged-in flow)
```

### Level 2

```bash
python -m unittest Level2/search_test.py -v
python -m unittest Level2/loggedin_search_test.py -v
```

### Non-functional (performance)

```bash
python -m unittest NonFunctional/nonfunctional_performance_test.py -v
```

**Flags explained:**
- `-m unittest` — runs the unittest framework (equivalent to `python Level1/search_test.py`)
- `-v` — verbose output showing each test case ID as it runs; omit for a concise dot summary

### Expected output (passing)

```
test_search (...) ...
  Running TC-004-001: keyword=''
  Running TC-004-002: keyword='a'
  Running TC-004-003: keyword='Biology'
  Running TC-004-004: keyword='aaaaaaaaaa...(300 chars)'
  ...
  Running TC-004-011: keyword='QuantumXYZ'
ok

Ran 1 test in ~60s

OK
```

> "Ran 1 test" is expected — it means 1 test *method* that loops through all CSV rows via `subTest`. A failure in one row does not abort the rest.

---

## Test cases covered

| TC ID | Keyword | Technique | Expected outcome |
|---|---|---|---|
| TC-004-001 | (empty) | BVA | Page loads without crashing |
| TC-004-002 | `a` | BVA | Results URL contains `search.php` |
| TC-004-003 | `Biology` | BVA | "General Biology (Foundation)" in results |
| TC-004-004 | `a` × 300 | BVA | "No courses were found" |
| TC-004-005 | `Psychology` | ECP | "Psychology in Cinema" in results |
| TC-004-006 | `xyznonexistent` | ECP | "No courses were found" |
| TC-004-007 | `@#$%^&*` | ECP | No crash or fatal error |
| TC-004-008 | `DIGITAL` | ECP | "Digital Literacy" in results (case-insensitive) |
| TC-004-009 | `Biology` (logged in) | Use-case | Login → search → click course → land on course page |
| TC-004-010 | `History` | Use-case | "History: Russia in Revolution" in results |
| TC-004-011 | `QuantumXYZ` → `English` | Use-case | No results → refine → "English Grammar & Syntax" found |

---

## File structure

```
Level1/
  search_test.py              # TC-004-001..008, 010, 011 (selectors hardcoded)
  search_data.csv
  loggedin_search_test.py     # TC-004-009
  loggedin_search_data.csv

Level2/
  search_test.py              # same TCs (URL + selectors from CSV)
  search_data.csv
  loggedin_search_test.py
  loggedin_search_data.csv

NonFunctional/
  nonfunctional_performance_test.py

requirements.txt
README.md
```

---

## Non-functional testing

**Type:** Performance  
**Approach:** Measures elapsed time from clicking the Search button to the results page body appearing, using `time.perf_counter()`. Selenium runs headless Chrome with no external load tool.  
**Threshold:** 5 seconds (standard interactive response target)

| TC ID | Keyword | Scenario |
|---|---|---|
| TC-PERF-001 | `Biology` | Valid keyword, results returned |
| TC-PERF-002 | `xyznonexistent` | No-result keyword |
| TC-PERF-003 | (empty) | Empty search |

---

## Important notes

**Moodle password rotation**  
The demo site resets hourly and the student password increments (e.g. `moodle26` → `moodle27`).  
If TC-004-009 fails at login, update the `password` field in:
- `Level1/loggedin_search_data.csv`
- `Level2/loggedin_search_data.csv`

The current password is always shown on the [Moodle demo login page](https://school.moodledemo.net/login/index.php).

**300-character keyword (TC-004-004)**  
The CSV stores the sentinel value `$REPEAT_a_300` to keep the file readable. Both `search_test.py` scripts expand this to 300 `a` characters at runtime before typing into the search box.

**Two-step search (TC-004-011)**  
Runs in a single Selenium session: step 1 submits `QuantumXYZ` (asserts no results), then step 2 navigates back to the search index, submits `English`, and asserts "English Grammar & Syntax" appears in results.

**Course name highlighting**  
Moodle wraps matched terms in `<span class="highlight">` in the HTML, which breaks plain `page_source` string matching. All text assertions use `document.body.textContent` (rendered text, tag-free) via JavaScript to work around this.
