"""DOCX File Parser"""
from typing import List, Dict
from pathlib import Path
from docx import Document

class DOCXParser:
    """Parse DOCX files and extract text"""
    
    def __init__(self):
        print("📄 Initializing DOCXParser")
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse DOCX and return text chunks with metadata
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            List of dicts with 'text', 'paragraph', 'chunk_id'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX not found: {file_path}")
        
        if not file_path.suffix.lower() == '.docx':
            raise ValueError(f"Not a DOCX file: {file_path}")
        
        print(f"🔍 Parsing DOCX: {file_path.name}")
        
        chunks = []
        
        try:
            doc = Document(file_path)
            
            for para_num, paragraph in enumerate(doc.paragraphs, 1):
                text = paragraph.text.strip()
                
                if text:
                    chunks.append({
                        'text': text,
                        'paragraph': para_num,
                        'chunk_id': f"docx_{para_num}",
                        'format': 'docx'
                    })
            
            print(f"   ✅ Extracted {len(chunks)} paragraphs from DOCX")
            return chunks
            
        except Exception as e:
            raise RuntimeError(f"Error parsing DOCX: {e}")
