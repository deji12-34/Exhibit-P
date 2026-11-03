// Cosmetic only. OCR runs on the Flask server, not in the browser.
const input = document.getElementById('receipt');
const label = document.getElementById('upload-label');
if (input && label) {
  input.addEventListener('change', () => {
    label.textContent = input.files.length ? input.files[0].name : 'Choose a payment receipt';
  });
}
