from fastapi import FastAPI, HTTPException
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
    allow_origins=["*"],  # for development
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

    if matches.empty:
        async def error_stream():
            yield f"data: {json.dumps({'error': 'Roll number not found'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def event_generator():

        for idx, row in matches.iterrows():

            # 1️⃣ Send Queued state immediately
            yield f"data: {json.dumps({'row_id': idx, 'status': 'Queued'})}\n\n"
            await asyncio.sleep(0.1)

            # 2️⃣ Send Evaluating state
            yield f"data: {json.dumps({'row_id': idx, 'status': 'Evaluating'})}\n\n"
            await asyncio.sleep(0.1)

            # 3️⃣ FAST PHASE
            fast_result = evaluate_student_fast_phase(row)

            # If completed in fast phase
            if fast_result["phase"] == "completed":

                payload = {
                    "index": index,
                    "status": "Queued"
                }
                yield f"data: {json.dumps(payload)}\n\n"

                continue

            # 4️⃣ LLM REQUIRED
            if fast_result["phase"] == "llm_required":

                # Notify UI that slow validation started
                yield f"data: {json.dumps({
                    'row_id': idx,
                    'status': 'LLM Validation (may take 1-2 minutes)'
                })}\n\n"

                # Small pause to allow UI update
                await asyncio.sleep(0.2)

                # Run slow LLM phase
                final_result = evaluate_student_llm_phase(
                    fast_result["data"]
                )

                yield f"data: {json.dumps({
                    'row_id': idx,
                    'status': 'Completed',
                    'result': final_result
                })}\n\n"

            await asyncio.sleep(0.2)

        # Optional: Signal stream end
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
