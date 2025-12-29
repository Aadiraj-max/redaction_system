# Update test_agent.py to test flexibility:
#!/usr/bin/env python3
"""End-to-end Agent + Redactor Integration Test"""
from src.redaction_system.agent import interpret_prompt
from src.redaction_system.redactor import PresidioRedactor

def main():
    print("🚀 PII REDACTION SYSTEM - STEP 2 TEST")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing Redactor...")
    redactor = PresidioRedactor(language='en')
    
    # Test cases
    tests = [
        ("redact names", "John Smith works at Microsoft Corp."),
        ("redact emails and phones", "Email john@example.com or call 555-123-4567."),
        ("anonymize personal info", "Jane Doe (jane@company.com) SSN: 123-45-6789.")
    ]
    
    for i, (prompt, text) in enumerate(tests, 1):
        print(f"\n📋 TEST {i}: '{prompt}'")
        print("-" * 45)
        
        # Agent: Decide what to redact
        config = interpret_prompt(prompt)
        print(f"🤖 Agent: {config.entities}")
        
        # Redactor: Process text
        redacted = redactor.redact_text(text, config)
        
        print(f"📄 Original:  {text}")
        print(f"🛡️  Redacted: {redacted}")
        print()
    
    print("🎯 STEP 2 COMPLETE! Ready for Orchestrator.")

if __name__ == "__main__":
    main()

