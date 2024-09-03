import re
import cv2
import pytesseract
import numpy as np

# Define patterns for various IDs
patterns = {
    # Date of Birth (Multiple formats)
    'DOB': r'\b(?:0[1-9]|[12][0-9]|3[01])[-/](?:0[1-9]|1[0-2])[-/](?:19|20)\d{2}\b',

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
    
    # Refined Trademark Registration Number (with optional prefix, typically 7-8 alphanumeric)
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

# Function to extract text from image using pytesseract
def extract_text_from_image(file_path):
    """Extract text from an image file."""
    image = cv2.imread(file_path)
    if image is None:
        raise FileNotFoundError(f"Error loading image: {file_path}")
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_image)
    data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
    return image,data,text

# Function to hide sensitive text with black rectangles in the image
def blur_sensitive_text_in_image(image, sensitive_data):
    h, w = image.shape[:2]
    boxes = pytesseract.image_to_boxes(image)

    for box in boxes.splitlines():
        b = box.split()
        x, y, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        word = b[0]
        
        for label, value in sensitive_data:
            
            if word in value or label:
                cv2.rectangle(image, (x, h-y2), (x2, h-y), (0, 0, 0), -1)

    return image



file_path = 'idproof.jpeg' 
image ,data,text= extract_text_from_image(file_path)
sensitive_data = check_sensitive_data(text)
if sensitive_data:
    for data in sensitive_data:
        print(f"Detected: {data}")
    
    blurred_image = blur_sensitive_text_in_image(image, sensitive_data)
    hidden_image_path = 'blurred_idproof.jpeg'
    cv2.imwrite(hidden_image_path, blurred_image)
    print(f"Hidden image saved as: {hidden_image_path}")
else:
    print("No sensitive data detected.")
