from fastapi import FastAPI

app = FastAPI()

@app.post("/record")
def record_fee(amount: float):
    return {"recorded_fee": amount}

@app.get("/health")
def health():
    return {"status": "revenue-service running"}
