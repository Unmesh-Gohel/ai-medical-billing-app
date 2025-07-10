"""
Medical Coding Tools for CrewAI agents with NLP and RAG capabilities
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from crewai_tools import BaseTool
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

from app.utils.logging import get_logger
from app.config import settings


logger = get_logger("tools.coding")


class MedicalCodingTool(BaseTool):
    """AI-powered tool for assigning medical codes to clinical documentation"""
    
    name: str = "Medical Coding Assistant"
    description: str = (
        "Assign ICD-10, CPT, and HCPCS codes to clinical documentation using NLP and RAG. "
        "Input should be JSON with clinical_text, documentation_type, and specialty. "
        "Returns suggested codes with confidence scores and explanations."
    )
    
    def __init__(self):
        super().__init__()
        self.embedding_model = None
        self.chroma_client = None
        self.coding_collection = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models and vector database"""
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            
            # Get or create coding collection
            try:
                self.coding_collection = self.chroma_client.get_collection("medical_codes")
            except:
                self.coding_collection = self.chroma_client.create_collection(
                    name="medical_codes",
                    metadata={"description": "Medical coding knowledge base"}
                )
                self._populate_coding_knowledge()
            
            logger.info("Medical coding models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize coding models: {str(e)}")
    
    def _run(self, input_data: str) -> str:
        """Assign medical codes to clinical text"""
        try:
            # Parse input data
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data
            
            clinical_text = data.get("clinical_text", "")
            documentation_type = data.get("documentation_type", "general")
            specialty = data.get("specialty", "general")
            code_types = data.get("code_types", ["icd10", "cpt"])
            
            if not clinical_text:
                return json.dumps({"error": "Clinical text is required for coding"})
            
            # Process clinical text and extract relevant information
            processed_text = self._preprocess_clinical_text(clinical_text)
            
            # Extract medical entities and concepts
            entities = self._extract_medical_entities(processed_text)
            
            # Generate code suggestions for each type
            coding_results = {}
            
            for code_type in code_types:
                codes = self._suggest_codes(processed_text, entities, code_type, specialty)
                coding_results[code_type] = codes
            
            # Validate and cross-reference codes
            validated_codes = self._validate_code_combinations(coding_results)
            
            result = {
                "clinical_text": clinical_text,
                "documentation_type": documentation_type,
                "specialty": specialty,
                "extracted_entities": entities,
                "suggested_codes": validated_codes,
                "coding_confidence": self._calculate_overall_confidence(validated_codes),
                "coding_notes": self._generate_coding_notes(entities, validated_codes)
            }
            
            logger.info(f"Medical coding completed for {documentation_type} documentation")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Medical coding failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _preprocess_clinical_text(self, text: str) -> str:
        """Preprocess clinical text for better entity extraction"""
        # Normalize text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s\-\.\,\:\;]', '', text)  # Remove special chars
        
        # Expand common medical abbreviations
        abbreviations = {
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'mi': 'myocardial infarction',
            'cad': 'coronary artery disease',
            'copd': 'chronic obstructive pulmonary disease',
            'chf': 'congestive heart failure',
            'uti': 'urinary tract infection',
            'uri': 'upper respiratory infection',
            'gerd': 'gastroesophageal reflux disease',
            'oa': 'osteoarthritis'
        }
        
        for abbrev, full_term in abbreviations.items():
            text = re.sub(r'\b' + abbrev + r'\b', full_term, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from clinical text"""
        entities = {
            "diagnoses": [],
            "procedures": [],
            "symptoms": [],
            "medications": [],
            "anatomy": [],
            "lab_values": []
        }
        
        # Use pattern matching for common medical entities
        # In production, this would use a trained NER model
        
        # Extract diagnoses
        diagnosis_patterns = [
            r'\b(diabetes|hypertension|pneumonia|bronchitis|arthritis|fracture)\b',
            r'\b(\w+itis)\b',  # Inflammatory conditions
            r'\b(\w+oma)\b',   # Tumors
            r'\b(\w+pathy)\b'  # Disease conditions
        ]
        
        for pattern in diagnosis_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["diagnoses"].extend([match.lower() if isinstance(match, str) else match[0].lower() for match in matches])
        
        # Extract procedures
        procedure_patterns = [
            r'\b(surgery|biopsy|injection|examination|consultation)\b',
            r'\b(\w+ectomy)\b',  # Surgical removals
            r'\b(\w+oscopy)\b',  # Endoscopic procedures
            r'\b(\w+plasty)\b'   # Reconstructive procedures
        ]
        
        for pattern in procedure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["procedures"].extend([match.lower() if isinstance(match, str) else match[0].lower() for match in matches])
        
        # Extract symptoms
        symptom_patterns = [
            r'\b(pain|fever|nausea|vomiting|headache|fatigue|cough|shortness of breath)\b',
            r'\b(swelling|redness|tenderness|stiffness)\b'
        ]
        
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["symptoms"].extend([match.lower() for match in matches])
        
        # Remove duplicates and clean up
        for entity_type in entities:
            entities[entity_type] = list(set(entities[entity_type]))
        
        return entities
    
    def _suggest_codes(self, text: str, entities: Dict[str, List[str]], 
                      code_type: str, specialty: str) -> List[Dict[str, Any]]:
        """Suggest codes using RAG and similarity matching"""
        if not self.coding_collection:
            return []
        
        try:
            # Create query embedding
            query_text = f"{text} {' '.join(entities.get('diagnoses', []))} {' '.join(entities.get('procedures', []))}"
            query_embedding = self.embedding_model.encode([query_text])
            
            # Search for similar codes in vector database
            results = self.coding_collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=10,
                where={"code_type": code_type}
            )
            
            suggested_codes = []
            
            for i, (code, description, distance) in enumerate(zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                confidence = max(0, 1 - distance)  # Convert distance to confidence
                
                suggested_code = {
                    "code": code,
                    "description": description.get("description", ""),
                    "code_type": code_type,
                    "confidence": round(confidence, 3),
                    "reasoning": self._generate_code_reasoning(text, entities, code, description),
                    "specialty_specific": specialty.lower() in description.get("specialties", [])
                }
                
                suggested_codes.append(suggested_code)
            
            # Sort by confidence and specialty relevance
            suggested_codes.sort(key=lambda x: (x["confidence"], x["specialty_specific"]), reverse=True)
            
            return suggested_codes[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Code suggestion failed for {code_type}: {str(e)}")
            return []
    
    def _generate_code_reasoning(self, text: str, entities: Dict[str, List[str]], 
                               code: str, description: Dict[str, Any]) -> str:
        """Generate reasoning for why a code was suggested"""
        reasoning_parts = []
        
        # Check for direct matches
        code_desc = description.get("description", "").lower()
        
        for diagnosis in entities.get("diagnoses", []):
            if diagnosis in code_desc:
                reasoning_parts.append(f"Matches diagnosed condition: {diagnosis}")
        
        for procedure in entities.get("procedures", []):
            if procedure in code_desc:
                reasoning_parts.append(f"Matches documented procedure: {procedure}")
        
        for symptom in entities.get("symptoms", []):
            if symptom in code_desc:
                reasoning_parts.append(f"Aligns with reported symptom: {symptom}")
        
        if not reasoning_parts:
            reasoning_parts.append("Suggested based on semantic similarity to clinical documentation")
        
        return "; ".join(reasoning_parts)
    
    def _validate_code_combinations(self, coding_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Validate code combinations and check for conflicts"""
        validated = {}
        
        for code_type, codes in coding_results.items():
            validated_codes = []
            
            for code in codes:
                # Basic validation rules
                is_valid = True
                validation_notes = []
                
                # Check for common coding conflicts
                if code_type == "icd10":
                    # Ensure diagnosis codes are appropriate
                    if code["confidence"] < 0.3:
                        validation_notes.append("Low confidence - manual review recommended")
                    
                elif code_type == "cpt":
                    # Ensure procedure codes match documented procedures
                    if not any(proc in code["description"].lower() 
                             for proc in coding_results.get("procedures", [])):
                        validation_notes.append("Procedure code may not match documentation")
                
                if is_valid:
                    code["validation_notes"] = validation_notes
                    validated_codes.append(code)
            
            validated[code_type] = validated_codes
        
        return validated
    
    def _calculate_overall_confidence(self, validated_codes: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate overall confidence score for the coding assignment"""
        all_confidences = []
        
        for code_type, codes in validated_codes.items():
            for code in codes:
                all_confidences.append(code["confidence"])
        
        if not all_confidences:
            return 0.0
        
        return round(sum(all_confidences) / len(all_confidences), 3)
    
    def _generate_coding_notes(self, entities: Dict[str, List[str]], 
                             validated_codes: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate coding notes and recommendations"""
        notes = []
        
        # Check for missing primary diagnosis
        icd_codes = validated_codes.get("icd10", [])
        if not icd_codes:
            notes.append("No ICD-10 diagnosis codes identified - manual coding required")
        
        # Check for procedure documentation
        cpt_codes = validated_codes.get("cpt", [])
        procedures = entities.get("procedures", [])
        
        if procedures and not cpt_codes:
            notes.append("Procedures documented but no CPT codes identified")
        
        # Check for high-confidence codes
        high_conf_codes = []
        for code_type, codes in validated_codes.items():
            high_conf_codes.extend([c for c in codes if c["confidence"] > 0.8])
        
        if high_conf_codes:
            notes.append(f"{len(high_conf_codes)} high-confidence codes identified")
        
        # Check for specialty-specific considerations
        specialty_codes = []
        for code_type, codes in validated_codes.items():
            specialty_codes.extend([c for c in codes if c.get("specialty_specific", False)])
        
        if specialty_codes:
            notes.append("Specialty-specific codes identified")
        
        return notes
    
    def _populate_coding_knowledge(self):
        """Populate the vector database with medical coding knowledge"""
        # Sample coding data - in production, this would load from comprehensive databases
        sample_codes = [
            {
                "code": "E11.9",
                "description": "Type 2 diabetes mellitus without complications",
                "code_type": "icd10",
                "specialties": ["endocrinology", "internal medicine", "family medicine"]
            },
            {
                "code": "I10",
                "description": "Essential hypertension",
                "code_type": "icd10", 
                "specialties": ["cardiology", "internal medicine", "family medicine"]
            },
            {
                "code": "99213",
                "description": "Office visit, established patient, level 3",
                "code_type": "cpt",
                "specialties": ["all"]
            },
            {
                "code": "99214",
                "description": "Office visit, established patient, level 4",
                "code_type": "cpt",
                "specialties": ["all"]
            }
        ]
        
        try:
            for code_data in sample_codes:
                # Create embedding for the code description
                embedding = self.embedding_model.encode([code_data["description"]])
                
                # Add to collection
                self.coding_collection.add(
                    embeddings=embedding.tolist(),
                    documents=[code_data["description"]],
                    metadatas=[{
                        "description": code_data["description"],
                        "code_type": code_data["code_type"],
                        "specialties": code_data["specialties"]
                    }],
                    ids=[code_data["code"]]
                )
            
            logger.info(f"Populated coding knowledge base with {len(sample_codes)} codes")
            
        except Exception as e:
            logger.error(f"Failed to populate coding knowledge: {str(e)}")


class DiagnosisLookupTool(BaseTool):
    """Tool for looking up ICD-10 diagnosis codes"""
    
    name: str = "ICD-10 Diagnosis Lookup"
    description: str = (
        "Look up ICD-10 diagnosis codes by description or code. "
        "Input should be a search term or ICD-10 code. "
        "Returns matching diagnosis codes with descriptions."
    )
    
    def _run(self, search_term: str) -> str:
        """Look up ICD-10 diagnosis codes"""
        try:
            # Mock ICD-10 lookup - in production would query comprehensive database
            icd10_codes = {
                "diabetes": [
                    {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
                    {"code": "E10.9", "description": "Type 1 diabetes mellitus without complications"},
                    {"code": "E11.21", "description": "Type 2 diabetes mellitus with diabetic nephropathy"}
                ],
                "hypertension": [
                    {"code": "I10", "description": "Essential (primary) hypertension"},
                    {"code": "I11.9", "description": "Hypertensive heart disease without heart failure"},
                    {"code": "I12.9", "description": "Hypertensive chronic kidney disease without heart failure"}
                ],
                "pneumonia": [
                    {"code": "J18.9", "description": "Pneumonia, unspecified organism"},
                    {"code": "J15.9", "description": "Unspecified bacterial pneumonia"},
                    {"code": "J12.9", "description": "Viral pneumonia, unspecified"}
                ]
            }
            
            search_lower = search_term.lower()
            results = []
            
            # Search by description
            for condition, codes in icd10_codes.items():
                if search_lower in condition or condition in search_lower:
                    results.extend(codes)
            
            # Search by exact code
            if search_term.upper() in ["E11.9", "I10", "J18.9"]:  # Sample exact matches
                for codes in icd10_codes.values():
                    for code in codes:
                        if code["code"] == search_term.upper():
                            results.append(code)
            
            result = {
                "search_term": search_term,
                "matches": results[:10],  # Limit to 10 results
                "total_found": len(results)
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"ICD-10 lookup failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})


class ProcedureLookupTool(BaseTool):
    """Tool for looking up CPT procedure codes"""
    
    name: str = "CPT Procedure Lookup"
    description: str = (
        "Look up CPT procedure codes by description or code. "
        "Input should be a search term or CPT code. "
        "Returns matching procedure codes with descriptions."
    )
    
    def _run(self, search_term: str) -> str:
        """Look up CPT procedure codes"""
        try:
            # Mock CPT lookup - in production would query comprehensive database
            cpt_codes = {
                "office visit": [
                    {"code": "99213", "description": "Office visit, established patient, level 3"},
                    {"code": "99214", "description": "Office visit, established patient, level 4"},
                    {"code": "99203", "description": "Office visit, new patient, level 3"}
                ],
                "injection": [
                    {"code": "96372", "description": "Therapeutic injection, subcutaneous or intramuscular"},
                    {"code": "20610", "description": "Arthrocentesis, aspiration and injection, major joint"},
                    {"code": "11900", "description": "Injection, intralesional; up to and including 7 lesions"}
                ],
                "surgery": [
                    {"code": "27447", "description": "Total knee arthroplasty"},
                    {"code": "66984", "description": "Extracapsular cataract removal"},
                    {"code": "43239", "description": "Upper endoscopy, biopsy"}
                ]
            }
            
            search_lower = search_term.lower()
            results = []
            
            # Search by description
            for procedure_type, codes in cpt_codes.items():
                if search_lower in procedure_type or procedure_type in search_lower:
                    results.extend(codes)
            
            # Search by exact code
            if search_term in ["99213", "99214", "96372"]:  # Sample exact matches
                for codes in cpt_codes.values():
                    for code in codes:
                        if code["code"] == search_term:
                            results.append(code)
            
            result = {
                "search_term": search_term,
                "matches": results[:10],  # Limit to 10 results
                "total_found": len(results)
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"CPT lookup failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}) 