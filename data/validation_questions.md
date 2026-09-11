# ASPICE Knowledge Graph — Validation Questions
# Version: 1.0
# Purpose: Test graph quality after LLM extraction
# How to use: Ask each question to the graph chat interface.
#             Record the answer and whether it is correct.

---

## How to Record Results

For each question, fill in:
- **Graph Answer**: what the graph returned
- **Correct**: Yes / Partial / No
- **Gap**: what was missing or wrong

---

## Category 1 — Process Structure (PAM 4.1)

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 1 | What are the base practices of SWE.1? | | | |
| 2 | What are the base practices of SWE.2? | | | |
| 3 | What are the base practices of MAN.3? | | | |
| 4 | What outcomes does SWE.2 have? | | | |
| 5 | What outcomes does SYS.3 have? | | | |
| 6 | What is the purpose of SUP.9? | | | |
| 7 | What is the purpose of MAN.5? | | | |
| 8 | Which processes belong to the SWE process group? | | | |
| 9 | Which processes belong to the Supporting category? | | | |
| 10 | Which processes belong to the MLE process group? | | | |

---

## Category 2 — Information Items (PAM 4.1)

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 11 | What information items does SWE.3 produce? | | | |
| 12 | What information items does SWE.1 produce? | | | |
| 13 | What information items does MAN.3 produce? | | | |
| 14 | What are the characteristics of information item 04-04 Software Architecture? | | | |
| 15 | Which processes produce the information item 17-00 Requirement? | | | |

---

## Category 3 — Capability Levels and Process Attributes (PAM 4.1)

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 16 | What is required to achieve CL2? | | | |
| 17 | What is required to achieve CL3? | | | |
| 18 | Which process attributes belong to CL2? | | | |
| 19 | What information items does PA 2.1 require as evidence? | | | |
| 20 | What generic practices apply to PA 2.1? | | | |
| 21 | What generic practices apply to PA 3.1? | | | |
| 22 | What achievements does PA 2.2 have? | | | |
| 23 | What does GP 2.1.1 require? | | | |
| 24 | What does GP 3.1.1 require? | | | |
| 25 | Which generic practices must be satisfied to achieve PA 2.1 achievement 2? | | | |

---

## Category 4 — Cybersecurity PAM (CS PAM 2.0)

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 26 | What is the purpose of MAN.7? | | | |
| 27 | What base practices does SEC.1 contain? | | | |
| 28 | What base practices does SEC.2 contain? | | | |
| 29 | What information items does SEC.1 produce? | | | |
| 30 | What information items does MAN.7 produce? | | | |
| 31 | Which base practice establishes traceability between threat scenarios and cybersecurity goals? | | | |
| 32 | What is the traceability chain from threat scenario to verification result? | | | |
| 33 | What cybersecurity controls does SEC.2 produce? | | | |
| 34 | What processes belong to the SEC process group? | | | |
| 35 | What is the difference between SEC.3 and SEC.4? | | | |

---

## Category 5 — Cross-Document and Cross-Process

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 36 | Which information items are shared between PAM 4.1 and CS PAM 2.0? | | | |
| 37 | Which PAM 4.1 processes does CS PAM 2.0 reference or extend? | | | |
| 38 | Which base practice in SWE.1 cross-references MAN.3? | | | |
| 39 | Which processes produce the Software Architecture information item 04-04? | | | |
| 40 | What is the relationship between SWE.2 and SEC.2? | | | |

---

## Category 6 — Assessment Readiness (Practical Use Cases)

| # | Question | Graph Answer | Correct | Gap |
|---|---|---|---|---|
| 41 | What evidence do I need to demonstrate CL2 for SWE.1? | | | |
| 42 | What work products does an assessor look for in SWE.3 at CL1? | | | |
| 43 | What base practices must be satisfied for SWE.2 Outcome 3? | | | |
| 44 | What generic practices apply across all processes at CL3? | | | |
| 45 | If a supplier claims CL2 for MAN.3, what evidence should I request? | | | |

---

## Scoring Summary (fill in after testing)

| Category | Questions | Correct | Partial | Wrong |
|---|---|---|---|---|
| 1 Process Structure | 10 | | | |
| 2 Information Items | 5 | | | |
| 3 Capability Levels and PAs | 10 | | | |
| 4 Cybersecurity PAM | 10 | | | |
| 5 Cross-Document | 5 | | | |
| 6 Assessment Readiness | 5 | | | |
| **Total** | **45** | | | |

---

## Overall Graph Quality Score

```
Score = (Correct + 0.5 × Partial) / Total × 100

Target for POC: > 60%
Target for publication: > 80%
```

Actual score: _____ %

---

## Gaps Identified (summary of what needs manual correction)

List the top issues found during validation:

1.
2.
3.
4.
5.

---

## Manual Corrections Made

Track what you fixed in Neo4j after validation:

| Date | Node/Relationship | What Was Fixed |
|---|---|---|
| | | |
