import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def verify_coursera_certificate(url, expected_name=None):

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        # -------------------------
        # FAST EXTRACTION (Requests)
        # -------------------------
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # OG extraction
        og_data = {}
        for tag in soup.find_all("meta"):
            if tag.get("property", "").startswith("og:"):
                og_data[tag["property"]] = tag.get("content", "")

        project_name = og_data.get("og:title")
        if project_name:
            project_name = " ".join(project_name.split()[3:])

        # Static HTML text extraction
        page_text = soup.get_text(separator=" ")

        name_found = False

        if expected_name and expected_name.lower() in page_text.lower():
            name_found = True

        # -------------------------
        # PLAYWRIGHT FALLBACK
        # -------------------------
        if not name_found and expected_name:

            print("⚠ Name not found in static HTML → Using Playwright fallback")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url, wait_until="networkidle")

                rendered_text = page.locator("body").inner_text()

                if expected_name.lower() in rendered_text.lower():
                    name_found = True

                browser.close()

        return {
            "Cert_Status": "Success",
            "coursera_project_name": project_name,
            "student_name_found": name_found,
        }

    except Exception as e:
        return {
            "Cert_Status": "Error",
            "error": str(e)
        }
