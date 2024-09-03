import cv2
import pytesseract
import numpy as np
import re
from pdf2image import convert_from_path

# Define patterns for various IDs
patterns = {
    'DOB': r'\b(?:0[1-9]|[12][0-9]|3[01])[-/](?:0[1-9]|1[0-2])[-/](?:19|20)\d{2}\b',
    'Aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b',
    'PAN': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    'Voter ID (EPIC)': r'\b[A-Z]{3}[0-9]{7}\b',
    'Passport': r'\b[A-Z]{1}[0-9]{7}\b',
    'Driving License': r'\b[A-Z]{2}\d{2}\s\d{4}\s\d{7}\b',
    'Ration Card': r'\b[A-Z0-9]{10,}\b',
    'Birth Certificate': r'\b[A-Z0-9]{10,}\b',
    'Marriage Certificate': r'\b[A-Z0-9]{10,}\b',
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

# Function to preprocess the image for better OCR
def preprocess_image_for_ocr(image):
    # Convert to grayscale for OCR purposes only
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    # Dilation to make the text thicker
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    return dilated

# Function to extract text from image using pytesseract
def extract_text_from_image(image):
    preprocessed_image = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(preprocessed_image)
    return text

# Function to hide sensitive text with black rectangles in the original image
def blur_sensitive_text_in_image(image, sensitive_data):
    h, w = image.shape[:2]
    boxes = pytesseract.image_to_boxes(image)

    for box in boxes.splitlines():
        b = box.split()
        x, y, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        word = b[0]
        
        for label, value in sensitive_data:
            if word in value:
                cv2.rectangle(image, (x, h-y2), (x2, h-y), (0, 0, 0), -1)
                print(f"Blurring {value}")

    return image

# Function to process images within a PDF
def process_pdf_with_images(file_path):
    images = convert_from_path(file_path)
    for i, image in enumerate(images):
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR format
        
        text = extract_text_from_image(open_cv_image)
        sensitive_data = check_sensitive_data(text)
        
        if sensitive_data:
            for data in sensitive_data:
                print(f"Detected: {data}")
            
            blurred_image = blur_sensitive_text_in_image(open_cv_image, sensitive_data)
            hidden_image_path = f"blurred_page_{i+1}.jpeg"
            cv2.imwrite(hidden_image_path, blurred_image)
            print(f"Hidden image saved as: {hidden_image_path}")
        else:
            print(f"No sensitive data detected on page {i+1}")

# Example usage
file_path = 'idproof.pdf'  # Replace with your file path
process_pdf_with_images(file_path)

