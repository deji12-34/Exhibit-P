"""Local, non-authenticating OCR for receipt images.

Results are claims extracted from pixels, not evidence of settlement.
Uploaded image bytes are processed in memory and never persisted here.
"""
from __future__ import annotations

import io
import re
from decimal import Decimal, InvalidOperation

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 12_000_000
SUPPORTED_FORMATS = {"PNG", "JPEG"}


class ReceiptImageError(ValueError):
    """An uploaded receipt is invalid or exceeds demo safety limits."""


class OCRUnavailableError(RuntimeError):
    """The local Tesseract executable could not be used."""


def open_receipt(content: bytes) -> Image.Image:
    if not content:
        raise ReceiptImageError("Select a PNG or JPEG receipt image.")
    if len(content) > MAX_IMAGE_BYTES:
        raise ReceiptImageError("Receipt image exceeds the 5 MB size limit.")
    try:
        with Image.open(io.BytesIO(content)) as check:
            if check.format not in SUPPORTED_FORMATS:
                raise ReceiptImageError("Only valid PNG and JPEG images are supported.")
            if check.width * check.height > MAX_PIXELS:
                raise ReceiptImageError("Image dimensions are too large (12 megapixel limit).")
            check.verify()
        with Image.open(io.BytesIO(content)) as image:
            image = ImageOps.exif_transpose(image)
            image.load()
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ReceiptImageError("The file is not a readable PNG or JPEG image.") from exc


def _currency_from(text: str) -> str:
    if re.search(r"(?i)(?:\bKES\b|\bKSH(?:S)?\.?\b|\bKSH\b)", text):
        return "KES"
    if re.search(r"(?i)\bNGN\b|₦|\bNAIRA\b", text):
        return "NGN"
    if re.search(r"(?i)\bUSD\b|\bUS\s*DOLLARS?\b|\$", text):
        return "USD"
    return ""


def _parse_amount(fragment: str) -> str:
    # Avoid guessing regional separators or negative amounts.
    pattern = r"(?<![\w.-])(?:₦|\$|NGN\s*|KES\s*|KSH\.?\s*|USD\s*)?\s*(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d{1,10}(?:\.\d{1,2})?)(?![\w.-])"
    candidates = re.findall(pattern, fragment, flags=re.I)
    for candidate in candidates:
        try:
            amount = Decimal(candidate.replace(",", ""))
        except InvalidOperation:
            continue
        if amount > 0 and amount.is_finite():
            return f"{amount:.2f}"
    return ""


def _extract_reference(lines: list[str]) -> str:
    labels = re.compile(
        r"(?i)\b(?:transaction\s*(?:reference|ref|id)|payment\s*(?:reference|ref|id)|"
        r"reference(?:\s*(?:no\.?|number|id))?|ref(?:\s*(?:no\.?|number|id))?|"
        r"transaction\s*no\.?)\b\s*[:#=\-]?\s*([A-Z0-9][A-Z0-9/_-]{5,63})\b"
    )
    for line in lines:
        m = labels.search(line)
        if m:
            return m.group(1).strip("-_/.").upper()
    # Explicit demonstration IDs only; generic digit strings are unreliable.
    match = re.search(r"(?i)\b(?:KE|NG)-DEMO-\d{4,}\b", "\n".join(lines))
    return match.group(0).upper() if match else ""


def _extract_merchant(lines: list[str]) -> str:
    pattern = re.compile(
        r"(?i)\b(?:merchant\s*id|recipient\s*(?:id|tag)|payee\s*id)\b\s*[:#=\-]?\s*([A-Z0-9][A-Z0-9/_-]{2,63})\b"
    )
    for line in lines:
        match = pattern.search(line)
        if match:
            return match.group(1).strip("-_/.").upper()
    return ""


def parse_receipt_text(text: str) -> dict:
    """Extract candidate fields from text; never authenticate a payment."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    complete = "\n".join(lines)
    currency = _currency_from(complete)
    amount = ""
    for line in lines:
        if re.search(r"(?i)\b(?:amount|total|paid|sent|transferred)\b", line):
            part = re.split(
                r"(?i)\b(?:amount|total|paid|sent|transferred)\b\s*[:=-]?",
                line, maxsplit=1
            )[-1]
            amount = _parse_amount(part)
            if amount:
                currency = _currency_from(line) or currency
                break
    if not amount:
        for line in lines:
            if _currency_from(line):
                amount = _parse_amount(line)
                if amount:
                    break

    status = ""
    match = re.search(
        r"(?im)\b(?:payment\s*)?status\s*[:=-]?\s*(successful|success|completed|settled|pending|failed)\b",
        complete
    )
    if match:
        status = match.group(1).upper()
    elif re.search(r"(?i)\bpayment\s+(?:successful|completed|pending|failed)\b", complete):
        status = re.search(r"(?i)\bpayment\s+(successful|completed|pending|failed)\b", complete).group(1).upper()

    fields = {
        "reference": _extract_reference(lines),
        "amount": amount,
        "currency": currency,
        "merchant_id": _extract_merchant(lines),
        "status_text": status,
    }
    warnings = []
    for key, label in (
        ("reference", "transaction reference"),
        ("amount", "payment amount"),
        ("currency", "currency"),
        ("merchant_id", "merchant ID"),
    ):
        if not fields[key]:
            warnings.append(f"Could not confidently extract {label}; enter it manually.")
    if status:
        warnings.append(
            "Receipt status is only text printed in an image, not confirmation of settlement."
        )
    return {"fields": fields, "warnings": warnings}


def extract_receipt(content: bytes) -> dict:
    """Run Tesseract, returning editable fields and OCR-quality warnings."""
    image = open_receipt(content)
    image = ImageOps.autocontrast(ImageOps.grayscale(image))
    if image.width < 1000:
        scale = min(2.0, 1000 / max(image.width, 1))
        if image.width * image.height * scale * scale <= MAX_PIXELS:
            image = image.resize((round(image.width * scale), round(image.height * scale)))
    try:
        import pytesseract
        from pytesseract import Output
        data = pytesseract.image_to_data(
            image, output_type=Output.DICT, config="--psm 6", timeout=15
        )
    except (ImportError, FileNotFoundError, OSError, RuntimeError) as exc:
        raise OCRUnavailableError(
            "OCR is unavailable. Install Tesseract OCR and the Python requirements, then retry."
        ) from exc

    lines: dict[tuple, list[str]] = {}
    confidences = []
    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue
        group = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(group, []).append(word)
        try:
            conf = float(data["conf"][i])
            if conf >= 0:
                confidences.append(conf)
        except (ValueError, TypeError):
            pass

    text = "\n".join(" ".join(words) for words in lines.values())
    parsed = parse_receipt_text(text)
    confidence = round(sum(confidences) / len(confidences), 1) if confidences else None
    if not text:
        parsed["warnings"].insert(
            0, "No readable text found. Try a clearer image or enter details manually."
        )
    elif confidence is not None and confidence < 65:
        parsed["warnings"].insert(
            0, "OCR text quality is low. Review every extracted field carefully."
        )
    return {**parsed, "raw_text": text[:4000], "average_confidence": confidence}
