"""
CV Parser Service
Extract text from PDF/DOCX files
"""

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    PyPDF2 = None

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

from typing import List, Dict, Any
import os


class CVParser:
    """Parse CV files in various formats"""
    
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parse a CV file and extract text
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return CVParser._parse_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return CVParser._parse_docx(file_path)
        elif file_extension == '.txt':
            return CVParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF file"""
        # Try PyMuPDF first
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                
                text_content = []
                page_count = len(doc)
                
                for page_num, page in enumerate(doc):
                    text = page.get_text("text")
                    text_content.append(text)
                
                full_text = "\n\n".join(text_content)
                
                doc.close()
                
                if len(full_text.strip()) > 10:  # If we got meaningful text
                    return {
                        'text': full_text,
                        'page_count': page_count,
                        'file_type': 'pdf',
                        'metadata': {},
                    }
            except Exception as e:
                print(f"PyMuPDF failed: {str(e)}")
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    text_content = []
                    page_count = len(pdf_reader.pages)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        text_content.append(text)
                    
                    full_text = "\n\n".join(text_content)
                    
                    return {
                        'text': full_text,
                        'page_count': page_count,
                        'file_type': 'pdf',
                        'metadata': {},
                    }
            except Exception as e:
                print(f"PyPDF2 failed: {str(e)}")
        
        raise ValueError("Could not parse PDF with any available library")
    
    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """Parse DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        
        doc = Document(file_path)
        
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        full_text = "\n".join(paragraphs)
        
        return {
            'text': full_text,
            'file_type': 'docx',
            'metadata': {},
        }
    
    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """Parse TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            full_text = file.read()
        
        return {
            'text': full_text,
            'file_type': 'txt',
            'metadata': {},
        }
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Simply extract text from a CV file"""
        parsed = CVParser.parse_file(file_path)
        return parsed['text']
    
    @staticmethod
    def is_valid_format(file_path: str) -> bool:
        """Check if file format is supported"""
        supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in supported_formats

