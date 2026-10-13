
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Acme Appliances Order Ledger API")


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"status": "ok", "message": "Acme Ledger API is running"}


@app.post("/")
def answer_question(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # TODO: Load the assignment data and implement
    # accurate revenue, refund, product, and customer calculations.
    return {"answer": "Question processing is not implemented yet"}
