import requests
import threading
import time
from decimal import Decimal

BASE_URL = "http://localhost:8000"


def deposit(account_id, amount):
    r = requests.post(
        f"{BASE_URL}/deposit",
        json={"account_id": account_id, "amount": amount}
    )
    if r.status_code != 200:
        print("Error:", r.text)


def run_test():
    print("Creating account...")

    response = requests.post(
        f"{BASE_URL}/accounts",
        json={
            "user_id": "load_test_user",
            "currency": "USD"
        }
    )

    print("Status:", response.status_code)
    print("Raw response:", response.text)

    account_id = response.json()["account_id"]

    print("Depositing initial 1000...")

    requests.post(
        f"{BASE_URL}/deposit",
        json={"account_id": account_id, "amount": 1000}
    )

    threads = []
    start = time.time()

    print("Running 100 concurrent deposits...")

    for _ in range(100):
        t = threading.Thread(
            target=deposit,
            args=(account_id, 1)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()

    # Fetch final balance
    response = requests.get(f"{BASE_URL}/accounts/{account_id}")
    final_balance = Decimal(response.json()["balance"])
    expected = Decimal("1100")

    print("\nLoad test completed.")
    print("Total time:", round(end - start, 3), "seconds")
    print("Final balance:", final_balance)
    print("Expected balance:", expected)

    if final_balance != expected:
        print("❌ Race condition detected")
    else:
        print("✅ Concurrency safe")


if __name__ == "__main__":
    run_test()

