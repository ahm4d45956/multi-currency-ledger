from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from decimal import Decimal
import logging
import json
import time

app = FastAPI()

# ---------------------------
# Database Configuration
# ---------------------------

DB_CONFIG = {
    "host": "postgres",
    "dbname": "ledger",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ---------------------------
# Structured Logging
# ---------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ledger-service")


def log_event(event_type: str, data: dict):
    log_entry = {
        "event": event_type,
        "timestamp": time.time(),
        **data
    }
    logger.info(json.dumps(log_entry))


# ---------------------------
# Request Models
# ---------------------------

class CreateAccountRequest(BaseModel):
    user_id: str
    currency: str


class DepositRequest(BaseModel):
    account_id: int
    amount: Decimal


# ---------------------------
# Endpoints
# ---------------------------

@app.post("/accounts")
def create_account(data: CreateAccountRequest):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO accounts (user_id, currency, balance)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (data.user_id, data.currency, Decimal("0.00"))
        )

        account_id = cur.fetchone()[0]
        conn.commit()

        log_event("account_created", {
            "account_id": account_id,
            "user_id": data.user_id,
            "currency": data.currency
        })

        return {"account_id": account_id}

    finally:
        cur.close()
        conn.close()


@app.post("/deposit")
def deposit(data: DepositRequest):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Row-level locking
        cur.execute(
            "SELECT balance FROM accounts WHERE id = %s FOR UPDATE;",
            (data.account_id,)
        )

        row = cur.fetchone()
        if not row:
            return {"error": "Account not found"}

        current_balance = row[0]
        amount = Decimal(str(data.amount))
        new_balance = current_balance + amount

        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s;",
            (new_balance, data.account_id)
        )

        conn.commit()

        log_event("deposit", {
            "account_id": data.account_id,
            "amount": str(amount),
            "new_balance": str(new_balance)
        })

        return {"new_balance": str(new_balance)}

    finally:
        cur.close()
        conn.close()


@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT id, user_id, currency, balance FROM accounts WHERE id = %s;",
            (account_id,)
        )
        row = cur.fetchone()

        if not row:
            return {"error": "Account not found"}

        return {
            "account_id": row[0],
            "user_id": row[1],
            "currency": row[2],
            "balance": str(row[3])
        }

    finally:
        cur.close()
        conn.close()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def readiness():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}

