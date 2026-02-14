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
        completion_date = og_data.get("og:description")  # Often contains completion info

        if project_name:
            project_name = " ".join(project_name.split()[3:])

        # Extract static page text
        page_text = soup.get_text(separator=" ")

        name_found = False

        if expected_name and expected_name.lower() in page_text.lower():
            name_found = True

        # -------------------------
        # PLAYWRIGHT FALLBACK
        # -------------------------
        # if not name_found and expected_name:

        #     print("\n⚠ Playwright fallback triggered")
        #     print(f"URL: {url}")

            # with sync_playwright() as p:

            #     browser = p.chromium.launch(headless=True)
            #     page = browser.new_page()

            #     page.goto(url, wait_until="networkidle")

            #     rendered_text = page.locator("body").inner_text()

            #     # Try extracting completion date from rendered page
            #     completion_date_rendered = completion_date
            #     if "completed" in rendered_text.lower():
            #         completion_date_rendered = "Found in rendered page"

            #     # Check name again
            #     if expected_name.lower() in rendered_text.lower():
            #         name_found = True

            #     # ⭐ PRINT REQUIRED DATA
            #     print("----- Coursera Extracted Data (Fallback) -----")
            #     print(f"Student Name          : {expected_name}")
            #     print(f"Coursera Project Name : {project_name}")
            #     print(f"Completion Date       : {completion_date_rendered}")
            #     print("------------------------------------------------\n")

            #     browser.close()

        if not name_found  and expected_name:
            return {
                "Cert_Status": "Fail",
                "coursera_project_name": '',
                "completion_date": '',
                "student_name_found": '',
            }
        
        return {
            "Cert_Status": "Success",
            "coursera_project_name": project_name,
            "completion_date": completion_date,
            "student_name_found": name_found,
        }

    except Exception as e:
        return {
            "Cert_Status": "Error",
            "error": str(e)
        }
