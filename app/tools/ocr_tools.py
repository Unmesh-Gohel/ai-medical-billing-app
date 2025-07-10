"""
OCR Tools for CrewAI agents to extract data from documents and insurance cards
"""

import json
import re
from typing import Dict, Any, Optional
from crewai_tools import BaseTool
import pytesseract
from PIL import Image
import cv2
import numpy as np

from app.utils.logging import get_logger


logger = get_logger("tools.ocr")


class OCRTool(BaseTool):
    """Tool for extracting text from documents using OCR"""
    
    name: str = "OCR Document Processor"
    description: str = (
        "Extract text from medical documents, intake forms, and patient paperwork. "
        "Input should be the file path to the document image. "
        "Returns extracted text with confidence scores."
    )
    
    def _run(self, document_path: str, document_type: str = "general") -> str:
        """Extract text from document using OCR"""
        try:
            # Load and preprocess image
            image = self._preprocess_image(document_path)
            
            # Configure OCR based on document type
            config = self._get_ocr_config(document_type)
            
            # Perform OCR
            extracted_text = pytesseract.image_to_string(image, config=config)
            
            # Get confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            result = {
                "text": extracted_text.strip(),
                "confidence": round(avg_confidence, 2),
                "document_type": document_type,
                "extracted_fields": self._extract_structured_data(extracted_text, document_type)
            }
            
            logger.info(f"OCR completed for {document_type} with {avg_confidence:.1f}% confidence")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"OCR processing failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg, "text": "", "confidence": 0})
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Read image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def _get_ocr_config(self, document_type: str) -> str:
        """Get OCR configuration based on document type"""
        base_config = '--oem 3 --psm 6'
        
        if document_type == "intake_form":
            return f"{base_config} -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ()-.,/:"
        elif document_type == "insurance_card":
            return f"{base_config} -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ()-"
        else:
            return base_config
    
    def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from OCR text based on document type"""
        fields = {}
        
        if document_type == "intake_form":
            fields.update(self._extract_patient_fields(text))
        elif document_type == "insurance_card":
            fields.update(self._extract_insurance_fields(text))
        
        return fields
    
    def _extract_patient_fields(self, text: str) -> Dict[str, str]:
        """Extract patient information from intake form text"""
        patterns = {
            "first_name": r"(?:first\s+name|fname)[\s:]*([A-Za-z]+)",
            "last_name": r"(?:last\s+name|lname|surname)[\s:]*([A-Za-z]+)",
            "date_of_birth": r"(?:dob|date\s+of\s+birth|birth\s+date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "phone": r"(?:phone|telephone|tel)[\s:]*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            "email": r"(?:email|e-mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            "address": r"(?:address|street)[\s:]*([0-9]+\s+[A-Za-z\s]+)",
            "city": r"(?:city)[\s:]*([A-Za-z\s]+)",
            "state": r"(?:state)[\s:]*([A-Z]{2})",
            "zip_code": r"(?:zip|postal|zip\s+code)[\s:]*(\d{5}(?:-\d{4})?)"
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1).strip()
        
        return extracted
    
    def _extract_insurance_fields(self, text: str) -> Dict[str, str]:
        """Extract insurance information from card text"""
        patterns = {
            "member_id": r"(?:member\s+id|id\s+number|member\s+#)[\s:]*([A-Za-z0-9]+)",
            "group_number": r"(?:group\s+number|group\s+#|grp)[\s:]*([A-Za-z0-9]+)",
            "plan_name": r"(?:plan|insurance)[\s:]*([A-Za-z\s]+)",
            "effective_date": r"(?:effective|eff\s+date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "copay": r"(?:copay|co-pay)[\s:]*\$?(\d+)",
            "deductible": r"(?:deductible|ded)[\s:]*\$?(\d+)"
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1).strip()
        
        return extracted


class InsuranceCardTool(BaseTool):
    """Specialized tool for processing insurance cards with front/back recognition"""
    
    name: str = "Insurance Card Processor"
    description: str = (
        "Extract information from insurance cards (front and back). "
        "Input should be JSON with 'image_path' and 'side' (front/back). "
        "Returns structured insurance information."
    )
    
    def _run(self, input_data: str) -> str:
        """Process insurance card and extract relevant information"""
        try:
            # Parse input
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            image_path = data.get("image_path")
            side = data.get("side", "front")
            
            if not image_path:
                return json.dumps({"error": "Image path is required"})
            
            # Use OCR tool to extract text
            ocr_tool = OCRTool()
            ocr_result = json.loads(ocr_tool._run(image_path, "insurance_card"))
            
            # Extract side-specific information
            if side == "front":
                insurance_info = self._extract_front_info(ocr_result.get("text", ""))
            else:
                insurance_info = self._extract_back_info(ocr_result.get("text", ""))
            
            result = {
                "side": side,
                "confidence": ocr_result.get("confidence", 0),
                "insurance_info": insurance_info,
                "raw_text": ocr_result.get("text", "")
            }
            
            logger.info(f"Insurance card {side} processed successfully")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Insurance card processing failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _extract_front_info(self, text: str) -> Dict[str, str]:
        """Extract information from front of insurance card"""
        patterns = {
            "insurance_company": r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*(?:Health|Insurance|Medical)",
            "member_name": r"(?:member|name)[\s:]*([A-Z][a-z]+\s+[A-Z][a-z]+)",
            "member_id": r"(?:member\s+id|id|member\s+#)[\s:]*([A-Za-z0-9-]+)",
            "group_number": r"(?:group|grp)[\s:]*([A-Za-z0-9-]+)",
            "plan_type": r"(?:plan|type)[\s:]*([A-Za-z\s]+)",
            "effective_date": r"(?:effective|eff)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "rx_bin": r"(?:bin|rx\s+bin)[\s:]*(\d+)",
            "rx_pcn": r"(?:pcn|rx\s+pcn)[\s:]*([A-Za-z0-9]+)"
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1).strip()
        
        return extracted
    
    def _extract_back_info(self, text: str) -> Dict[str, str]:
        """Extract information from back of insurance card"""
        patterns = {
            "customer_service": r"(?:customer\s+service|help\s+line|phone)[\s:]*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            "claims_address": r"(?:claims|send\s+claims\s+to)[\s:]*([0-9]+\s+[A-Za-z\s,]+\d{5})",
            "website": r"(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            "precertification": r"(?:precert|pre-cert|authorization)[\s:]*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
            "pharmacy_benefits": r"(?:pharmacy|rx)[\s:]*([A-Za-z\s]+)",
            "mental_health": r"(?:mental\s+health|behavioral)[\s:]*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1).strip()
        
        return extracted 