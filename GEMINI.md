# Project Context: Redaction System

## 1. Project Status
**Current Phase: 4.3 - Custom Recognizers & Refinement (Next Step)**
-   **Previous:** Phase 4.2 (Large-Scale Testing) - **COMPLETED**.
    -   Tested on `yes_bank_q2_fy26_report.txt`.
    -   **Result:** Core PII (Names, Emails, Dates) redacted successfully.
    -   **Issues Identified:** 
        -   Missed Indian-specific PII (PAN, Aadhaar formats).
        -   Missed 15-digit Bank Account Numbers.
        -   Partial redactions (e.g., `XXXX-1234`) were left as-is (acceptable, but noted).

## 2. Quick Start (Developer Context)
-   **Git Root:** `code/redaction_project` (NOT the project root).
-   **Virtual Env:** `.\venv\Scripts\activate`
-   **Install/Update:** `pip install -e code/redaction_project`
-   **Run Redaction:**
    ```powershell
    redact file "tests/data/yes_bank_q2_fy26_report.txt" --prompt "redact all financial PII" --no-preview
    ```

## 3. Architecture Overview
-   **Goal:** Privacy-first, local anonymization (No cloud APIs).
-   **Pipeline:** `Orchestrator` -> `Parser` -> `Job 1 (Intent)` -> `Presidio (Scan)` -> `Job 2 (Validation)` -> `Reassembly`.
-   **Key Components:**
    -   **Agent (`src/redaction_system/agent`):** Uses `llama3.1:8b` (Ollama) for:
        1.  **Prompt Interpretation:** "redact emails" -> `['EMAIL_ADDRESS']`.
        2.  **Analyst Mode:** Reviews low-confidence (<0.7) Presidio matches using context.
    -   **Redactor (`src/redaction_system/redactor`):** Wraps Microsoft Presidio.
    -   **CLI (`src/redaction_system/cli`):** `click`-based with `textual` TUI for preview.

## 4. Known Limitations & Roadmap
1.  **Indian PII:** Need to add custom `Presidio` recognizers (Regex/Context) for PAN, Aadhaar, and IFSC.
2.  **Context Window:** Large files can saturate agent context.
3.  **15-Digit Accounts:** Default financial recognizers are US/EU centric.

## 5. Directory Map
-   `code/redaction_project/`: **GIT REPO ROOT**. Contains source code.
-   `tools/`: Helper scripts.
-   `tests/data/`: Test documents (e.g., `yes_bank_q2_fy26_report.txt`).
