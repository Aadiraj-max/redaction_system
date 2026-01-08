from dataclasses import dataclass
from typing import List, Dict
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EntityConfig:
    entities: List[str]
    confidence: float = 0.95
    reasoning: str = ""

def interpret_prompt(user_input: str) -> EntityConfig:
    """
    Intelligently interpret user's redaction intent.
    FLEXIBLE - handles many variations naturally.
    """
    
    ollama_host = os.getenv("OLLAMA_HOST")
    model = os.getenv("OLLAMA_MODEL")
    
    # SMART system prompt (context + reasoning, not hardcoded rules)
    system_prompt = """You are an expert PII identification system.

TASK: Extract PII entity types that match the user's redaction/anonymization intent.

AVAILABLE ENTITY TYPES:
- PERSON (names, individuals)
- EMAIL_ADDRESS (email addresses)
- PHONE_NUMBER (phone numbers)
- US_SSN (social security numbers)
- CREDIT_CARD (credit cards, payment cards)
- DATE_TIME (dates, times, timestamps)
- ORGANIZATION (companies, institutions)
- IP_ADDRESS (IP addresses)
- URL (websites, URLs)
- LOCATION (places, addresses, cities, countries)
- PAN (Permanent Account Number, India)
- AADHAAR (Aadhaar unique ID, India)
- BANK_ACCOUNT (Bank account numbers)
- IFSC (IFSC bank code)
- GST_REGISTRATION (GST registration number)
- CIN (Corporate Identification Number)


INSTRUCTIONS:
1. UNDERSTAND THE USER'S INTENT (what are they really trying to protect?)
2. INFER RELATED ENTITY TYPES intelligently
3. Think about context:
   - "Personal info" or "identities" → PERSON, EMAIL, PHONE, LOCATION
   - "Financial" or "payment" → CREDIT_CARD, US_SSN
   - "Contact info" → EMAIL_ADDRESS, PHONE_NUMBER, LOCATION
   - "Everything private" → All types
   - "Specific type" → Just that type
4. Be smart about variations:
   - "redact names" = PERSON
   - "hide personal data" = PERSON, EMAIL, PHONE, LOCATION
   - "anonymize everything" = All entity types

OUTPUT: ONLY valid JSON array of entity type names. NO conversational text.
Examples: ["PERSON"], ["EMAIL_ADDRESS", "PHONE_NUMBER"], ["PERSON", "EMAIL_ADDRESS", "CREDIT_CARD"]

If nothing matches: []"""

    payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\nUser request: {user_input}",
        "stream": False,
        "format": "json",  # Force JSON mode if supported by the model version
        "options": {
            "temperature": 0.1,  # Low = consistent, not random
            "num_predict": 100
        }
    }
    
    try:
        response = requests.post(
            f"{ollama_host}/api/generate", 
            json=payload, 
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        entities_str = result['response'].strip()
        
        print(f"LLM Response: {entities_str}")

        # Attempt to extract JSON from the string if it contains extra text
        try:
            # Find the first '[' or '{'
            start_list = entities_str.find('[')
            start_dict = entities_str.find('{')
            
            start_index = -1
            end_index = -1
            
            # Determine if we are looking for a list or a dict
            if start_list != -1 and (start_dict == -1 or start_list < start_dict):
                # It's likely a list
                start_index = start_list
                end_index = entities_str.rfind(']') + 1
            elif start_dict != -1:
                # It's likely a dict
                start_index = start_dict
                end_index = entities_str.rfind('}') + 1
                
            if start_index != -1 and end_index != -1:
                entities_str = entities_str[start_index:end_index]
        except:
            pass
        
        # Parse JSON
        entities = json.loads(entities_str)
        
        # Normalize input to a list of strings
        if isinstance(entities, dict):
            # Case: {"entities": ["PERSON", ...]}
            if "entities" in entities:
                entities = entities["entities"]
            # Case: {"response": ["PERSON", ...]}
            elif "response" in entities:
                entities = entities["response"]
            # Case: {"entity_types": ["PERSON", ...]}
            elif "entity_types" in entities:
                entities = entities["entity_types"]
            # Case: {"PERSON": null, "EMAIL": null} -> Use keys
            else:
                entities = list(entities.keys())
        
        # Ensure it is now a list
        if not isinstance(entities, list):
             entities = [str(entities)]

        # Validate (only keep valid entity types)
        valid_entities = [
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", 
            "CREDIT_CARD", "DATE_TIME", "ORGANIZATION", 
            "IP_ADDRESS", "URL", "LOCATION", 
            "PAN", "AADHAAR", "BANK_ACCOUNT", "IFSC", "GST_REGISTRATION", "CIN"
        ]
        filtered_entities = [e for e in entities if e in valid_entities]
        
        return EntityConfig(
            entities=filtered_entities if filtered_entities else ["PERSON"],
            confidence=0.95,
            reasoning=f"Interpreted: {user_input}"
        )
        
    except Exception as e:
        print(f"Error: {e}. Using fallback.")
        return EntityConfig(
            entities=["PERSON"],
            confidence=0.0,
            reasoning="Fallback"
        )

def validate_candidates(candidates: List[Dict], context_text: str) -> List[int]:
    """
    Job 2: Analyst Mode. Review uncertain candidates and return the INDICES of valid ones.
    
    Returns: List of integers (indices in the candidates list that are TRUE positives)
    """
    if not candidates:
        return []
    
    ollama_host = os.getenv('OLLAMA_HOST')
    model = os.getenv('OLLAMA_MODEL')
    
    # Build candidate descriptions with their IDs
    candidate_desc = "\n".join([
        f"- ID: {i}, Text: '{c.get('text')}', Type: {c.get('entity_type')}, Context: '...{c.get('context', 'N/A')}...'"
        for i, c in enumerate(candidates)
    ])
    
    system_prompt = f"""You are an expert Data Privacy Analyst. Your job is to VALIDATE potential PII candidates.

Presidio flagged these with LOW confidence. Decide if they are TRUE PII based on context.

Candidates:
{candidate_desc}

RULES:
1. TRUE POSITIVE: Real person names, real account numbers, real PII
2. FALSE POSITIVE: Employee IDs (EMP-XXXX), generic patterns, non-sensitive terms
3. Look at the Context to decide

OUTPUT: JSON array of IDs that are TRUE positives.
Example: [0, 2, 3]
"""
    
    payload = {
        'model': model,
        'prompt': system_prompt,
        'stream': False,
        'format': 'json',
        'options': {'temperature': 0.0}
    }
    
    try:
        response = requests.post(f'{ollama_host}/api/generate', json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        valid_ids = json.loads(result['response'].strip())
        
        # Handle if LLM wrapped it in a dict
        if isinstance(valid_ids, dict):
            for k, v in valid_ids.items():
                if isinstance(v, list):
                    valid_ids = v
                    break
        
        if not isinstance(valid_ids, list):
            valid_ids = []
        
        # Validate indices are integers in range
        valid_ids = [i for i in valid_ids if isinstance(i, int) and 0 <= i < len(candidates)]
        
        if valid_ids:
            validated_texts = [candidates[i]['text'] for i in valid_ids]
            print(f"✓ Agent validated {len(valid_ids)} entities: {validated_texts}")
        
        return valid_ids  # Return list of INDICES, not dicts
        
    except Exception as e:
        print(f"✗ Agent validation failed: {e}")
        return []
