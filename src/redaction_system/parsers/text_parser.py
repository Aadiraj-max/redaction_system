"""Text File Parser"""
from typing import List, Dict
from pathlib import Path

class TextParser:
    """Parse Text files and extract text"""
    
    def __init__(self):
        print("📝 Initializing TextParser")
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse Text file and return text chunks
        
        Args:
            file_path: Path to Text file
        
        Returns:
            List of dicts with 'text', 'line', 'chunk_id'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.suffix.lower() == '.txt':
            raise ValueError(f"Not a Text file: {file_path}")
        
        print(f"🔍 Parsing Text: {file_path.name}")
        
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Group lines into chunks (paragraphs)
            current_chunk = []
            chunk_num = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip()
                
                if line.strip():
                    current_chunk.append(line)
                elif current_chunk:
                    text = '\n'.join(current_chunk)
                    chunk_num += 1
                    chunks.append({
                        'text': text,
                        'line_start': line_num - len(current_chunk),
                        'chunk_id': f"txt_{chunk_num}",
                        'format': 'text'
                    })
                    current_chunk = []
            
            if current_chunk:
                text = '\n'.join(current_chunk)
                chunk_num += 1
                chunks.append({
                    'text': text,
                    'chunk_id': f"txt_{chunk_num}",
                    'format': 'text'
                })
            
            print(f"   ✅ Extracted {len(chunks)} chunks from Text")
            return chunks
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Text file: {e}")
