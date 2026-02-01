from utils.local_llm import run_local_llm

prompt = """
Student completed Working with BigQuery.
LinkedIn project: Working with BigQuery.
Name found: True.
Missing hashtags: [].

Reply with PASS or FAIL.
"""

print(run_local_llm(prompt))
