# EXHIBIT P

**Intelligent Payment Receipt Integrity Assessment**

*Evidence. Integrity. Verification.*

## 1. Overview

Exhibit P is a proof-of-concept payment verification system designed to assess the integrity of payment information and identify discrepancies between submitted payment details and transaction records.

The project explores how businesses can reduce exposure to fraudulent, altered, duplicated, or unverified payment receipts.

The current PoC uses a simulated transaction ledger to demonstrate payment verification.

## 2. Problem Statement

Businesses that rely on screenshots and manually submitted payment receipts can face risks including:

- Forged or manipulated payment receipts.
- Incorrect transaction references.
- Amount and currency discrepancies.
- Payments that are pending rather than settled.
- Reuse of previously submitted payment evidence.

A receipt image alone does not establish that a payment has successfully reached the intended recipient.

## 3. Current PoC Features

- Flask-based web interface.
- SQLite transaction database.
- Transaction-reference lookup.
- Amount verification.
- Currency verification.
- Merchant identification checks.
- Payment settlement-status checks.
- Input validation.
- Automated verification tests.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Flask | Web application |
| SQLite | Simulated transaction ledger |
| HTML | User interface |
| CSS | Interface styling |
| JavaScript | Frontend functionality |
| Pytest | Automated testing |

## 5. System Architecture

The current verification workflow:

1. User submits payment information.
2. Flask receives and validates the submitted fields.
3. The verification engine queries the SQLite transaction ledger.
4. The system checks the reference, amount, currency, merchant and settlement status.
5. The application returns a verification result.

## 6. Verification Results

| Result | Meaning |
|---|---|
| RECORD_MATCHED | Submitted details match a settled ledger record |
| UNVERIFIED | No unique matching transaction was found |
| NOT_SETTLED | The transaction has not settled |
| MISMATCH | One or more payment details do not match |
| INVALID_INPUT | Submitted information is incomplete or invalid |

**Important:** `RECORD_MATCHED` means the submitted details match the demonstration ledger. It does not establish independent confirmation from a live financial institution.

## 7. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- Visual Studio Code (recommended).

### Clone the repository

```bash
git clone https://github.com/Stephan-y44/Exhibit-P.git
cd Exhibit-P
```

### Create a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Initialize and seed the database

```powershell
python -m database.seed
```

### Run the application

```powershell
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000/
```

## 8. Demonstration Transactions

Use these sample records to test the application.

| Reference | Amount | Currency | Merchant ID |
|---|---:|---|---|
| KE-DEMO-000241 | 2500.00 | KES | TEST-MERCHANT-001 |
| NG-DEMO-000242 | 42500.00 | NGN | TEST-MERCHANT-002 |
| KE-DEMO-000243 | 7500.00 | KES | TEST-MERCHANT-001 |

The third transaction should return `NOT_SETTLED`.

## 9. Running Tests

Run:

```powershell
python -m pytest -v
```

The tests cover successful verification, pending transactions, unknown references, amount mismatches, merchant mismatches, currency mismatches and invalid amounts.

## 10. Current Limitations

This is an early-stage proof of concept.

The current implementation does not yet include:

- Receipt image OCR extraction.
- AI-based fraud classification.
- Image manipulation detection.
- Live M-Pesa Daraja API integration.
- Independent bank or payment-provider confirmation.
- Production-grade authentication and authorization.

These capabilities are potential areas for subsequent development and must be validated before being presented as implemented features.

## 11. Development Roadmap

**Week 3 — Proof of Concept**
- Demonstrate transaction verification using a simulated ledger.
- Validate core verification logic.
- Test the application.

**Week 4 — Prototype**
- Develop receipt-image processing.
- Explore OCR-based information extraction.
- Introduce integrity assessment.
- Evaluate integration with authorized payment-provider data.

## 12. Security and Privacy

Exhibit P is being developed with attention to payment-data integrity and responsible handling of sensitive information.

Demonstration data should be synthetic. Real transaction receipts and financial statements must not be uploaded or shared without appropriate authorization, consent and data protection safeguards.

## 13. Project Status

**Current stage:** Proof of Concept (PoC).

**Repository:** https://github.com/Stephan-y44/Exhibit-P

---

*EXHIBIT P — Evidence. Integrity. Verification.*