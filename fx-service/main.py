from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class FXRequest(BaseModel):
    amount: float
    rate: float
    spread: float = 0.01

@app.post("/convert")
def convert_fx(data: FXRequest):
    adjusted_rate = data.rate * (1 + data.spread)
    converted = data.amount * adjusted_rate
    return {
        "converted_amount": converted,
        "applied_rate": adjusted_rate
    }

@app.get("/health")
def health():
    return {"status": "fx-service running"}
