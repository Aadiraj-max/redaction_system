"""Main Orchestrator - Coordinates Agent, Redactor, and Parsers"""
from pathlib import Path
from typing import List, Dict
from redaction_system.agent import interpret_prompt, EntityConfig
from redaction_system.redactor import PresidioRedactor
from redaction_system.parsers import PDFParser, DOCXParser, ExcelParser, MarkdownParser

class Orchestrator:
    """Orchestrates the full redaction pipeline"""
    
    def __init__(self):
        print("🎯 Initializing Orchestrator")
        self.agent = None  # Lazy load
        self.redactor = PresidioRedactor()
        self.parsers = {
            'pdf': PDFParser(),
            'docx': DOCXParser(),
            'xlsx': ExcelParser(),
            'xls': ExcelParser(),
            'csv': ExcelParser(),
            'md': MarkdownParser()
        }
    
    def _get_parser(self, file_path: str):
        """Get appropriate parser for file type"""
        file_path = Path(file_path)
        ext = file_path.suffix.lower().lstrip('.')
        
        if ext not in self.parsers:
            raise ValueError(f"Unsupported format: {ext}. Supported: {list(self.parsers.keys())}")
        
        return self.parsers[ext]
    
    def redact_file(self, file_path: str, redaction_prompt: str, output_path: str = None) -> str:
        """
        Main redaction pipeline
        
        Args:
            file_path: Path to input file
            redaction_prompt: User intent ("redact names", "anonymize all", etc.)
            output_path: Where to save redacted file (default: original_redacted.format)
        
        Returns:
            Path to redacted file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"\n🔄 REDACTION PIPELINE")
        print(f"{'='*60}")
        print(f"📁 Input:  {file_path}")
        print(f"💬 Prompt: {redaction_prompt}")
        
        # STEP 1: Parse file
        print(f"\n1️⃣  PARSING")
        parser = self._get_parser(str(file_path))
        chunks = parser.parse(str(file_path))
        
        if not chunks:
            raise ValueError("No text extracted from file")
        
        # STEP 2: Get redaction config from Agent
        print(f"\n2️⃣  AGENT DECISION")
        config = interpret_prompt(redaction_prompt)
        print(f"   Entities to redact: {config.entities}")
        
        # STEP 3: Redact all chunks
        print(f"\n3️⃣  REDACTING ({len(chunks)} chunks)")
        redacted_chunks = []
        
        for i, chunk in enumerate(chunks, 1):
            original_text = chunk['text']
            redacted_text = self.redactor.redact_text(original_text, config)
            
            redacted_chunk = chunk.copy()
            redacted_chunk['text'] = redacted_text
            redacted_chunk['original_text'] = original_text
            redacted_chunks.append(redacted_chunk)
            
            # Progress indicator
            if i % max(1, len(chunks) // 5) == 0:
                print(f"   {i}/{len(chunks)} chunks redacted...")
        
        # STEP 4: Reassemble file
        print(f"\n4️⃣  REASSEMBLING")
        if output_path is None:
            output_path = file_path.parent / f"{file_path.stem}_redacted{file_path.suffix}"
        else:
            output_path = Path(output_path)
        
        self._save_redacted_file(redacted_chunks, output_path, file_path.suffix.lower())
        
        print(f"\n✅ COMPLETE")
        print(f"{'='*60}")
        print(f"📁 Output: {output_path}")
        
        return str(output_path)
    
    def _save_redacted_file(self, chunks: List[Dict], output_path: Path, file_format: str):
        """Save redacted content back to file"""
        if file_format == '.pdf':
            # For now, save as text (full PDF rewriting is complex)
            with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    f.write(chunk['text'] + '\n\n')
            print(f"   ℹ️  PDF saved as text: {output_path.with_suffix('.txt')}")
        
        elif file_format == '.docx':
            from docx import Document
            doc = Document()
            for chunk in chunks:
                doc.add_paragraph(chunk['text'])
            doc.save(output_path)
            print(f"   ✅ Saved DOCX: {output_path}")
        
        elif file_format in ['.xlsx', '.xls', '.csv']:
            import pandas as pd
            # Reconstruct dataframe
            rows = []
            for chunk in chunks:
                if 'original_row' in chunk:
                    # Redact each field in the row
                    redacted_row = {}
                    for key, val in chunk['original_row'].items():
                        redacted_row[key] = chunk['text'].split(' | ')[-1] if key == 'value' else val
                    rows.append(redacted_row)
            
            if rows:
                df = pd.DataFrame(rows)
                if file_format == '.csv':
                    df.to_csv(output_path, index=False)
                else:
                    df.to_excel(output_path, index=False)
                print(f"   ✅ Saved Excel: {output_path}")
        
        elif file_format == '.md':
            with open(output_path, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    f.write(chunk['text'] + '\n\n')
            print(f"   ✅ Saved Markdown: {output_path}")
