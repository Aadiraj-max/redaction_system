# Architecture & Problem Statements

**Last Updated:** 2026-01-07 | **Maintainer:** Aditya Rajhans

---

## Table of Contents
1. [Code Architecture](#code-architecture)
2. [Code-Level Problems](#code-level-problems)
3. [Architectural/Design Problems](#architecturaldesign-problems)
4. [Problem Resolution Log](#problem-resolution-log)

---

## Code Architecture

### Project Structure
```
redaction_system/
├── src/redaction_system/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── prompt_interpreter.py      [JOB 1 & JOB 2: Intent + Validation]
│   ├── redactor/
│   │   ├── __init__.py
│   │   ├── presidio_wrapper.py       [3-Layer Scanner: Spacy + Regex + Lists]
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── orchestrator.py           [Pipeline Coordinator]
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py             [PDF → Text Chunks]
│   │   ├── docx_parser.py            [DOCX → Text Chunks]
│   │   ├── excel_parser.py           [XLSX/XLS/CSV → Text Chunks]
│   │   ├── markdown_parser.py        [MD → Text Chunks]
│   │   ├── text_parser.py            [TXT → Text Chunks]
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py               [Click CLI Entry Points]
│   │   ├── interactive_preview.py    [Terminal UI for Manual Review]
│   │   ├── preview.py                [Preview Handler]
│   │   ├── utils.py                  [CLI Helpers]
├── requirements.txt
├── setup.py
├── PROJECT_PLAN.md
├── ARCHITECTURE_AND_PROBLEMS.md (THIS FILE)
├── tests/
│   ├── test_agent.py
│   ├── test_orchestrator.py
│   ├── data/
│   │   ├── analyst_test.txt
│   │   ├── test_input.txt
│   │   ├── test_input.md
```

### Core Data Flow

```
User Input: File + Prompt
    │
    │ [Parser Layer]
    │ Converts file format to text chunks
     │
     │
     ✂───[Job 1: Interpret Prompt]
          Llama → "Hide personal data" → ["PERSON", "EMAIL", "PHONE"]
          EntityConfig output
                 │
                                                                  │
                  For Each Chunk:                                                        │
                                                                                                                                                                                                                                                              │
                  [Job 1.5: Presidio Analyze]                                                   │
                    Text → Spacy/Regex/Lists → Candidates                        │
                                                                                │
                  Split Results:                                                            │
                    - Certain (≥0.7) → Queue for redaction                        │
                    - Uncertain (<0.7) → Job 2                                  │
                                                                                │
                  [Job 2: Validate Uncertain]                                                    │
                    Llama reviews with context → TRUE POSITIVES                    │
                                                                                │
                  [Anonymizer]                                                              │
                    Combine: Certain + Validated → Redact Text                      │
                                                                           │
                                                                       │
             Output: Redacted File                                                   │
                                                                   │
```

### Module Responsibilities

| Module | Primary Responsibility | Key Classes/Functions |
|--------|------------------------|------------------------|
| **agent/** | LLM-powered decision making | `interpret_prompt()`, `validate_candidates()`, `EntityConfig` |
| **redactor/** | PII detection & anonymization | `PresidioRedactor.analyze()`, `.anonymize()` |
| **orchestrator/** | Pipeline orchestration & chunk management | `Orchestrator.redact_file()`, validation loop |
| **parsers/** | File format conversion to text | Parser classes for each format |
| **cli/** | User interface & commands | Click commands, interactive UI |

---

## Code-Level Problems

### Problem 1: PDF Text Extraction Reliability ⚠️ OPEN

**Type:** Code Issue  
**Severity:** Medium  
**Status:** Open (Not blocking MVP)

**Description:**
PDF text extraction via `pdfplumber` can fail on:
- Scanned/image-based PDFs (OCR needed)
- PDFs with unusual encoding
- PDFs with embedded images containing text

**Current Solution:**
- Using `pdfplumber` which handles most text PDFs well
- Graceful error handling in `PDFParser.parse()`

**What’s Needed:**
- OCR integration (Tesseract/EasyOCR) for scanned PDFs
- Better error messages to guide user
- Fallback to alternative extraction methods

**Timeline:** Phase 5 enhancement

---

### Problem 2: Excel Cell-to-Text Mapping Ambiguity ⚠️ OPEN

**Type:** Code Issue  
**Severity:** Low  
**Status:** Open (Workaround in place)

**Description:**
When redacting Excel files, it’s unclear how to map redacted cell values back to the original grid. Current implementation treats rows as text chunks, losing structure.

**Current Solution:**
- ExcelParser flattens to row-based text
- Loses column structure and formulas
- Acceptable for Phase 4 MVP

**What’s Needed:**
- Cell-level tracking with coordinates
- Preserve formulas & formatting
- Reconstruct exact spreadsheet structure

**Timeline:** Phase 5 enhancement

---

### Problem 3: Environment Variable Validation ⚠️ OPEN

**Type:** Code Issue  
**Severity:** Low  
**Status:** Open (Documented in README)

**Description:**
If `OLLAMA_HOST` or `OLLAMA_MODEL` are missing, errors are unclear.

**Current Solution:**
- Users must set `.env` manually
- Some error logging in place

**What’s Needed:**
- Validation at startup
- Clear error message if variables missing
- Auto-detect Ollama if running locally

**Timeline:** Phase 4.3 quick fix (30 mins)

---

## Architectural/Design Problems

### Problem 1: Presidio’s "Blindness" to Organization Names 🚨 OPEN

**Type:** Architectural (Inherent to Spacy NER)  
**Severity:** High  
**Status:** Identified, Workaround Planned  
**Phase Identified:** Phase 4.2

**Description:**
Presidio (using Spacy NER) fails to detect organization names like "Google", "Apple", "Microsoft" even with very low confidence thresholds.

**Root Cause:**
- Spacy NER model trained on CoNLL 2003 dataset
- Doesn’t "see" organizations well in certain contexts
- The problem is **Recall** (missing entities), not precision
- If Spacy returns 0 candidates, Job 2 (Llama) never gets to validate

**Current Impact:**
- ORG entity recall estimated at 40-50% (vs. 95%+ for PERSON)
- If project requires high ORG detection, this is critical
- If project only needs PERSON/EMAIL/PHONE, this is acceptable

**Solutions Evaluated:**

1. **Pattern-Based Expansion** ✅ Considered
   - Add 100+ company name regex patterns
   - Cost: 2-3 hours
   - Risk: Pattern overlap causes confidence degradation (we observed this)
   - **Verdict:** Not recommended. Causes more problems than it solves.

2. **Hybrid NER (BERT + Presidio)** ✅✅ Recommended
   - Run BERT transformer model in parallel with Presidio
   - BERT catches ORGs that Spacy misses
   - Merge results intelligently
   - Cost: 2-3 hours
   - Latency: +200-500ms per document
   - **Verdict:** This is the production solution. Implement in Phase 4.3 if needed.

3. **Custom NER Fine-tuning** ❌ Rejected (Out of Scope)
   - Requires labeled training data
   - Requires ML pipeline setup
   - Cost: 2-4 weeks
   - **Verdict:** Too expensive for MVP. Consider for v2.0.

**Decision Point (Phase 4.2 Testing):**
- If Phase 4.2 testing shows ORG recall < 50% AND matters to your use case:
  - Implement Hybrid NER in Phase 4.3 (2-3 hours)
  - Re-test. Expected improvement: 40% → 80%+ recall
- If ORG detection not critical:
  - Document as known limitation
  - Move to Phase 5
  - Schedule Hybrid NER as Phase 5 enhancement

**Current Status:**
- [ ] Phase 4.2: Measure actual ORG recall on large documents
- [ ] Phase 4.3: Decide on Hybrid NER based on results
- [ ] Phase 5: Implement Hybrid NER if not done in 4.3

---

### Problem 2: LLM Model Fatigue / Drift 🔁 RESOLVED ✅

**Type:** Architectural (LLM Behavior)  
**Severity:** Medium (if not handled)  
**Status:** RESOLVED  
**Phase Resolved:** Phase 3 (Design), Phase 4.1 (Testing)

**Original Concern:**
If Llama processes 100+ candidates in a single prompt or maintains conversation history, it might:
- Drift toward always saying "Yes" (Mode Collapse)
- Lose focus on middle items in a long list (Lost in the Middle)
- Forget system instructions over time

**How It Was Resolved:**

1. **Stateless API Calls** ✅
   - Each validation call is fresh (no chat history)
   - Llama has no memory of previous decisions
   - Prevents drift/fatigue
   - Code: `prompt_interpreter.py` uses fresh `requests.post()` calls

2. **Small Batch Processing** ✅
   - Chunk-based processing (paragraph-level)
   - Each chunk typically 1-5 validation items
   - Keeps attention focused
   - Code: `orchestrator.py` validates per-chunk

3. **Reset Between Calls** ✅
   - Llama doesn’t see the previous chunk’s context
   - Fresh mental state for each chunk

**Why It Works:**
- Stateless = No fatigue
- Small batches = High attention
- Reset = Fresh start

**Testing Result:**
Ran analyst_test.txt repeatedly. No accuracy degradation observed.

**Status:** ✅ No further action needed. Architecture handles this correctly.

---

### Problem 3: Pattern Confusion / Confidence Degradation 📄 PARTIALLY RESOLVED

**Type:** Architectural (Presidio Behavior)  
**Severity:** Low-Medium  
**Status:** Identified, Mitigated, Monitoring  
**Phase Identified:** Phase 4.2

**Original Concern:**
When adding multiple regex patterns to Presidio, confidence scores for valid entities drop. This is not "fatigue" but rather "noise."

**Root Cause:**
Presidio calculates scores by averaging/weighing multiple recognizers:
- If you add a weak regex pattern, it conflicts with strong Spacy detection
- Confidence = average(Spacy_score, Weak_Regex_score)
- Result: High Spacy score (0.95) + Weak Regex (0.2) = Average (0.575) - below our 0.7 threshold!

**How It Was Mitigated:**
1. **Avoided Pattern Expansion** ✅
   - Didn’t add messy regex patterns
   - This keeps scoring clean

2. **Rely on Spacy Quality** ✅
   - Spacy is good at detecting PERSON/EMAIL/PHONE
   - Upgrade Spacy model rather than add patterns

3. **Keep Threshold Tuning**
   - If pattern confusion persists, we adjust threshold from 0.7 to 0.6
   - But better to avoid the problem than manage it

**Current Mitigation:**
- [x] Don’t add weak regex patterns
- [x] Rely on Spacy quality
- [ ] Monitor Phase 4.2 tests for confidence degradation
- [ ] If observed, consider Spacy model upgrade

**Status:** ✅ Mitigated. Requires monitoring during Phase 4.2 testing.

---

### Problem 4: US-Centric Entity Patterns 🗺️ OPEN

**Type:** Architectural (Presidio Default Config)  
**Severity:** Medium (for international users)  
**Status:** Identified, Not Critical for MVP  
**Phase Identified:** Phase 1

**Description:**
Presidio’s default recognizers are biased toward US formats:
- Phone: `(XXX) XXX-XXXX` (US format), misses `+XX XXXX XXXX` (international)
- Date: MM/DD/YYYY prioritized over DD/MM/YYYY
- Email: Works well (international)

**Current Impact:**
- MVP targets English-language documents
- If processing international documents, phone/date detection will miss some

**Solution:**
Add region/language configuration:
```python
redactor = PresidioRedactor(region="IN")  # India-specific patterns
# Or
redactor = PresidioRedactor(region="EU")  # EU-specific patterns
```

**Timeline:** Phase 5 enhancement (Multi-language support)

**Status:** ⏳ Documented. Not blocking MVP.

---

## Problem Resolution Log

### Summary Table

| Problem | Type | Status | Resolution | Timeline |
|---------|------|--------|------------|----------|
| Presidio Blindness (ORG) | Arch | ⏳ Investigating | Hybrid NER planned | Phase 4.3 (Conditional) |
| LLM Fatigue | Arch | ✅ Resolved | Stateless + Batching | Phase 3 |
| Pattern Confusion | Arch | ✅ Mitigated | Avoid weak patterns | Ongoing |
| US-Centric Bias | Arch | ⏳ Deferred | Region config (Phase 5) | Phase 5 |
| PDF OCR | Code | ⏳ Deferred | Tesseract integration | Phase 5 |
| Excel Mapping | Code | ⏳ Deferred | Cell-level tracking | Phase 5 |
| Env Validation | Code | ⏳ Deferred | Auto-detection (Phase 4.3) | Phase 4.3 |

---

## Next Steps & Decision Points

### Phase 4.2 (NOW): Testing & Measurement

**Critical Metrics to Collect:**
- [ ] PERSON recall: ____% (Target: >90%)
- [ ] EMAIL recall: ____% (Target: >95%)
- [ ] PHONE recall: ____% (Target: >90%)
- [ ] ORG recall: ____% (Baseline, expect 40-50%)
- [ ] Processing time per document: ____seconds (Target: <30s)
- [ ] Any edge cases or failures: ____

**Decision Gate (Phase 4.2 → 4.3):**
- If ORG recall < 50% AND critical: Implement Hybrid NER (3 hours)
- If all recalls > 90%: Proceed to Phase 5
- If unexpected issues: Document and patch

---

## How to Use This Document

1. **For Understanding System State:**
   - Read Problem tables to understand what’s known/unknown
   - Check status badges: ✅ Resolved | ⏳ Open | ⚠️ Mitigated

2. **For Decision Making:**
   - Go to "Decision Point" sections
   - Check "Timeline" for when to act
   - Review solutions and trade-offs

3. **For Contributing:**
   - If you fix a problem, update its status here
   - Add new problems as they’re discovered
   - Update Phase Timeline as you progress

4. **For Future Reference:**
   - This document creates institutional memory
   - Explains why certain decisions were made
   - Prevents repeating past mistakes

---

**Last Reviewed:** 2026-01-07  
**Next Review:** After Phase 4.2 testing completion  
**Maintainer:** Aditya Rajhans (@Aadiraj-max)
