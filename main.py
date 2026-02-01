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

Your task is to judge whether a student's submission is valid.

Rules:
1. Project name on LinkedIn must semantically match the Coursera project.
2. Student name must be visible on LinkedIn.
3. Mandatory hashtags should be present (minor spelling mistakes may be tolerated).
4. Post must be publicly visible.
5. Judge based on academic intent, not formatting.

Return response ending with exactly one of:
VERDICT: PASS
or
VERDICT: FAIL
"""


# =====================================================
# FINAL LLM JUDGMENT FUNCTION
# =====================================================

def ai_final_evaluation(student_name, coursera_data, linkedin_data):

    linkedin_summary = f"""
Public visibility: {linkedin_data.get("public_visibility")}
Student name found: {linkedin_data.get("student_name_found")}
LinkedIn project name: {linkedin_data.get("linkedin_project_name")}
Coursera project name: {linkedin_data.get("coursera_project_name")}
Missing mandatory hashtags: {linkedin_data.get("missing_required_hashtags")}
"""

    prompt = f"""
You are an academic evaluator.

Decide if submission is valid.

Student name: {student_name}

Coursera verification:
{coursera_data.get("verification_line")}

LinkedIn observations:
{linkedin_summary}

Reply strictly with:
VERDICT: PASS
or
VERDICT: FAIL
"""

    return run_local_llm(prompt)



# =====================================================
# AGENT PIPELINE
# =====================================================

def ai_failure_reason(student_name, coursera_data, linkedin_data):

    prompt = f"""
You are an academic evaluator.

The submission has FAILED.

Based ONLY on the following observations, write ONE short sentence
explaining the primary reason for failure.

Do NOT add suggestions.
Do NOT add multiple reasons.
Do NOT exceed one sentence.

Observations:
- Student name found: {linkedin_data.get("student_name_found")}
- Public visibility: {linkedin_data.get("public_visibility")}
- LinkedIn project: {linkedin_data.get("linkedin_project_name")}
- Coursera project: {linkedin_data.get("coursera_project_name")}
- Missing mandatory hashtags: {linkedin_data.get("missing_required_hashtags")}

Return ONLY the sentence.
"""

    return run_local_llm(prompt)


def run_pipeline(input_filename):

    input_path = os.path.join("data", "inputs", input_filename)
    df = pd.read_csv(input_path)

    results = []

    total = min(5, len(df))

    print("\n🤖 AI AGENTIC EVALUATOR STARTED\n")

    for index, row in df.head(5).iterrows():

        print(f"\n[{index + 1}/{total}] Evaluating: {row['Full Name']}")

        # =============================
        # 1. Coursera Perception
        # =============================
        print("  ▶ Checking Coursera certificate...")
        coursera_data = verify_coursera_certificate(
            row["Coursera completion certificate link"],
            row["Full Name"]
        )
        print("  ✓ Coursera data extracted")

        # Extract project name
        verification_line = coursera_data.get("verification_line", "")
        coursera_project = ""
        if "completion of" in verification_line:
            coursera_project = verification_line.split("completion of")[-1].strip()

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
        # 3. AI Judgment
        # =============================
        print("  ▶ Running AI judgment (local LLM)...")
        ai_output = ai_final_evaluation(
            row["Full Name"],
            coursera_data,
            linkedin_data
        )

        if "VERDICT: PASS" in ai_output.upper():
            verdict = "PASS"
            reason = ""
        else:
            verdict = "FAIL"
            reason = ai_failure_reason(
                row["Full Name"],
                coursera_data,
                linkedin_data
            )
        print(f"  ✓ Verdict generated: {verdict}")

        # =============================
        # 4. Save Result
        # =============================
        results.append({
            "Full Name": row["Full Name"],
            "Coursera Completion Date": coursera_data.get("completion_date"),
            "Coursera Verification Line": coursera_data.get("verification_line"),
            "LinkedIn Public": linkedin_data.get("public_visibility"),
            "LinkedIn Project": linkedin_data.get("linkedin_project_name"),
            "Missing Mandatory Hashtags": ", ".join(
                linkedin_data.get("missing_required_hashtags", [])
            ),
            "AI Verdict": verdict,
            "Failure Reason": reason.strip(),
            "AI Explanation": ai_output
        })

    # =============================
    # Output
    # =============================
    output_path = os.path.join("data", "outputs", "Final_Evaluation.xlsx")
    pd.DataFrame(results).to_excel(output_path, index=False)

    print("\n✅ Evaluation completed successfully.")
    print(f"📁 Output saved at: {output_path}")

# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_pipeline("submission.csv")
