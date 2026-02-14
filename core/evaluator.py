from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match


def evaluate_student_fast_phase(row: dict):
    print("START FAST PHASE")

    roll = row["Roll Number"]
    full_name = row["Full Name"]
    certificate_link = row["Coursera completion certificate link"].strip()

    # 1️⃣ Verify Coursera
    print("Calling Coursera")
    coursera_data = verify_coursera_certificate(
        certificate_link,
        full_name
    )

    if coursera_data.get("Cert_Status") == "Fail":
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "verdict": "INVALID",
                "reason": "Coursera link is invalid."
            }
        }

    coursera_project = coursera_data.get("coursera_project_name")
    completion_date = coursera_data.get("completion_date", "")

    # 2️⃣ LinkedIn Fast Match
    print("Calling LinkedIn")
    linkedin_data = get_linkedin_observations(
        row["LinkedIn Post Link"],
        full_name,
        coursera_project
    )
    print("LinkedIn Done")


    if linkedin_data.get("project_match"):
        return {
            "phase": "completed",
            "result": {
                "roll_number": roll,
                "full_name": full_name,
                "project": coursera_project,
                "completion_date": completion_date,
                "verdict": "PASS",
                "reason": ""
            }
        }

    # If fast match failed → need LLM
    return {
        "phase": "llm_required",
        "data": {
            "roll": roll,
            "full_name": full_name,
            "project": coursera_project,
            "completion_date": completion_date,
            "linkedin_description": linkedin_data.get("linkedin_description", "")
        }
    }

def evaluate_student_llm_phase(data: dict):

    llm_result = llm_project_context_match(
        data["project"],
        data["linkedin_description"]
    )

    if llm_result.get("match"):
        return {
            "roll_number": data["roll"],
            "full_name": data["full_name"],
            "project": data["project"],
            "completion_date": data["completion_date"],
            "verdict": "PASS",
            "reason": f"LLM Context Match ({llm_result.get('confidence', 0)}%)"
        }

    return {
        "roll_number": data["roll"],
        "full_name": data["full_name"],
        "project": data["project"],
        "completion_date": data["completion_date"],
        "verdict": "FAIL",
        "reason": "LinkedIn post does not mention the Coursera project."
    }
