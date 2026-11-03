# OCR page (separate from the original homepage)

The teammate's original homepage and verification handler remain intact.
The OCR contribution now lives at /ocr, and its extractor stays in ocr/extractor.py.

## Run the website

Install the Python packages with: python -m pip install -r requirements.txt
Install the Tesseract OCR executable separately and make it available on PATH.
Run python -m database.seed and python app.py, then visit:

- http://127.0.0.1:5000/ — original verification homepage
- http://127.0.0.1:5000/ocr — independent receipt scanner

Do not open templates/index.html directly or launch it with VS Code Live Server.
Jinja variables render only when the page is served through Flask.

OCR reads text from an image; it does not authenticate a payment.
The verification ledger is simulated, not a bank/payment-provider settlement check.
