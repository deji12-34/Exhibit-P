"""Independent OCR page; does not change the teammate's verification views."""
from flask import Blueprint, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from ocr.extractor import OCRUnavailableError, ReceiptImageError, extract_receipt

ocr_bp = Blueprint("ocr", __name__, template_folder="templates")


@ocr_bp.route("/ocr", methods=["GET", "POST"])
def scan_receipt():
    scan = None
    status = 200
    if request.method == "POST":
        upload = request.files.get("receipt")
        if upload is None or not upload.filename:
            scan = {"error": "Please choose a receipt image."}
            status = 400
        else:
            try:
                scan = extract_receipt(upload.read(5 * 1024 * 1024 + 1))
            except (ReceiptImageError, OCRUnavailableError) as exc:
                scan = {"error": str(exc)}
                status = 400
    return render_template("ocr/scan.html", scan=scan), status


@ocr_bp.errorhandler(RequestEntityTooLarge)
def too_large(_exc):
    return render_template(
        "ocr/scan.html",
        scan={"error": "Image is too large. Upload a PNG or JPEG under 5 MB."},
    ), 413
