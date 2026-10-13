

import os
import requests
import calendar
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Acme Appliances Ledger Agent")

# Store the complete assignment URL in Render as ASSIGNMENT_URL.
ASSIGNMENT_URL = os.getenv("ASSIGNMENT_URL", "")


class Question(BaseModel):
    question: str


def fetch_data():
    if not ASSIGNMENT_URL:
        raise RuntimeError("ASSIGNMENT_URL is not configured")

    response = requests.get(ASSIGNMENT_URL, timeout=8)
    response.raise_for_status()
    return response.json()


def find_records(data):
    """Find a list of order-like records in JSON."""
    if isinstance(data, list):
        if all(isinstance(x, dict) for x in data):
            return data
        for item in data:
            result = find_records(item)
            if result is not None:
                return result

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                result = find_records(value)
                if result is not None:
                    return result
        for value in data.values():
            result = find_records(value)
            if result is not None:
                return result

    return None


def parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def answer_question(question, records):
    q = question.lower()

    # Handle "How many orders from South were refunded in April 2026?"
    if (
        "how many" in q
        and "order" in q
        and "refund" in q
        and "south" in q
        and "april 2026" in q
    ):
        count = 0

        for order in records:
            region = str(order.get("region", "")).lower()
            status = str(order.get("status", "")).lower()

            refund_date = (
                order.get("refund_date")
                or order.get("refunded_at")
            )
            date = parse_date(refund_date)

            refunded = (
                "refund" in status
                or order.get("refunded") is True
                or order.get("is_refunded") is True
                or bool(refund_date)
            )

            if (
                region == "south"
                and refunded
                and date is not None
                and date.year == 2026
                and date.month == 4
            ):
                count += 1

        return count

    raise ValueError(
        "This question type is not implemented yet. "
        "Inspect the API schema and add the appropriate calculation."
    )


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/")
def ask(data: Question):
    try:
        payload = fetch_data()
        records = find_records(payload)

        if records is None:
            raise ValueError(
                "The configured URL did not return a recognizable "
                "list of records. Inspect its JSON response."
            )

        answer = answer_question(data.question, records)
        return {"answer": answer}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
