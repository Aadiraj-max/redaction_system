#!/usr/bin/env python3
"""Test Orchestrator End-to-End"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.redaction_system.orchestrator import Orchestrator

def main():
    print("🚀 ORCHESTRATOR TEST - STEP 3\n")
    
    # Initialize
    orchestrator = Orchestrator()
    
    # Create test files
    create_test_files()
    
    # Test each format
    tests = [
        ('test_input.md', 'redact names'),
        ('test_input.txt', 'redact emails and phones'),
    ]
    
    for input_file, prompt in tests:
        if Path(input_file).exists():
            try:
                output = orchestrator.redact_file(input_file, prompt)
                print(f"✅ Redacted: {output}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")

def create_test_files():
    """Create sample files for testing"""
    # Markdown
    md_content = """# Contact Information

John Smith works at Microsoft Corporation.
Email: john.smith@microsoft.com
Phone: 555-123-4567

Jane Doe is a developer.
Email: jane.doe@company.com
Phone: 555-987-6543
"""
    Path('test_input.md').write_text(md_content)
    
    # Text (for Markdown parser test)
    txt_content = "Contact: john@example.com or call 555-1234"
    Path('test_input.txt').write_text(txt_content)

if __name__ == "__main__":
    main()
