import requests
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def normalize_name(text):
    return re.sub(r"[^a-z]", "", text.lower()) if text else ""


def extract_linkedin_username(url):

    match = re.search(r"linkedin\.com/(in|posts)/([^/?]+)", url)

    if match:
        return match.group(2)

    return None


def username_matches_student(username, student_name):

    if not username:
        return False

    return normalize_name(student_name) in normalize_name(username)


def extract_name_from_og_title(og_title):

    if not og_title:
        return None

    return og_title.split("|")[0].strip()


def verify_linkedin_identity(url, student_name):

    # ------------------------
    # Step 1 → Username Match
    # ------------------------
    username = extract_linkedin_username(url)

    if username_matches_student(username, student_name):
        return True

    # ------------------------
    # Step 2 → OG Title Match
    # ------------------------
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        og_title = None
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:title":
                og_title = tag.get("content")

        profile_name = extract_name_from_og_title(og_title)

        if profile_name and normalize_name(student_name) in normalize_name(profile_name):
            return True

    except:
        pass

    # ------------------------
    # Step 3 → Playwright fallback
    # ------------------------
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle")

            rendered_text = page.locator("body").inner_text()

            browser.close()

            return normalize_name(student_name) in normalize_name(rendered_text)

    except:
        return False


def check_project_presence(linkedin_text, coursera_project):

    if not linkedin_text or not coursera_project:
        return False

    return coursera_project.lower() in linkedin_text.lower()


def get_linkedin_observations(url, student_name, coursera_project_name):

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        og = {}
        for tag in soup.find_all("meta"):
            if tag.get("property", "").startswith("og:"):
                og[tag["property"]] = tag.get("content", "")

        description = og.get("og:description", "")
        is_public = bool(description.strip())

        # ⭐ Identity verification using username + fallback
        name_match = verify_linkedin_identity(url, student_name)

        project_match = check_project_presence(description, coursera_project_name)

        return {
            "status": "Success",
            "public_visibility": is_public,
            "student_name_found": name_match,
            "project_match": project_match,
            "linkedin_description": description 
        }

    except Exception as e:
        return {
            "status": "Fail",
            "error": str(e)
        }
