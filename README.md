# IMEI.info API v5 Python SDK 🐍

[![PyPI version](https://img.shields.io/pypi/v/imei-info.svg?style=flat-square)](https://pypi.org/project/imei-info/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?style=flat-square)](https://pypi.org/project/imei-info/)

The official, modern, fully typed Python client library for the **IMEI.info API v5** — the ultimate global **IMEI checker API** for developers.

Integrate the high-performance **IMEI check API** into your Python backend, Django/FastAPI web services, trade-in systems, or wholesale ERP solutions. Perform instant **IMEI check** and **IMEI lookup** requests to fetch comprehensive mobile device data from our global **TAC (Type Allocation Code)** catalog and **TAC database**. Retrieve real-time **blacklist check** details, check complete **blacklist status (carrier lock, phone block)**, verify Find My iPhone **iCloud check** states, and identify **FRP bypass status (Google Factory Reset Protection)** to secure your trade-in and recycling pipelines.

---

## ⚡ Supported IMEI Check API Features & Services

* **Dual Client Design**: `ImeiClient` for sync environments, `AsyncImeiClient` for highly efficient async applications.
* **Instant Blacklist & Carrier Verification**: Query global databases to check GSMA status, perform a **blacklist check** or discover a device's exact **blacklist status (carrier lock, phone block)**.
* **Apple & Android Security Lock Checking**: Instantly execute an **iCloud check** to find Find My iPhone status, or verify **FRP bypass status (Google Factory Reset Protection)** to prevent locked device trade-ins.
* **TAC Identification**: Match device model names, brands, and technical specs automatically from the official **TAC database**.
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

## Postman Collection

Prefer testing requests before writing code?

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://god.gw.postman.com/run-collection/55865585-498f1c10-3c55-4d01-9062-256e7a99e8cc?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D55865585-498f1c10-3c55-4d01-9062-256e7a99e8cc%26entityType%3Dcollection%26workspaceId%3D1f90c16b-0b90-404a-bff7-ff4035dbccf8#?env%5BIMEI.info%20API%20v5%5D=W3sia2V5IjoiYmFzZV91cmwiLCJ2YWx1ZSI6Imh0dHBzOi8vZGFzaC5pbWVpLmluZm8vYXBpIiwidHlwZSI6ImRlZmF1bHQiLCJlbmFibGVkIjp0cnVlfSx7ImtleSI6IkFQSV9LRVkiLCJ2YWx1ZSI6IiIsInR5cGUiOiJzZWNyZXQiLCJlbmFibGVkIjp0cnVlfSx7ImtleSI6InNlcnZpY2VfaWQiLCJ2YWx1ZSI6IjAiLCJ0eXBlIjoiZGVmYXVsdCIsImVuYWJsZWQiOnRydWV9LHsia2V5IjoicmVzdWx0X2lkIiwidmFsdWUiOiIiLCJ0eXBlIjoiZGVmYXVsdCIsImVuYWJsZWQiOnRydWV9LHsia2V5IjoiYnVsa19yZXN1bHRfaWQiLCJ2YWx1ZSI6IiIsInR5cGUiOiJkZWZhdWx0IiwiZW5hYmxlZCI6dHJ1ZX1d)


Licensed under the MIT License. Developed and maintained by the IMEI.info Team.
