import cv2
import numpy as np
import pytesseract
from PIL import Image
import os
import re
from typing import Dict, List, Optional, Any
import easyocr
import easyocr

class OCRProcessor:
    def __init__(self, confidence_threshold: int = 90):
        self.confidence_threshold = confidence_threshold

    def extract_text_from_image(self, image_dir: str) -> str:
        """Extract text from all images in a directory."""
        try:
            full_text = ""
            for image_file in os.listdir(image_dir):
                image_path = os.path.join(image_dir, image_file)
                print(f"Processing: {image_path}")
                reader = easyocr.Reader(["en"])
                results = reader.readtext(image_path)
                for bbox, text, conf in results:
                    full_text += text + " "

            return full_text.strip()
        except Exception as e:
            print(f"Error in extract_text_from_image: {e}")
            return ""

    def extract_text_from_bytes(self, image_bytes:List[bytes]) -> str:
        """Extract text directly from raw image bytes."""
        try:
            full_text = ""
            for image_byte in image_bytes:
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Could not decode image from bytes")

                reader = easyocr.Reader(["en"])
                results = reader.readtext(image)
                for bbox, text, conf in results:
                    full_text += text + " "
            return full_text.strip()
        except Exception as e:
            print(f"Error in extract_text_from_bytes: {e}")
            return ""

    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured info like part numbers, serial numbers, etc."""
        structured_data: Dict[str, Any] = {}
        patterns = {
            'part_number': r'(?:Part|P/N|Part No|Part Number)[:\s]+([A-Z0-9\-]+)',
            'serial_number': r'(?:Serial|S/N|Serial No|Serial Number)[:\s]+([A-Z0-9\-]+)',
            'date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'amount': r'[$]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'phone': r'(\d{3}-\d{3}-\d{4}|\(\d{3}\)\s*\d{3}-\d{4})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        }

        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                structured_data[key] = matches

        return structured_data
