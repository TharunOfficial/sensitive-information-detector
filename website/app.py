from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from PIL import Image, ImageEnhance
import re
import cv2
import pytesseract
import numpy as np
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from docx import Document

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Define patterns for sensitive data
patterns = {
    'DOB': r'\b(?:0[1-9]|[12][0-9]|3[01])[-/](?:0[1-9]|1[0-2])[-/](?:19|20)\d{2}\b',
    'Aadhaar': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'PAN': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    'Voter ID (EPIC)': r'\b[A-Z]{3}[0-9]{7}\b',
    'Passport': r'\b[A-Z]{1}[0-9]{7}\b',
    'Driving License': r'\b[A-Z]{2}\d{2}\s\d{4}\s\d{7}\b',
    'Ration Card': r'\b[0-9]{2,4}[A-Z]{2}[0-9]{4,6}\b',  
    'Birth Certificate': r'\b(?:BC-)?[0-9]{8}\b',  
    'Marriage Certificate': r'\b(?:MC-)?[A-Z]{3}[0-9]{7}\b',
    'NPR (National Population Register)': r'\b\d{3}\s\d{3}\s\d{3}\s\d{3}\b',
    'ESIC': r'\b\d{10}\b',
    'GSTIN': r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b',
    'CIN': r'\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b',
    'TAN': r'\b[A-Z]{4}[0-9]{5}[A-Z]{1}\b',
    'Udyog Aadhaar': r'\b[U][A-Z0-9]{12}\b',
    'IEC': r'\b\d{10}\b',
    'TIN': r'\b\d{11}\b',
    'EPFO Establishment Code': r'\b\d{2}[A-Z]{1}[A-Z0-9]{7}\b',
    'LLPIN': r'\b[A-Z]{3}-\d{4}\b',
    'Professional Tax Registration': r'\b[A-Z0-9]{15}\b',
    'Name': r'\bName\s*[:\s]*[A-Za-z][A-Za-z\s]*\b',
    'Address': r'\bAddress\s*[:\s]*[A-Za-z0-9\s,.-]+\b',
    'Phone': r'\b\d{10}\b|\b\d{3}[-\s]\d{3}[-\s]\d{4}\b'
}
def pil_to_cv2(pil_image):
    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR
    return open_cv_image

# Function to resize the image
def resize_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dimensions = (width, height)
    resized_image = cv2.resize(image, dimensions, interpolation=cv2.INTER_LINEAR)
    return resized_image

# Function to enhance the image
def enhance_image(image):
    if isinstance(image, np.ndarray):  # OpenCV image
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Resize the image if it's small
    if image.size[0] < 500 or image.size[1] < 500:  # Adjust threshold as needed
        print("Image is small. Resizing...")
        image = pil_to_cv2(resize_image(pil_to_cv2(image), scale_percent=200))
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2)  # Increase contrast

    return pil_to_cv2(enhanced_image)

def preprocess_image_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    return dilated

def check_sensitive_data(text):
    detected_data = []
    for id_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            detected_data.append((id_type, match))
    return detected_data
def extract_text_from_image(image):
    enhance_image1=enhance_image(image)
    text = pytesseract.image_to_string(enhance_image1)
    return text

def extract_text_from_imagepdf(image):
    # Step 1: Enhance the image for better OCR accuracy
    enhanced_image = enhance_image(image)
    
    # Step 2: Preprocess the enhanced image
    preprocessed_image = preprocess_image_for_ocr(enhanced_image)
    
    # Step 3: Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(preprocessed_image)
    
    return text
def blur_sensitive_text_in_image(image, sensitive_data):
    h, w = image.shape[:2]
    boxes = pytesseract.image_to_boxes(image)

    for box in boxes.splitlines():
        b = box.split()
        x, y, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        word = b[0]

        for label, value in sensitive_data:
            if word in value :
                cv2.rectangle(image, (x, h-y2), (x2, h-y), (0, 0, 0), -1)
                
    return image

def process_pdf_with_images(file_path):
    images = convert_from_path(file_path)
    sensitive_data = []
    image_paths = []

    for i, image in enumerate(images):
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        
        text = extract_text_from_imagepdf(open_cv_image)
        data = check_sensitive_data(text)
        if data:
            sensitive_data.extend(data)
            blurred_image = blur_sensitive_text_in_image(open_cv_image, data)
            blurred_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'blurred_page_{i+1}.jpg')
            cv2.imwrite(blurred_image_path, blurred_image)
            image_paths.append(f'blurred_page_{i+1}.jpg')

    return sensitive_data, image_paths

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)

def process_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            sensitive_data = []
            image_paths = []

            # Handle image files
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    image = cv2.imread(file_path)
                    if image is None:
                        raise FileNotFoundError(f"Error loading image: {file_path}")
                    text = extract_text_from_image(image)
                    print(text)
                    sensitive_data = check_sensitive_data(text)
                    if sensitive_data:
                        blurred_image = blur_sensitive_text_in_image(image, sensitive_data)
                        blurred_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blurred_' + filename)
                        cv2.imwrite(blurred_image_path, blurred_image)
                        image_paths.append(f'blurred_' + filename)
                except Exception as e:
                    app.logger.error(f"Error processing image: {e}")
                    return jsonify({'error': str(e)}), 500

            # Handle PDF files
            elif filename.lower().endswith('.pdf'):
                try:
                    sensitive_data, image_paths = process_pdf_with_images(file_path)
                except Exception as e:
                    app.logger.error(f"Error processing PDF: {e}")
                    return jsonify({'error': str(e)}), 500

            # Handle DOCX files
            elif filename.lower().endswith('.docx'):
                try:
                    text = extract_text_from_docx(file_path)
                    sensitive_data = check_sensitive_data(text)
                    if sensitive_data:
                        result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename)
                        with open(result_file_path, 'w', encoding='utf-8') as result_file:
                            result_file.write('\n'.join([f"{label}: {"X"*len(value)}" for label, value in sensitive_data]))
                        image_paths.append(f'processed_' + filename)
                except Exception as e:
                    app.logger.error(f"Error processing DOCX: {e}")
                    return jsonify({'error': str(e)}), 500

            # Handle TXT files
            elif filename.lower().endswith('.txt'):
                try:
                    text = process_text_file(file_path)
                    sensitive_data = check_sensitive_data(text)
                    if sensitive_data:
                        result_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename)
                        with open(result_file_path, 'w', encoding='utf-8') as result_file:
                            result_file.write('\n'.join([f"{label}: {"X"*len(value)}" for label, value in sensitive_data]))
                        image_paths.append(f'processed_' + filename)
                except Exception as e:
                    app.logger.error(f"Error processing TXT: {e}")
                    return jsonify({'error': str(e)}), 500

            else:
                return jsonify({'error': 'Unsupported file format'}), 400

            os.remove(file_path)

            result = {'sensitive_data': sensitive_data}
            if image_paths:
                result['blurred_image_urls'] = [f'/download/{path}' for path in image_paths]

            return jsonify(result)
        
        else:
            return jsonify({'error': 'Invalid file'}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
