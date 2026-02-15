from pydantic import BaseModel

class CreateAccount(BaseModel):
    user_id: str
    currency: str

class DepositRequest(BaseModel):
    account_id: int
    amount: float

class WithdrawRequest(BaseModel):
    account_id: int
    amount: float
