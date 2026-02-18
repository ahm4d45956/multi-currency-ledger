import os
import logging
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Database configuration from environment
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "ledger"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# ---------- Models ----------

class CreateAccountRequest(BaseModel):
    user_id: int
    currency: str


class DepositRequest(BaseModel):
    account_id: int
    amount: Decimal

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal   


# ---------- Global Exception Handler ----------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ---------- DB Connection ----------

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database unavailable")


# ---------- Health Check ----------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Create Account ----------

@app.post("/accounts")
def create_account(data: CreateAccountRequest):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO accounts (user_id, currency, balance)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (data.user_id, data.currency, Decimal("0.00"))
        )

        account_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        logger.info(f"Account created: {account_id}")

        return {"account_id": account_id}

    except Exception as e:
        logger.error(f"Create account failed: {e}")
        raise HTTPException(status_code=500, detail="Account creation failed")


# ---------- Deposit (ACID Safe) ----------

@app.post("/deposit")
def deposit(data: DepositRequest):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Lock row for safe concurrent updates
        cur.execute(
            "SELECT balance FROM accounts WHERE id = %s FOR UPDATE",
            (data.account_id,)
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Account not found")

        current_balance = row[0]
        new_balance = current_balance + data.amount

        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            (new_balance, data.account_id)
        )

        conn.commit()

        cur.close()
        conn.close()

        logger.info(
            f"Deposit successful: account={data.account_id}, amount={data.amount}"
        )

        return {"new_balance": str(new_balance)}

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Deposit failed: {e}")
        raise HTTPException(status_code=500, detail="Transaction failed")
#------------------Transfer-------------------


@app.post("/transfer")
def transfer(data: TransferRequest):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    conn = get_connection()
    try:
        conn.autocommit = False
        cur = conn.cursor()

# Always lock in ID order to avoid deadlocks
        first_id = min(data.from_account_id, data.to_account_id)
        second_id = max(data.from_account_id, data.to_account_id)

        cur.execute(
            "SELECT id, balance FROM accounts WHERE id IN (%s, %s) FOR UPDATE",
            (first_id, second_id)
        )

        rows = cur.fetchall()

        if len(rows) != 2:
            raise HTTPException(status_code=404, detail="One or both accounts not found")

        balances = {row[0]: row[1] for row in rows}

        from_balance = balances.get(data.from_account_id)
        to_balance = balances.get(data.to_account_id)

        if from_balance is None or to_balance is None:
            raise HTTPException(status_code=404, detail="Account mismatch")

        if from_balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        new_from_balance = from_balance - data.amount
        new_to_balance = to_balance + data.amount

        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            (new_from_balance, data.from_account_id)
        )

        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            (new_to_balance, data.to_account_id)
        )

        conn.commit()

        return {
            "status": "success",
            "from_account_new_balance": str(new_from_balance),
            "to_account_new_balance": str(new_to_balance)
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()


# ---------- Get Balance ----------

@app.get("/balance/{account_id}")
def get_balance(account_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT balance FROM accounts WHERE id = %s",
            (account_id,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Account not found")

        return {"balance": str(row[0])}

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Balance fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Balance retrieval failed")
