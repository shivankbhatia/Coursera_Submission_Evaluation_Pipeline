import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


def run_llama(prompt, temperature=0.1):
    """
    Runs prompt on Ollama Llama model
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        raise RuntimeError("Ollama request failed")

    return response.json()["response"]


# ---------------------------------------------------
# MAIN CONTEXT MATCH FUNCTION
# ---------------------------------------------------

def llm_project_context_match(project_name, linkedin_text):
    """
    Uses Llama 3.1 to determine if LinkedIn post
    genuinely relates to the project.
    """

    prompt = f"""
You are a STRICT but INTELLIGENT academic project evaluator.

Your task is to determine whether a LinkedIn post genuinely describes work 
related to a specific academic guided project.

----------------------------------------
Project Title:
{project_name}

LinkedIn Post:
{linkedin_text}
----------------------------------------

Evaluation Instructions:

1. The LinkedIn post may contain MULTIPLE projects.
   If ANY one project in the post meaningfully corresponds 
   to the given Project Title, mark match = true.

2. The project title does NOT need to match word-for-word.
   Accept minor variations such as:
   - Abbreviations (e.g., ML for Machine Learning)
   - Reordered words
   - Slight phrasing differences
   - “Introduction to X” vs “X Basics”
   - “Guided Project” vs “Hands-on Project”
   - Singular/plural variations
   - Use of  word 'using' instead of 'with' or vice-a-versa.

3. Use SEMANTIC similarity — not strict string matching.
   If the overall topic, objective, and workflow clearly align,
   consider it a match.

4. The post MUST demonstrate hands-on work:
   - Learning outcomes
   - Implementation
   - Code development
   - Dataset usage
   - Model building
   - System design
   - Technical pipeline
   - Real output or results

5. Generic statements such as:
   - "I completed a course"
   - "I learned about X"
   - "Great experience"
   are NOT sufficient.

6. Mentioning tools or buzzwords alone is NOT sufficient.
   The post must show actual project-level involvement.

7. If the post discusses multiple projects,
   evaluate each independently and return TRUE
   if at least one strongly aligns.

Be academically conservative but not overly rigid.
Accept realistic variations in naming.

----------------------------------------

Confidence Scoring:

90–100 → Explicit, detailed project explanation  
70–89  → Strong technical overlap and workflow similarity  
40–69  → Weak or indirect relation  
0–39   → No meaningful relation  

----------------------------------------

Return STRICT JSON only:
{{
 "match": true or false,
 "confidence": number from 0 to 100,
 "reason": "short explanation"
}}
"""

    raw_output = run_llama(prompt)


    # -------------------------
    # SAFE JSON PARSE
    # -------------------------
    try:
        json_start = raw_output.find("{")
        json_end = raw_output.rfind("}") + 1
        json_str = raw_output[json_start:json_end]

        result = json.loads(json_str)
        # Confidence calibration
        if not result["match"]:
            result["confidence"] = min(result["confidence"], 40)

        if result["match"] and result["confidence"] < 60:
            result["match"] = False
        
        return result

    except Exception:

        # fallback if model produces messy output
        return {
            "match": False,
            "confidence": 0,
            "reason": "Parsing failed"
        }
