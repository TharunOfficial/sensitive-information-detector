import re
import pytesseract
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from PIL import Image
import os

# Define patterns for various IDs
patterns = {
    # Individuals
    'Aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b',
    'PAN': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    'Voter ID (EPIC)': r'\b[A-Z]{3}[0-9]{7}\b',
    'Passport': r'\b[A-Z]{1}[0-9]{7}\b',
    'Driving License': r'\b[A-Z]{2}\d{2}\s\d{4}\s\d{7}\b',
    'Ration Card': r'\b[A-Z0-9]{10,}\b',
    'Birth Certificate': r'\b[A-Z0-9]{10,}\b',
    'Marriage Certificate': r'\b[A-Z0-9]{10,}\b',
    'NPR (National Population Register)': r'\b\d{3}\s\d{3}\s\d{3}\s\d{3}\b',
    'ESIC': r'\b\d{10}\b',
    
    # Businesses
    'GSTIN': r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b',
    'CIN': r'\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b',
    'TAN': r'\b[A-Z]{4}[0-9]{5}[A-Z]{1}\b',
    'Udyog Aadhaar': r'\b[U][A-Z0-9]{12}\b',
    'IEC': r'\b\d{10}\b',
    'TIN': r'\b\d{11}\b',
    'EPFO Establishment Code': r'\b\d{2}[A-Z]{1}[A-Z0-9]{7}\b',
    'LLPIN': r'\b[A-Z]{3}-\d{4}\b',
    'Professional Tax Registration': r'\b[A-Z0-9]{15}\b',
    'Trademark Registration Number': r'\b[A-Z0-9]{7,8}\b'
}

# Function to check text against patterns
def check_sensitive_data(text):
    alerts = []
    for id_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            alerts.append(f"{id_type} detected: {', '.join(matches)}")
    return alerts

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Function to extract text from image using OCR
def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to process files
def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    if file_extension == '.pdf':
        extracted_text = extract_pdf_text(file_path)
    elif file_extension == '.docx':
        extracted_text = extract_text_from_docx(file_path)
    elif file_extension in ['.jpeg', '.jpg', '.png']:
        extracted_text = extract_text_from_image(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return []

    return check_sensitive_data(extracted_text)

# Example Usage
file_path = 'idproof.jpg'  # replace with your file path

alerts = process_file(file_path)
if alerts:
    for alert in alerts:
        print(alert)
else:
    print("No sensitive data detected.")
