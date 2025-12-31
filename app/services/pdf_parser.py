"""
AI Career Companion - PDF Parser Service
Extracts text and structured data from resume PDFs.
"""
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import pdfplumber

logger = logging.getLogger(__name__)


class PDFParserService:
    """
    PDF parsing service for resume extraction.
    Uses pdfplumber for reliable text extraction.
    """
    
    def __init__(self):
        logger.info("📄 PDF Parser Service initialized")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes (for file uploads).
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        import io
        try:
            text_parts = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"PDF bytes extraction error: {e}")
            raise
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Attempt to extract common resume sections.
        
        Args:
            text: Full resume text
            
        Returns:
            Dict with section names as keys
        """
        sections = {}
        current_section = "header"
        current_content = []
        
        # Common section headers
        section_keywords = [
            "education", "experience", "work experience", "employment",
            "skills", "technical skills", "projects", "achievements",
            "certifications", "awards", "publications", "interests",
            "objective", "summary", "profile"
        ]
        
        for line in text.split("\n"):
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            is_header = False
            for keyword in section_keywords:
                if keyword in line_lower and len(line_lower) < 50:
                    # Save previous section
                    if current_content:
                        sections[current_section] = "\n".join(current_content)
                    
                    # Start new section
                    current_section = keyword.replace(" ", "_")
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from resume text.
        
        Returns:
            Dict with email, phone, linkedin, github
        """
        import re
        
        contact = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "name": None
        }
        
        # Email pattern
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact["email"] = email_match.group()
        
        # Phone pattern (various formats)
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text.lower())
        if linkedin_match:
            contact["linkedin"] = f"https://{linkedin_match.group()}"
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text.lower())
        if github_match:
            contact["github"] = f"https://{github_match.group()}"
        
        # Name (usually first line or first capitalized words)
        lines = text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            # Check if first line looks like a name (2-4 words, mostly letters)
            words = first_line.split()
            if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
                contact["name"] = first_line
        
        return contact


# Singleton instance
_pdf_service: Optional[PDFParserService] = None

def get_pdf_parser() -> PDFParserService:
    """Get or create PDF parser service."""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFParserService()
    return _pdf_service
