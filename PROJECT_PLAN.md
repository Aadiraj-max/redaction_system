# Project Plan: Privacy-First Redaction System

**Last Updated:** 2026-01-07 | **Current Phase:** 4.2 (Testing & Validation)

---

## 📋 Project Overview

A **Privacy-First Data Redaction System** that intelligently anonymizes Personally Identifiable Information (PII) across multiple file formats using:
- **Presidio (Microsoft)** - Analyzer & Anonymizer
- **Llama 3.1 (via Ollama)** - Intelligent validation & intent interpretation
- **Multi-Format Support** - PDF, DOCX, XLSX, Markdown, TXT

**Vision:** Create a base MVP that matches or exceeds market-leading redaction tools while maintaining privacy-first principles (all processing local, no cloud dependencies).

---

## 🎯 Phase Breakdown & Completion Status

### Phase 1: Agent Integration ✅ COMPLETE
**Goal:** Build the "brain" - LLM-based intent interpretation

**What was built:**
- `prompt_interpreter.py` with Job 1 (Interpret Intent) and Job 2 (Analyst Validation)
- Natural language prompt interpretation (e.g., "Hide personal data" → `["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]`)
- Context-aware validation of uncertain entities using Llama

**Status:** ✅ Working perfectly. Stateless design prevents model fatigue.

---

### Phase 2: Presidio Integration ✅ COMPLETE
**Goal:** Build the "scanner" - Multi-layer PII detection

**What was built:**
- `presidio_wrapper.py` wrapping Analyzer & Anonymizer engines
- Three-layer architecture: Spacy NER + Regex Patterns + Entity Lists
- Configurable score thresholds and entity type filtering

**Status:** ✅ Working well for PERSON, EMAIL, PHONE, DATE. ⚠️ Known limitation: Blind to ORG entities (See Architecture_and_Problems.md)

---

### Phase 3: Orchestrator Integration ✅ COMPLETE
**Goal:** Wire everything together - Job 1 → Presidio → Job 2 → Anonymize

**What was built:**
- `orchestrator.py` - Main pipeline coordinator
- Chunk-based processing (prevents model fatigue)
- Two-path filtering: Certain (≥0.7) → Immediate redaction, Uncertain (<0.7) → Llama validation
- Seamless file reassembly

**Status:** ✅ Fully functional. Architecture handles fatigue prevention correctly.

---

### Phase 4: UI/UX & CLI + File Parsing 🔄 IN PROGRESS

#### Phase 4.1: Basic CLI & Text Parser ✅ COMPLETE (2026-01-05)
**What was built:**
- `TextParser` for `.txt` file support
- CLI commands: `redact <file> "<prompt>" [output]"`
- Interactive approval workflow
- Test infrastructure

**Status:** ✅ Working. Tested on small files.

---

#### Phase 4.2: Large-Scale Document Testing 🔄 CURRENT (2026-01-07 → TBD)
**Goal:** Validate MVP on production-scale documents (50-100 pages)

**Objectives:**
- [ ] Create/obtain 50-100 page test documents (PDF, DOCX, TXT with realistic PII)
- [ ] Run end-to-end redaction pipeline
- [ ] Measure accuracy metrics:
  - [ ] PERSON recall: Target >90%
  - [ ] EMAIL recall: Target >95%
  - [ ] PHONE recall: Target >90%
  - [ ] ORG recall: Baseline (likely 40-50% due to Spacy limitation)
  - [ ] Overall accuracy: Target >90%
- [ ] Measure performance:
  - [ ] Processing speed: Target <30 seconds per document
  - [ ] Memory usage: Track and optimize
- [ ] Identify real-world edge cases
- [ ] Document findings

**Current Status:**
- **2026-01-07:** Legacy test data cleared. Ready for fresh document generation.
- **Blockers:** Need large test documents (help needed from user)

**Timeline:** Expected completion: 2026-01-08

---

#### Phase 4.3: Accuracy Improvements & Finalization (TBD → TBD)
**Goal:** Address limitations found in Phase 4.2 testing

**Potential Actions (based on Phase 4.2 results):**

**Scenario A: If ORG Recall < 50% AND Matters to MVP**
- Implement Hybrid NER (BERT + Presidio parallel processing)
- Time: 2-3 hours
- Re-test
- Expected improvement: ORG recall 40% → 80%+

**Scenario B: If All Recalls > 90%**
- No changes needed
- Document known limitations
- Move to Phase 5

**Scenario C: If Pattern Confusion or Model Fatigue Detected**
- Improve chunking strategy
- Add Chain-of-Thought (CoT) to Job 2 prompts
- Time: 1-2 hours

**Scenario D: If Performance Issues**
- Implement batching optimization
- Explore quantized Llama models
- Time: 2-4 hours

**Timeline:** Expected completion: 2026-01-08 (if no changes needed) to 2026-01-09 (if Hybrid NER needed)

---

### Phase 5: Scaling & Advanced Features 📅 PLANNED
**Goal:** Production-readiness, web interface, advanced accuracy

**Planned Components:**
1. **Web UI** (FastAPI + React)
2. **Distributed Processing** (Celery/Ray for multi-document batches)
3. **RAG Integration** (Vector DB for custom entity learning)
4. **Hybrid NER Upgrade** (If not done in Phase 4.3)
5. **Performance Optimization** (Caching, quantization, batch processing)
6. **Multi-Language Support** (Non-English redaction)

**Timeline:** TBD (Post Phase 4 completion)

---

## 📊 Metrics & Goals

### MVP Success Criteria
- ✅ **Multi-Format Support:** PDF, DOCX, XLSX, MD, TXT
- ✅ **English Language:** Full support
- ✅ **Natural Language Intent:** User can say "hide personal data" instead of listing entities
- ⏳ **Accuracy:** >90% on PERSON/EMAIL/PHONE, baseline on ORG
- ⏳ **Speed:** <30 seconds per 50-page document
- ✅ **Privacy:** 100% local processing, no cloud APIs

### Phase 5+ Goals
- **Accuracy:** >95% across all entity types
- **Speed:** <10 seconds per 50-page document
- **Scalability:** Handle 1000+ documents in batch mode
- **Learning:** System improves with feedback (RAG)

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **NER/PII Detection** | Microsoft Presidio | Primary scanner |
| **Context Understanding** | Spacy (en_core_web_sm) | Named entity recognition |
| **Intent Interpretation** | Llama 3.1 (via Ollama) | Intelligent validation |
| **PDF Processing** | pdfplumber | Text extraction |
| **DOCX Processing** | python-docx | Word document handling |
| **Excel Processing** | openpyxl | Spreadsheet handling |
| **CLI** | Click | Command-line interface |
| **Deployment** | Local + Docker (future) | Privacy-first hosting |

---

## 📁 Deliverables Checklist

### Phase 1-3 Deliverables ✅
- [x] `src/redaction_system/agent/prompt_interpreter.py`
- [x] `src/redaction_system/redactor/presidio_wrapper.py`
- [x] `src/redaction_system/orchestrator/orchestrator.py`
- [x] `src/redaction_system/parsers/*.py` (all format parsers)
- [x] `src/redaction_system/cli/commands.py`
- [x] `requirements.txt` with all dependencies
- [x] `setup.py` for package installation

### Phase 4 Deliverables 🔄
- [x] Phase 4.1 Complete: Text parser, CLI working
- [ ] Phase 4.2 In Progress: Large-scale testing, accuracy metrics
- [ ] Phase 4.3 Pending: Performance optimization, potential Hybrid NER
- [ ] Documentation: ARCHITECTURE_AND_PROBLEMS.md
- [ ] Documentation: This file (PROJECT_PLAN.md)
- [ ] Phase log: PHASE_LOG.md (Updated after each phase)

### Phase 5 Deliverables 📅
- [ ] Web API (FastAPI)
- [ ] Web UI (React/Vue)
- [ ] Docker setup
- [ ] Performance benchmarks
- [ ] RAG integration

---

## 🔗 Related Documents

- **ARCHITECTURE_AND_PROBLEMS.md** - Code structure, known issues, and resolutions
- **PHASE_LOG.md** - Detailed log of what was done in each phase
- **Deep Dives:**
  - `rag_vs_hybrid_vs_presidio_deep_dive.md` - Technical comparison of solutions
  - `phase_4_2_status_analysis.md` - Presidio recall limitation analysis

---

## 📝 Notes for Next Developer (or Future You)

1. **The "Blind Spot" Problem:** Presidio (Spacy NER) doesn't detect organization names well. This is a known limitation of the Spacy model, not a code bug. Hybrid NER (BERT + Presidio) is the planned fix for Phase 5.

2. **Model Fatigue Prevention:** Llama fatigue is prevented by:
   - Stateless API calls (no chat history)
   - Small batch processing (chunk-based)
   - These safeguards are already in place.

3. **Accuracy Trade-offs:**
   - Presidio prioritizes precision (avoids false positives)
   - Job 2 adds recall (finds missed entities)
   - Together they achieve balanced accuracy

4. **Next Critical Decision:** Results from Phase 4.2 testing will determine whether Hybrid NER is needed in Phase 4.3. Monitor ORG recall specifically.

---

## 🚀 How to Contribute

1. **For Phase 4.2 Testing:**
   - Create/provide 50-100 page test documents
   - Run: `python -m redaction_system.cli.commands redact <file> "<prompt>"`
   - Log accuracy metrics
   - Document edge cases

2. **For Phase 4.3 Improvements:**
   - Based on Phase 4.2 results, implement one of the scenarios above
   - Update this document with findings
   - Create pull request with improvements

3. **General:**
   - Update ARCHITECTURE_AND_PROBLEMS.md when adding features
   - Keep PHASE_LOG.md current with decisions and findings
   - Test thoroughly before merging

---

**Status Summary:** MVP Logic Complete. Awaiting large-scale validation. Ready for Phase 4.2 testing. 🎯
