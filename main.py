import pandas as pd
import os

from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.local_llm import run_local_llm
from utils.context_project_match import llm_project_context_match



SYSTEM_INSTRUCTION = """
You are an academic evaluator.

Judge submission credibility using these rules ONLY:

1. Coursera certificate must be valid.
2. Student name must match between certificate and LinkedIn.
3. LinkedIn post must clearly mention the Coursera project.
4. Ignore hashtags completely.

Return exactly one line:
VERDICT: PASS
or
VERDICT: FAIL
"""


def ai_final_evaluation(student_name, coursera_data, linkedin_data):

    # print("\n========== RAW COURSERA DATA ==========")
    # print(coursera_data)

    # print("\n========== RAW LINKEDIN DATA ==========")
    # print(linkedin_data)

    linkedin_summary = f"""
Public visibility: {linkedin_data.get("public_visibility")}
Student name found: {linkedin_data.get("student_name_found")}
LinkedIn mentions Coursera project: {linkedin_data.get("project_match")}
Coursera project name: {coursera_data.get("coursera_project_name")}
"""

    llm_prompt = f"""
{SYSTEM_INSTRUCTION}

Student name:
{student_name}

LinkedIn observations:
{linkedin_summary}
"""

    # print("\n========== DATA SENT TO LLM ==========")
    # print(llm_prompt)
    # print("\n======================================\n")

    return run_local_llm(llm_prompt)


def llm_name_match(
    student_name,
    coursera_name_found,
    linkedin_name_found,
    linkedin_username,
    linkedin_description,
    coursera_project_name
):

    prompt = f"""
You are an academic evaluator.

Your job is to decide whether the LinkedIn post
describes work related to the project title.

Project Title:
{coursera_project_name}

LinkedIn Post:
{linkedin_description}

IMPORTANT:
Respond ONLY with valid JSON.
Do not add explanation outside JSON.
Do not add markdown.
Do not add extra text.

Return EXACTLY:

{{
 "match": true or false,
 "confidence": number between 0 and 100,
 "reason": "one short sentence"
}}
"""


    result = run_local_llm(prompt)

    return "TRUE" in result.upper()


def run_pipeline(input_filename):

    input_path = os.path.join("data", "inputs", input_filename)
    df = pd.read_csv(input_path)

    results = []
    seen_certificates_by_roll = {}

    subset = df.iloc[39:60]

    for index, row in subset.iterrows():

        print(f"\n[{index + 1}/{len(df)}] Evaluating: {row['Full Name']}")

        roll = row["Roll Number"]
        certificate_link = row["Coursera completion certificate link"].strip()

        # =============================
        # Coursera Perception
        # =============================
        coursera_data = verify_coursera_certificate(
            certificate_link,
            row["Full Name"]
        )

        coursera_project = coursera_data.get("coursera_project_name")

        # =============================
        # LinkedIn Perception
        # =============================
        linkedin_data = get_linkedin_observations(
            row["LinkedIn Post Link"],
            row["Full Name"],
            coursera_project
        )

        # =============================
        # Duplicate Certificate Check
        # =============================
        if roll not in seen_certificates_by_roll:
            seen_certificates_by_roll[roll] = set()

        is_duplicate = certificate_link in seen_certificates_by_roll[roll]

        if not is_duplicate:
            seen_certificates_by_roll[roll].add(certificate_link)

        # =============================
        # Final Decision Logic
        # =============================

        linkedin_description = linkedin_data.get("linkedin_description", "")

        llm_match_result = {
            "match": False,
            "confidence": 0,
            "reason": ""
        }

        if is_duplicate:
            verdict = "FAIL"
            reason = "Duplicate Coursera certificate submission."

        elif linkedin_data.get("project_match"):
            verdict = "PASS"
            reason = ""

        else:
            # ⭐ Run LLM ONLY when project_match fails
            if coursera_project and linkedin_description:
                llm_match_result = llm_project_context_match(
                    coursera_project,
                    linkedin_description
                )

            if llm_match_result["match"]:
                verdict = "PASS"
                reason = f"LLM Context Match ({llm_match_result['confidence']}%)"
            else:
                verdict = "FAIL"
                reason = "LinkedIn post does not mention the Coursera project."


        # =============================
        # Output Raw Signals Only
        # =============================
        results.append({
            "Roll Number": roll,
            "Full Name": row["Full Name"],
            "Coursera Project": coursera_project,
            "Duplicate Certificate": is_duplicate,
            "Project Mention Match": linkedin_data.get("project_match"),
            "LLM Context Match": llm_match_result["match"],
            "LLM Confidence": llm_match_result["confidence"],
            "LLM Reason": llm_match_result["reason"],
            "Final Verdict": verdict,
            "Failure Reason": reason,
        })

    output_path = os.path.join("data", "outputs", "Final_Evaluation_6.csv")
    pd.DataFrame(results).to_csv(output_path, index=False)

    print("\n✅ Debug output generated.")



if __name__ == "__main__":
    run_pipeline("submission.csv")
