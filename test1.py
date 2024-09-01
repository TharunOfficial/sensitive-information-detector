import re
import pytesseract
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from PIL import Image, ImageFilter
import cv2
import numpy as np
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
    detected_data = []
    for id_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            detected_data.append((id_type, match))
    return detected_data

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Function to extract text from image using OCR and apply blur filter
def extract_and_blur_text_from_image(file_path):
    image = cv2.imread(file_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text_data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)

    for i, word in enumerate(text_data['text']):
        for id_type, pattern in patterns.items():
            if re.match(pattern, word):
                # Get bounding box coordinates
                (x, y, w, h) = (text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i])
                
                # Apply blur to the area of detected sensitive information
                roi = image[y:y+h, x:x+w]
                blurred_roi = cv2.GaussianBlur(roi, (51, 51), 0)
                image[y:y+h, x:x+w] = blurred_roi

                print(f"{id_type} detected and blurred: {word}")

    # Save the modified image
    blurred_image_path = f"blurred_{os.path.basename(file_path)}"
    cv2.imwrite(blurred_image_path, image)
    return blurred_image_path

# Function to process files
def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    extracted_text = ""
    alerts = []

    if file_extension == '.pdf':
        extracted_text = extract_pdf_text(file_path)
        alerts = check_sensitive_data(extracted_text)
    elif file_extension == '.docx':
        extracted_text = extract_text_from_docx(file_path)
        alerts = check_sensitive_data(extracted_text)
    elif file_extension in ['.jpeg', '.jpg', '.png']:
        blurred_image_path = extract_and_blur_text_from_image(file_path)
        print(f"Blurred image saved to: {blurred_image_path}")
    else:
        print(f"Unsupported file format: {file_extension}")
        return

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No sensitive data detected.")

# Example Usage
file_path = 'idproof.jpg'  # replace with your file path
process_file(file_path)
