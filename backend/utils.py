import os  # Operating system interface
import uuid  # Generate unique identifiers
import logging  # Logging
from PIL import Image  # Image processing
import cv2  # OpenCV for advanced image processing

logger = logging.getLogger(__name__)

def save_uploaded_file(file, upload_dir='uploads'):
    # Save uploaded file to disk with unique name
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    logger.info(f"File saved: {filepath}")
    return filepath

def validate_image(file):
    # Validate if file is a valid image
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)  # Reset stream position after verification
        return True
    except Exception as e:
        logger.error(f"Invalid image: {e}")
        return False

def resize_image(image_path, max_size=512):
    # Resize image while maintaining aspect ratio
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Failed to read image: {image_path}")
        return
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(image_path, resized)
        logger.info(f"Image resized to {new_width}x{new_height}")

def cleanup_files(file_paths):
    # Remove temporary files
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up: {path}")
