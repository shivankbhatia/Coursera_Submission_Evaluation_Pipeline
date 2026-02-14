from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
from core.evaluator import (
    evaluate_student_fast_phase,
    evaluate_student_llm_phase
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load submission file ONCE
# -------------------------
submission_df = pd.read_csv("submission2.csv")


class StudentQuery(BaseModel):
    roll_number: str
    full_name: str


@app.get("/evaluate-stream/{roll_number}")
async def evaluate_stream(roll_number: str):

    matches = submission_df[
        submission_df["Roll Number"].astype(str) == roll_number
    ].reset_index(drop=True)

    # -------------------------
    # No records found
    # -------------------------
    if matches.empty:
        async def error_stream():
            payload = {"error": "Roll number not found"}
            yield f"data: {json.dumps(payload)}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # -------------------------
    # Main Stream Generator
    # -------------------------
    async def event_generator():

        for idx, row in matches.iterrows():

            # 1️⃣ Queued
            payload = {
                "row_id": idx,
                "status": "Queued"
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.1)

            # 2️⃣ Evaluating
            payload = {
                "row_id": idx,
                "status": "Evaluating"
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.1)

            # 3️⃣ FAST PHASE
            fast_result = evaluate_student_fast_phase(row)

            # -------------------------
            # Completed in FAST phase
            # -------------------------
            if fast_result["phase"] == "completed":

                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": fast_result["result"]
                }

                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)
                continue

            # -------------------------
            # LLM REQUIRED
            # -------------------------
            if fast_result["phase"] == "llm_required":

                # Notify frontend slow validation
                payload = {
                    "row_id": idx,
                    "status": "LLM Validation (may take 1-2 minutes)"
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

                # Run LLM
                final_result = evaluate_student_llm_phase(
                    fast_result["data"]
                )

                payload = {
                    "row_id": idx,
                    "status": "Completed",
                    "result": final_result
                }

                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)

        # Stream finished
        payload = {"done": True}
        yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
