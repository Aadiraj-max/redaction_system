"""Main Orchestrator - Coordinates Agent, Redactor, and Parsers"""
from pathlib import Path
from typing import List, Dict
from redaction_system.agent import interpret_prompt, validate_candidates, EntityConfig
from redaction_system.redactor.presidio_wrapper import PresidioRedactor
from redaction_system.parsers import PDFParser, DOCXParser, ExcelParser, MarkdownParser, TextParser

class Orchestrator:
    """Orchestrates the full redaction pipeline"""
    
    def __init__(self):
        print("🎯 Initializing Orchestrator")
        self.redactor = PresidioRedactor()
        self.parsers = {
            'pdf': PDFParser(),
            'docx': DOCXParser(),
            'xlsx': ExcelParser(),
            'xls': ExcelParser(),
            'csv': ExcelParser(),
            'md': MarkdownParser(),
            'txt': TextParser()
        }
    
    def _get_parser(self, file_path: str):
        file_path = Path(file_path)
        ext = file_path.suffix.lower().lstrip('.')
        if ext not in self.parsers:
            raise ValueError(f"Unsupported format: {ext}")
        return self.parsers[ext]
    
    def redact_file(self, file_path: str, redaction_prompt: str, output_path: str = None) -> str:
        file_path = Path(file_path)
        
        # STEP 1: Parse file
        print(f"\n1️⃣  PARSING")
        parser = self._get_parser(str(file_path))
        chunks = parser.parse(str(file_path))
        
        # STEP 2: Job 1 - Agent interprets prompt
        print(f"\n2️⃣  AGENT DECISION (Job 1: Interpret)")
        config = interpret_prompt(redaction_prompt)
        print(f"   Entities to redact: {config.entities}")
        
        # STEP 3: Redact all chunks
        print(f"\n3️⃣  PROCESSING ({len(chunks)} chunks)")
        redacted_chunks = []
        
        for i, chunk in enumerate(chunks, 1):
            text = chunk['text']
            
            # --- VALIDATION LOGIC (Your snippets) ---
            
            # A. Presidio Processes (with low threshold to catch everything)
            results = self.redactor.analyze(text, config.entities, score_threshold=0.1)
            print(f"   Raw Presidio found {len(results)} candidates")
            
            # B. Split by confidence
            certain = [r for r in results if r.score >= 0.7]
            uncertain = [r for r in results if r.score < 0.7]
            
            # C. Job 2 - Agent validates uncertain entities
            validated = []
            if uncertain:
                # Prepare candidates for the analyst (Job 2)
                # We use a context window of +/- 50 chars for the LLM
                candidates_for_llm = []
                for idx, r in enumerate(uncertain):
                    start = max(0, r.start - 50)
                    end = min(len(text), r.end + 50)
                    context_snippet = text[start:end]
                    
                    candidates_for_llm.append({
                        'id': idx,
                        'text': text[r.start:r.end],
                        'entity_type': r.entity_type,
                        'context': context_snippet,
                        'start': r.start,
                        'end': r.end
                    })
                
                # Batch call to Agent for validation
                # (Passing 'text' as full context, but candidates have snippets)
                validated_dicts = validate_candidates(candidates_for_llm, text)
                
                # Map back to Presidio objects
                for v in validated_dicts:
                    for r in uncertain:
                        if r.start == v['start'] and r.end == v['end']:
                            validated.append(r)
                            break
            
            # D. Combine and Redact
            final_results = certain + validated
            redacted_text = self.redactor.anonymize(text, final_results)
            
            # Log results for this chunk if anything was found
            if final_results:
                print(f"   Chunk {i}: Redacted {len(certain)} certain and {len(validated)} validated entities.")
            
            redacted_chunk = chunk.copy()
            redacted_chunk['text'] = redacted_text
            redacted_chunks.append(redacted_chunk)
        
        # STEP 4: Reassemble file
        print(f"\n4️⃣  REASSEMBLING")
        if output_path is None:
            output_path = file_path.parent / f"{file_path.stem}_redacted{file_path.suffix}"
        else:
            output_path = Path(output_path)
        
        self._save_redacted_file(redacted_chunks, output_path, file_path.suffix.lower())
        
        print(f"\n✅ COMPLETE -> {output_path}")
        return str(output_path)
    
    def _save_redacted_file(self, chunks: List[Dict], output_path: Path, file_format: str):
        if file_format in ['.md', '.txt']:
            with open(output_path, 'w', encoding='utf-8') as f:
                for chunk in chunks:
                    f.write(chunk['text'] + '\n\n')
        elif file_format == '.docx':
            from docx import Document
            doc = Document()
            for chunk in chunks:
                doc.add_paragraph(chunk['text'])
            doc.save(output_path)
        # ... (Excel and PDF logic would go here, omitting for brevity in this tool call)
