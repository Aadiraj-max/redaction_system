"""Excel File Parser"""
from typing import List, Dict
from pathlib import Path
import pandas as pd

class ExcelParser:
    """Parse Excel files and extract data"""
    
    def __init__(self):
        print("📊 Initializing ExcelParser")
    
    def parse(self, file_path: str) -> List[Dict]:
        """
        Parse Excel and return text chunks with metadata
        
        Args:
            file_path: Path to Excel file (.xlsx or .csv)
        
        Returns:
            List of dicts with 'text', 'row', 'chunk_id'
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        if file_path.suffix.lower() not in ['.xlsx', '.xls', '.csv']:
            raise ValueError(f"Not an Excel file: {file_path}")
        
        print(f"🔍 Parsing Excel: {file_path.name}")
        
        chunks = []
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path, dtype=str)
            
            # Convert each row to text
            for row_num, (idx, row) in enumerate(df.iterrows(), 1):
                # Combine all columns into single text
                row_text = ' | '.join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                
                if row_text.strip():
                    chunks.append({
                        'text': row_text,
                        'row': row_num,
                        'chunk_id': f"excel_{row_num}",
                        'format': 'excel',
                        'original_row': row.to_dict()
                    })
            
            print(f"   ✅ Extracted {len(chunks)} rows from Excel")
            return chunks
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Excel: {e}")
