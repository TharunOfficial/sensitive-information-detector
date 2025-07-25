# Sensitive Information Detector & Redactor

This project was developed as part of the **Smart India Hackathon (SIH) 2024**, aimed at building an automated solution to detect and redact sensitive Personally Identifiable Information (PII) from documents.

A Python-based tool to detect sensitive information (PII, document IDs, etc.) in PDF and image documents, and automatically redact (blank out) the detected information using a black overlay.

## Features

- Extracts text from PDF, JPG, PNG, and other image formats using OCR.
- Detects sensitive data patterns like:
  - Aadhaar Numbers
  - PAN Cards
  - Ration Cards
  - Birth/Marriage Certificates
  - Custom Regex-based patterns
- Automatically blanks out (redacts) sensitive information with a black overlay.
- Outputs a redacted image or PDF file with sensitive data obscured.
- Simple web-based UI using Flask.

## Prerequisites

- Python 3.x
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure **Tesseract OCR** is installed and accessible.

## Usage

### 1. Run the Web Application

Start the Flask web server:

````bash
python3 app.py
```python
patterns = {
    'Aadhaar': r"\b\d{4}\s\d{4}\s\d{4}\b",
    'PAN': r"[A-Z]{5}[0-9]{4}[A-Z]",
    'RationCard': r"\b[0-9]{10}\b",
    'BirthCertificate': r"BIRTH CERTIFICATE",
    'MarriageCertificate': r"MARRIAGE CERTIFICATE"
    ......
    ......
    ......
    ......
}
````

### 2. Launch the Web Interface

Run the Flask web app:

```bash
python3 app.py

```



## Example Output

- Sensitive data in documents will be blanked out with a black rectangle overlay.
- The output file will be saved as a redacted copy.



## requirements.txt

```
pytesseract
pdf2image
opencv-python
Flask
Pillow
```

## License

MIT License

## Disclaimer

Use responsibly. This tool is designed for privacy protection, compliance, and ethical data handling purposes.

