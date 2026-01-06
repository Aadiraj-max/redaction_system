"""Presidio PII Redaction Engine"""
from typing import List
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from ..agent.prompt_interpreter import EntityConfig

class PresidioRedactor:
    """Wrapper for Presidio Analyzer and Anonymizer"""
    
    def __init__(self, language: str = 'en'):
        print(f"🔧 Initializing PresidioRedactor (language: {language})")
        self.language = language
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def analyze(self, text: str, entities: List[str], score_threshold: float = 0.3) -> List[RecognizerResult]:
        """Step 1: Scan for PII candidates"""
        return self.analyzer.analyze(
            text=text,
            entities=entities,
            language=self.language,
            score_threshold=score_threshold
        )
    
    def anonymize(self, text: str, analyzer_results: List[RecognizerResult]) -> str:
        """Step 2: Replace PII with placeholders"""
        if not analyzer_results:
            return text
            
        result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )
        return result.text

    def redact_text(self, text: str, config: EntityConfig) -> str:
        """Legacy method for simple redaction (no validation)"""
        results = self.analyze(text, config.entities)
        return self.anonymize(text, results)
