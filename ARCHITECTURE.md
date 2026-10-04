# Architecture

```mermaid
flowchart TD
    U[User: question + India/International toggle] --> API[POST /api/ask]
    API --> G{ACCESS_CODE set?}
    G -- wrong/missing --> X[401]
    G -- ok/not set --> T[Keyword topic routing: 13 topics]
    T --> C{India + patent or formulation question, no clarifications yet?}
    C -- yes --> Q[Return 3 clarification questions]
    Q --> U
    C -- no --> CL[Classify: classical, proprietary, new, phytopharmaceutical, aahar, cosmetic]
    CL --> R[Retrieve inside chosen jurisdiction only: forced sources by category/topic + BM25 ranking]
    R --> A{Enough evidence? topic matched or 2+ query terms and BM25 above threshold}
    A -- no --> AB[Abstain: 'I will not guess' + escalation offer]
    A -- yes --> EX[Extract best sentences from stored passages, number citations]
    EX --> ABS[Add ABS checklist if ABS topic or new/phyto/proprietary; add cited sources to list]
    ABS --> CF[Confidence: high/medium/low with reasons; caps for drafts, International, patent, conflicts]
    CF --> OUT[JSON result]
    AB --> OUT
    OUT --> DB[(SQLite: audit log + result JSON)]
    OUT --> UI[Single HTML page: answer, sources, trail]
    UI --> ESC[POST /api/escalate -> case JSON saved in SQLite, downloaded]
    UI --> REP[GET /api/report/id -> .md]
```

## Language layer
`i18n.py` expands Devanagari questions with English search terms before routing and BM25, then localises the response (UI strings, reasons, notes, Hindi summaries from `corpus_hi.py`). The audit log, report and case file stay English.

## Components
- `corpus.py`: 33 hand-written summaries (23 India, 10 International) with verification metadata. Single source of truth for passages.
- `app.py`: topic routing, a small BM25 (k1=1.5, b=0.75, light plural stemming, one index per jurisdiction), answer assembly, confidence rules, Flask routes, SQLite.
- `static/index.html`: one page, no external resources.
- `eval.py`: 23 development tests via Flask's test client.

## Design rules enforced in code
- Each jurisdiction has its own BM25 index and candidate pool; `build_answer` asserts every source matches the chosen jurisdiction.
- Answers are sentences copied from stored summaries, never generated text.
- Every citation number maps to a source in the list; ABS checklist sources are appended to the list if missing.
- Confidence is a level plus reasons. No numeric score.
