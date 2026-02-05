import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


def run_llama(prompt, temperature=0.2):
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
You are an academic project evaluator.

Your task is to determine whether a LinkedIn post
credibly describes work related to a specific project.

Project Title:
{project_name}

LinkedIn Post:
{linkedin_text}

Evaluation Rules:
- Check conceptual overlap
- Tools mentioned should relate
- Workflow similarity counts
- Indirect references allowed
- Ignore hashtags

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
        return result

    except Exception:

        # fallback if model produces messy output
        return {
            "match": False,
            "confidence": 0,
            "reason": "Parsing failed"
        }
