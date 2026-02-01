import subprocess

OLLAMA_PATH = r"C:\Users\bhati\AppData\Local\Programs\Ollama\ollama.exe"

def run_local_llm(prompt):
    """
    Runs local Ollama model safely on Windows (UTF-8 safe).
    """

    # Remove problematic unicode characters
    safe_prompt = prompt.encode("utf-8", errors="ignore").decode("utf-8")

    process = subprocess.run(
        [OLLAMA_PATH, "run", "qwen2.5:1.5b"],
        input=safe_prompt,
        text=True,
        encoding="utf-8",
        capture_output=True
    )

    return process.stdout.strip()
