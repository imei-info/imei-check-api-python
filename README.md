# IMEI.info API v5 Python SDK 🐍

[![PyPI version](https://img.shields.io/pypi/v/imei-info.svg?style=flat-square)](https://pypi.org/project/imei-info/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square)](https://pypi.org/project/imei-info/)

The official, modern, fully typed Python client library for the **IMEI.info API v5**. 

This SDK supports both **synchronous** and **asynchronous** requests using `httpx`, provides 100% type safety via Python type-hints, and implements structured exception handling for quick integration and high reliability.

---

## ⚡ Features

* **Dual Client Design**: `ImeiClient` for sync environments, `AsyncImeiClient` for highly efficient async applications.
* **100% Type-Safe**: Fully typed data models (`ImeiCheckResponse`) and Enums.
* **Structured Exceptions**: Specific Python classes for API errors:
  * `ImeiAuthenticationError` (HTTP 401 — Invalid API key)
  * `ImeiInsufficientCreditsError` (HTTP 402 — Out of API credits)
  * `ImeiValidationError` (HTTP 422 — Invalid Luhn checksum)
  * `ImeiRateLimitError` (HTTP 429 — Rate limits reached)
* **API Sandbox Support**: Easily switch to local mock servers or the official IMEI.info sandbox environment.

---

## 📥 Installation

Install the library using `pip`:

```bash
pip install imei-info
```

---

## 🚀 Quick Start Guide

Before making requests, make sure you have your secure API token. You can generate one in your developer dashboard at **[dash.imei.info](https://dash.imei.info)**.

### 🔹 1. Synchronous Example (Simple Scripts & Cron Jobs)

```python
from imei_info import ImeiClient
from imei_info.exceptions import ImeiInsufficientCreditsError, ImeiValidationError

# Initialize the client with your Bearer Token
client = ImeiClient(token="YOUR_API_TOKEN")

try:
    # Query IMEI details
    report = client.check_imei("353541326469521")
    
    print(f"Device: {report.brand} {report.model}")
    print(f"Blacklist Status: {report.blacklist_status.value}") # "CLEAN" or "BLACKLISTED"
    print(f"Carrier Lock: {report.carrier_lock}")
    print(f"Original Carrier: {report.original_carrier}")
    print(f"Purchase Country: {report.purchase_country}")
    
    if report.specifications:
        print(f"CPU: {report.specifications.cpu} | RAM: {report.specifications.ram_gb}GB")

except ImeiInsufficientCreditsError:
    print("Error: Out of API lookup credits! Please top up at dash.imei.info.")
except ImeiValidationError as e:
    print(f"Error: Invalid IMEI checksum. Details: {e.message}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    client.close()
```

### 🔹 2. Asynchronous Example (FastAPI, Tornado, Asyncio)

```python
import asyncio
from imei_info import AsyncImeiClient
from imei_info.exceptions import ImeiError

async def main():
    async with AsyncImeiClient(token="YOUR_API_TOKEN") as client:
        try:
            report = await client.check_imei("353541326469521")
            print(f"Async Result: {report.brand} {report.model} - Status: {report.blacklist_status.value}")
        except ImeiError as e:
            print(f"API Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 Testing with the Sandbox

To test your integration without consuming your API lookup credits, use one of our official sandbox test IMEI numbers:

* `353541326469521` — Returns Apple iPhone 12 Pro Max specs (Status: `CLEAN`).
* `350545260771498` — Returns Samsung Galaxy S24 Ultra specs (Status: `CLEAN`).
* `355030794352540` — Returns Google Pixel 8 Pro specs (Status: `BLACKLISTED` / stolen).
* Any other IMEI — Simulates a `402 Payment Required` (credits exhausted) response in Sandbox mode.

---

## 📈 Strategic Integration & Support

* **Documentation Portal**: [https://www.imei.info/api/imei/docs/](https://www.imei.info/api/imei/docs/)
* **Interactive OpenAPI Specs**: [https://dash.imei.info/swagger/](https://dash.imei.info/swagger/)
* **Developer Panel**: [dash.imei.info](https://dash.imei.info)
* **Support Contact**: [api@imei.info](mailto:api@imei.info)

Licensed under the MIT License. Developed and maintained by the IMEI.info Team.
