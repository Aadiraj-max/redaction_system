from presidio_analyzer import PatternRecognizer, Pattern

# Your CustomEntityPatterns class should be defined in the same file
class CustomEntityPatterns:
    # PAN: Format AAAAA0000A
    PAN_PATTERN = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
    
    # Aadhaar: 12 digit number
    AADHAAR_WITH_SPACES = r"\b\d{4}\s\d{4}\s\d{4}\b"
    AADHAAR_WITHOUT_SPACES = r"\b\d{12}\b"
    
    # IFSC: Format AAAA0XXXXXX
    IFSC_PATTERN = r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    
    # GST: 15 character format
    GST_PATTERN = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}\b"
    
    # CIN: Correct format L12345XX2010XXX123456
    CIN_PATTERN = r"\b[A-Z]{1}\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b"
    
    # Bank Account: 9-18 digit numbers
    BANK_ACCOUNT_PATTERN = r"\b\d{9,18}\b"



def register_custom_recognizers(analyzer):
    """Register all custom recognizers with Presidio analyzer."""
    
    # PAN
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="PAN",
        patterns=[Pattern("PAN_PATTERN", CustomEntityPatterns.PAN_PATTERN, 0.85)],
        context=["PAN", "Permanent Account Number", "pan number"]
    ))
    
    # Aadhaar
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="AADHAAR",
        patterns=[
            Pattern("AADHAAR_WITH_SPACES", CustomEntityPatterns.AADHAAR_WITH_SPACES, 0.9),
            Pattern("AADHAAR_WITHOUT_SPACES", CustomEntityPatterns.AADHAAR_WITHOUT_SPACES, 0.6)
        ],
        context=["Aadhaar", "AADHAR", "UID", "unique id"]
    ))
    
    # IFSC
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="IFSC",
        patterns=[Pattern("IFSC_PATTERN", CustomEntityPatterns.IFSC_PATTERN, 0.85)],
        context=["IFSC", "bank code", "branch code", "ifsc code"]
    ))
    
    # GST
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="GST_REGISTRATION",
        patterns=[Pattern("GST_PATTERN", CustomEntityPatterns.GST_PATTERN, 0.9)],
        context=["GST", "GSTIN", "tax identification"]
    ))
    
    # CIN
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="CIN",
        patterns=[Pattern("CIN_PATTERN", CustomEntityPatterns.CIN_PATTERN, 0.85)],
        context=["CIN", "corporate identification"]
    ))
    
    # Bank Account
    analyzer.registry.add_recognizer(PatternRecognizer(
        supported_entity="BANK_ACCOUNT",
        patterns=[Pattern("BANK_ACCOUNT_PATTERN", CustomEntityPatterns.BANK_ACCOUNT_PATTERN, 0.5)],
        context=["account", "account number", "a/c", "bank account"]
    ))
