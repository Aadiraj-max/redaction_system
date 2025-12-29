"""Markdown File Parser"""
from typing import List, Dict
from pathlib import Path

class MarkdownParser:
    """Parse Markdown files and extract text"""
    
    def __init__(self):
        print("📝 Initializing MarkdownParser")
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse Markdown and return text chunks with metadata
        
        Args:
            file_path: Path to Markdown file
        
        Returns:
            List of dicts with 'text', 'line', 'chunk_id'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown not found: {file_path}")
        
        if not file_path.suffix.lower() == '.md':
            raise ValueError(f"Not a Markdown file: {file_path}")
        
        print(f"🔍 Parsing Markdown: {file_path.name}")
        
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Group lines into chunks (non-empty paragraphs)
            current_chunk = []
            chunk_num = 0
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip()
                
                if line.strip():
                    current_chunk.append(line)
                elif current_chunk:
                    # Empty line = end of paragraph
                    text = '\n'.join(current_chunk)
                    chunk_num += 1
                    
                    chunks.append({
                        'text': text,
                        'line_start': line_num - len(current_chunk),
                        'chunk_id': f"md_{chunk_num}",
                        'format': 'markdown'
                    })
                    current_chunk = []
            
            # Add remaining chunk
            if current_chunk:
                text = '\n'.join(current_chunk)
                chunk_num += 1
                chunks.append({
                    'text': text,
                    'chunk_id': f"md_{chunk_num}",
                    'format': 'markdown'
                })
            
            print(f"   ✅ Extracted {len(chunks)} chunks from Markdown")
            return chunks
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Markdown: {e}")
