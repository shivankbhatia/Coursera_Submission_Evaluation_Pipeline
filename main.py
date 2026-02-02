import pandas as pd
import os

from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.local_llm import run_local_llm


# =====================================================
# SYSTEM INSTRUCTION (LLM JUDGE)
# =====================================================

SYSTEM_INSTRUCTION = """
You are an academic evaluator.

Judge submission credibility using these rules ONLY:

1. Coursera certificate must be valid.
2. Student name must match between certificate and LinkedIn.
3. Project name on LinkedIn must refer to the same project as Coursera.
4. Ignore hashtags completely.
5. Judge based on credibility and consistency, not formatting.

Return exactly one line:
VERDICT: PASS
or
VERDICT: FAIL
"""


# =====================================================
# FINAL LLM JUDGMENT FUNCTION
# =====================================================

def ai_final_evaluation(student_name, coursera_data, linkedin_data):
    """
    Uses LLM ONLY to judge credibility, not to detect errors.
    """

    linkedin_summary = f"""
Public visibility: {linkedin_data.get("public_visibility")}
Student name found: {linkedin_data.get("student_name_found")}
LinkedIn project name: {linkedin_data.get("linkedin_project_name")}
Coursera project name: {linkedin_data.get("coursera_project_name")}
"""

    prompt = f"""
{SYSTEM_INSTRUCTION}

Student name:
{student_name}

Coursera verification:
{coursera_data.get("verification_line")}

LinkedIn observations:
{linkedin_summary}
"""

    return run_local_llm(prompt)


# =====================================================
# DETERMINISTIC FAILURE REASONING
# =====================================================

def determine_failure_reason(roll, project, seen_projects, coursera_data, linkedin_data):
    """
    Determines ONE primary failure reason deterministically.
    """

    if project in seen_projects.get(roll, set()):
        return "Duplicate project submission for the same roll number."

    if not coursera_data.get("verification_line"):
        return "Coursera certificate could not be verified."

    if not linkedin_data.get("student_name_found"):
        return "Student name does not match between certificate and LinkedIn post."

    if not linkedin_data.get("linkedin_project_name"):
        return "Project name could not be identified in the LinkedIn post."

    if not linkedin_data.get("public_visibility"):
        return "LinkedIn post is not publicly visible."

    return "LinkedIn post does not credibly match the Coursera certificate."


# =====================================================
# AGENT PIPELINE
# =====================================================

def run_pipeline(input_filename):

    input_path = os.path.join("data", "inputs", input_filename)
    df = pd.read_csv(input_path)

    results = []
    seen_projects_by_roll = {}

    total = len(df)

    print("\n🤖 AI AGENTIC EVALUATOR STARTED\n")

    for index, row in df.head(57).iterrows():

        print(f"\n[{index + 1}/{total}] Evaluating: {row['Full Name']}")

        roll = row["Roll Number"]

        # =============================
        # 1. Coursera Perception
        # =============================
        print("  ▶ Checking Coursera certificate...")
        coursera_data = verify_coursera_certificate(
            row["Coursera completion certificate link"],
            row["Full Name"]
        )
        print("  ✓ Coursera data extracted")

        verification_line = coursera_data.get("verification_line", "")
        coursera_project = ""

        if "completion of" in verification_line:
            coursera_project = verification_line.split("completion of")[-1].strip()

        project_key = coursera_project.lower()

        if roll not in seen_projects_by_roll:
            seen_projects_by_roll[roll] = set()

        is_duplicate = project_key in seen_projects_by_roll[roll]

        # =============================
        # 2. LinkedIn Perception
        # =============================
        print("  ▶ Analyzing LinkedIn post...")
        linkedin_data = get_linkedin_observations(
            row["LinkedIn Post Link"],
            row["Full Name"],
            coursera_project
        )
        print("  ✓ LinkedIn observations ready")

        # =============================
        # 3. Verdict Logic
        # =============================
        if is_duplicate:
            verdict = "FAIL"
            reason = "Duplicate project submission for the same roll number."

        else:
            print("  ▶ Running AI judgment (local LLM)...")
            ai_output = ai_final_evaluation(
                row["Full Name"],
                coursera_data,
                linkedin_data
            )

            if "VERDICT: PASS" in ai_output.upper():
                verdict = "PASS"
                reason = ""
                seen_projects_by_roll[roll].add(project_key)
            else:
                verdict = "FAIL"
                reason = determine_failure_reason(
                    roll,
                    project_key,
                    seen_projects_by_roll,
                    coursera_data,
                    linkedin_data
                )

        print(f"  ✓ Verdict generated: {verdict}")

        # =============================
        # 4. Save Result
        # =============================
        results.append({
            "Roll Number": roll,
            "Full Name": row["Full Name"],
            "Coursera Completion Date": coursera_data.get("completion_date"),
            "Coursera Verification Line": coursera_data.get("verification_line"),
            "LinkedIn Public": linkedin_data.get("public_visibility"),
            "LinkedIn Project": linkedin_data.get("linkedin_project_name"),
            "AI Verdict": verdict,
            "Failure Reason": reason
        })

    # =============================
    # OUTPUT
    # =============================
    output_path = os.path.join("data", "outputs", "Final_Evaluation_2.xlsx")
    pd.DataFrame(results).to_excel(output_path, index=False)

    print("\n✅ Evaluation completed successfully.")
    print(f"📁 Output saved at: {output_path}")


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_pipeline("submission.csv")
