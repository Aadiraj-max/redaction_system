"""PDF File Parser"""
from typing import List, Dict
from pathlib import Path
import pdfplumber

class PDFParser:
    """Parse PDF files and extract text"""
    
    def __init__(self):
        print("📄 Initializing PDFParser")
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse PDF and return text chunks with metadata
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            List of dicts with 'text', 'page', 'chunk_id'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")
        
        if not file_path.suffix.lower() == '.pdf':
            raise ValueError(f"Not a PDF file: {file_path}")
        
        print(f"🔍 Parsing PDF: {file_path.name}")
        
        chunks = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text.strip():
                        chunks.append({
                            'text': text,
                            'page': page_num,
                            'chunk_id': f"pdf_{page_num}",
                            'format': 'pdf'
                        })
            
            print(f"   ✅ Extracted {len(chunks)} pages from PDF")
            return chunks
            
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF: {e}")

