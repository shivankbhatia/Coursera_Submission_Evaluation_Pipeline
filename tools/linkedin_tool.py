import requests
from bs4 import BeautifulSoup
import re


REQUIRED_HASHTAGS = [
    "#TIET",
    "#ThaparUniversity",
    "#ThaparOutcomeBasedLearning",
    "#ThaparCoursera",
    "#Coursera",
    "#UCS654_Predictive_Analytics"
]


def normalize(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_project_name(description):
    """
    Attempts to extract the project name from LinkedIn description.
    Handles quotes and formatting variations.
    """

    if not description:
        return None

    patterns = [
        r'completed.*?[“"](.+?)[”"]',                    # “Working with BigQuery”
        r'completed.*?[\'"](.+?)[\'"]',                  # 'Working with BigQuery'
        r'completed.*?(Working with [A-Za-z0-9\s]+)',    # fallback
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def get_linkedin_observations(url, student_name, coursera_project_name):
    """
    LinkedIn Observation Sensor

    This tool DOES NOT make verdict decisions.
    It only extracts observable evidence for the LLM judge.
    """

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # -------------------------
        # Extract Open Graph data
        # -------------------------
        og = {}
        for tag in soup.find_all("meta"):
            if tag.get("property", "").startswith("og:"):
                og[tag.get("property")] = tag.get("content", "").strip()

        title = og.get("og:title", "")
        description = og.get("og:description", "")

        combined_text = f"{title} {description}"

        # -------------------------
        # Observations
        # -------------------------
        is_public = bool(description.strip())

        name_found = normalize(student_name) in normalize(combined_text)

        linkedin_project = extract_project_name(description)

        detected_hashtags = re.findall(r"#\w+", description)

        missing_required_hashtags = [
            tag for tag in REQUIRED_HASHTAGS
            if tag.lower() not in map(str.lower, detected_hashtags)
        ]

        # -------------------------
        # Structured evidence
        # -------------------------
        return {
            "status": "Success",
            "public_visibility": is_public,
            "student_name_found": name_found,
            "linkedin_project_name": linkedin_project,
            "coursera_project_name": coursera_project_name,
            "detected_hashtags": detected_hashtags,
            "missing_required_hashtags": missing_required_hashtags,
            "raw_text": f"""
LinkedIn Title:
{title}

LinkedIn Description:
{description}

Extracted Project Name:
{linkedin_project}

Detected Hashtags:
{', '.join(detected_hashtags)}

Missing Mandatory Hashtags:
{', '.join(missing_required_hashtags) if missing_required_hashtags else 'None'}
"""
        }

    except Exception as e:
        return {
            "status": "Error",
            "error": str(e),
            "raw_text": ""
        }
