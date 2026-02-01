import re
from playwright.sync_api import sync_playwright


def verify_coursera_certificate(url, expected_name):
    """
    Optimized Coursera Sensor
    Extracts ONLY:
    1. Completion date
    2. Verified completion line (name + project)
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)

            raw_text = page.locator("body").inner_text()

            # -----------------------------
            # 1. Extract completion date
            # -----------------------------
            date_match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
                raw_text
            )

            completion_date = date_match.group(0) if date_match else "Date not found"

            # -----------------------------------------------
            # 2. Extract verified completion sentence
            # -----------------------------------------------
            verification_pattern = (
                rf"{re.escape(expected_name)}'s account is verified\. "
                r"Coursera certifies their successful completion of .+"
            )

            verification_match = re.search(verification_pattern, raw_text)

            verification_line = (
                verification_match.group(0)
                if verification_match
                else "Verification line not found"
            )

            return {
                "Cert_Status": "Success",
                "completion_date": completion_date,
                "verification_line": verification_line,
                "raw_text": f"{completion_date}\n{verification_line}"
            }

        except Exception as e:
            return {
                "Cert_Status": f"Error: {str(e)[:60]}",
                "completion_date": "",
                "verification_line": "",
                "raw_text": ""
            }

        finally:
            browser.close()
