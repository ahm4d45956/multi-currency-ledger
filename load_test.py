import requests
import threading
import time
from decimal import Decimal

BASE_URL = "http://localhost:8000"


def deposit(account_id, amount):
    response = requests.post(
        f"{BASE_URL}/deposit",
        json={
            "account_id": account_id,
            "amount": float(amount)
        }
    )
    return response


def run_test():
    print("Creating account...")

    response = requests.post(
        f"{BASE_URL}/accounts",
        json={
            "user_id": 1,
            "currency": "USD"
        }
    )

    print("Status:", response.status_code)
    print("Raw response:", response.text)

    account_id = response.json()["account_id"]

    print("Depositing initial 1000...")

    requests.post(
        f"{BASE_URL}/deposit",
        json={
            "account_id": account_id,
            "amount": 1000
        }
    )

    print("Running 100 concurrent deposits...")

    threads = []
    start_time = time.time()

    for _ in range(100):
        t = threading.Thread(target=deposit, args=(account_id, 1))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    response = requests.get(f"{BASE_URL}/balance/{account_id}")

    print("Final balance status:", response.status_code)
    print("Final balance raw:", response.text)

    final_balance = Decimal(response.json()["balance"])
    expected = Decimal("1100")

    print("\nLoad test completed.")
    print("Total time:", round(end_time - start_time, 3), "seconds")
    print("Expected balance:", expected)
    print("Final balance:", final_balance)

    if final_balance == expected:
        print("SUCCESS: No race condition detected.")
    else:
        print("FAILURE: Race condition detected.")


if __name__ == "__main__":
    run_test()
