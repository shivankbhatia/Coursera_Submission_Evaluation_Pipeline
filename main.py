import pandas as pd
import os
import threading

from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match

from utils.google_sheet_logger import init_sheet
from utils.google_sheet_logger import append_result_live


llm_queue = Queue()
results_lock = threading.Lock()

fast_completed = 0
llm_completed = 0

counter_lock = threading.Lock()


# -------------------------
# DEBUG STATUS LOGGER
# -------------------------
def debug_status(prefix, message):
    print(f"[{prefix}] {message}")


# -------------------------
# LLM WORKER THREAD
# -------------------------
def llm_worker(results):

    global llm_completed

    debug_status("LLM", "Worker Started")

    while True:

        task = llm_queue.get()

        if task is None:
            debug_status("LLM", "Worker Stopped")
            break

        index, roll, name, coursera_project, completion_date, linkedin_description = task

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

        results[index]["Final Verdict"] = verdict
        results[index]["Failure Reason"] = reason

        append_result_live([
            roll,
            name,
            coursera_project,
            completion_date,
            results[index]["Project Mention Match"],
            verdict,
            reason
        ])

        llm_queue.task_done()

        # ⭐ LLM COUNTER + STATUS
        with counter_lock:
            llm_completed += 1

            debug_status(
                "LLM",
                f"Completed: {llm_completed} | Remaining Queue: {llm_queue.qsize()}"
            )


# -------------------------
# FAST RECORD PROCESSING
# -------------------------
def process_fast_record(row, results, seen_certificates_by_roll):

    global fast_completed

    roll = row["Roll Number"]
    certificate_link = row["Coursera completion certificate link"].strip()

    coursera_data = verify_coursera_certificate(
        certificate_link,
        row["Full Name"]
    )

    coursera_project = coursera_data.get("coursera_project_name")
    completion_date = coursera_data.get("completion_date", "")

    linkedin_data = get_linkedin_observations(
        row["LinkedIn Post Link"],
        row["Full Name"],
        coursera_project
    )

    if roll not in seen_certificates_by_roll:
        seen_certificates_by_roll[roll] = set()

    is_duplicate = certificate_link in seen_certificates_by_roll[roll]

    if not is_duplicate:
        seen_certificates_by_roll[roll].add(certificate_link)

    linkedin_description = linkedin_data.get("linkedin_description", "")

    result_entry = {
        "Roll Number": roll,
        "Full Name": row["Full Name"],
        "Coursera Project": coursera_project,
        "Certificate Completion Date": completion_date,
        "Project Mention Match": linkedin_data.get("project_match"),
        "Final Verdict": None,
        "Failure Reason": "",
        "Duplicate Certificate": is_duplicate,
        "LLM Context Match": False,
        "LLM Confidence": 0,
    }

    with results_lock:
        results.append(result_entry)
        current_index = len(results) - 1

    # -------------------------
    # FAST VERDICT LOGIC
    # -------------------------

    if is_duplicate:

        results[current_index]["Final Verdict"] = "FAIL"
        results[current_index]["Failure Reason"] = "Duplicate certificate"

        append_result_live([
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_data.get("project_match"),
            "FAIL",
            "Duplicate certificate"
        ])

    elif linkedin_data.get("project_match"):

        results[current_index]["Final Verdict"] = "PASS"

        append_result_live([
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_data.get("project_match"),
            "PASS",
            ""
        ])

    else:

        llm_queue.put((
            current_index,
            roll,
            row["Full Name"],
            coursera_project,
            completion_date,
            linkedin_description
        ))

    # ⭐ FAST COUNTER + STATUS
    with counter_lock:
        fast_completed += 1

        debug_status(
            "FAST",
            f"Completed: {fast_completed} | LLM Queue: {llm_queue.qsize()}"
        )


# -------------------------
# MAIN PIPELINE
# -------------------------
def run_pipeline(input_filename):

    input_path = os.path.join("data", "inputs", input_filename)
    df = pd.read_csv(input_path)

    init_sheet()

    results = []
    seen_certificates_by_roll = {}

    NUM_LLM_WORKERS = 2
    FAST_WORKERS = 4

    workers = []

    for _ in range(NUM_LLM_WORKERS):
        t = threading.Thread(target=llm_worker, args=(results,))
        t.start()
        workers.append(t)

    subset = df.iloc[39:60]

    # FAST PARALLEL
    with ThreadPoolExecutor(max_workers=FAST_WORKERS) as executor:

        futures = []

        for _, row in subset.iterrows():
            futures.append(
                executor.submit(process_fast_record, row, results, seen_certificates_by_roll)
            )

        for f in futures:
            f.result()

    debug_status("PIPELINE", "FAST processing finished")
    debug_status("PIPELINE", f"Waiting LLM completion | Pending: {llm_queue.qsize()}")

    llm_queue.join()

    for _ in workers:
        llm_queue.put(None)

    for w in workers:
        w.join()

    output_path = os.path.join("data", "outputs", "Final_Evaluation_8.csv")

    output_df = pd.DataFrame(results)

    output_df = output_df[[
        "Roll Number",
        "Full Name",
        "Coursera Project",
        "Certificate Completion Date",
        "Project Mention Match",
        "Final Verdict",
        "Failure Reason"
    ]]

    output_df.to_csv(output_path, index=False)

    debug_status("PIPELINE", "Evaluation Complete")


if __name__ == "__main__":
    run_pipeline("submission.csv")
