# Exhibit P OCR integration

This branch adds receipt text extraction with Tesseract. OCR reads text only and does not authenticate payment.

Install Python requirements and the Tesseract OCR command-line executable separately. Then run `python -m database.seed`, `python -m pytest -q`, and `python app.py`.

Receipt screenshots must be authorised or synthetic. Synthetic ledger matches are never proof of funds received.
