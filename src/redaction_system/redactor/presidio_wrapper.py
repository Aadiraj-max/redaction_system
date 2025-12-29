"""Presidio PII Redaction Engine"""
from typing import List
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from ..agent.prompt_interpreter import EntityConfig

class PresidioRedactor:
    """High-performance PII redaction using Presidio"""
    
    def __init__(self, language: str = 'en'):
        """
        Initialize Presidio engines
        
        Args:
            language: Detection language ('en', 'de', 'fr', etc.)
        """
        print(f"🔧 Initializing PresidioRedactor (language: {language})")
        self.language = language
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def redact_text(self, text: str, config: EntityConfig) -> str:
        """
        Redact single text block
        
        Args:
            text: Raw text with PII
            config: EntityConfig from agent
        
        Returns:
            Redacted text with <ENTITY> placeholders
        """
        print(f"🔍 Analyzing text ({len(config.entities)} entities): {text[:50]}...")
        
        # Step 1: ANALYZE - Find all PII
        results = self.analyzer.analyze(
            text=text,
            entities=config.entities,
            language=self.language
        )
        
        print(f"   Found {len(results)} PII entities")
        
        # Step 2: ANONYMIZE - Replace with placeholders
        redacted = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )
        
        return redacted.text
    
    def redact_documents(self, texts: List[str], config: EntityConfig) -> List[str]:
        """Batch process multiple text blocks"""
        return [self.redact_text(text, config) for text in texts]
