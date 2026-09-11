# ASPICE Knowledge Graph — Schema Definition
# Version: 1.0
# Based on: ASPICE PAM 4.1 + CS PAM 2.0
# Author: Sathiya Ramamoorthy
# Date: 2026-09-11

---

## Node Labels (13 total)

| Label | Description | Source |
|---|---|---|
| Document | The standard document itself | Both |
| ProcessCategory | Primary / Supporting / Organizational | PAM 4.1 |
| ProcessGroup | SWE, SYS, MAN, SEC etc | Both |
| Process | Individual process e.g. SWE.1, SEC.2 | Both |
| BasePractice | Specific activity within a process e.g. SWE.1.BP1 | Both |
| ProcessOutcome | Expected result of process performance | Both |
| InformationItem | Output indicator with numeric ID e.g. 04-04 | Both |
| DomainCharacteristic | CS-specific IIC extensions for shared IIs | CS PAM 2.0 |
| CapabilityLevel | CL0 to CL5 | PAM 4.1 |
| ProcessAttribute | PA 1.1 to PA 5.2 | PAM 4.1 |
| ProcessAttributeAchievement | Numbered achievements under each PA | PAM 4.1 |
| GenericPractice | GP 1.1.1 to GP 5.2.3 | PAM 4.1 |
| Note | Explanatory notes attached to base practices | Both |

---

## Node Properties

### Document
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | ASPICE_PAM_4.1 |
| title | string | YES | Automotive SPICE® Process Reference and Assessment Model |
| version | string | YES | 4.1 |
| date | string | YES | 2026-08-24 |
| status | string | YES | Released |
| publisher | string | YES | VDA Quality Management Center |
| type | string | YES | base OR supplement |

### ProcessCategory
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | Primary |
| name | string | YES | Primary processes category |
| source_document | string | YES | ASPICE_PAM_4.1 |

### ProcessGroup
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | SWE |
| name | string | YES | Software Engineering process group |
| source_document | string | YES | ASPICE_PAM_4.1 OR CS_PAM_2.0 |

### Process
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | SWE.1 |
| name | string | YES | Software Requirements Analysis |
| purpose | string | YES | The purpose is to establish... |
| source_document | string | YES | ASPICE_PAM_4.1 OR CS_PAM_2.0 |
| domain | string | YES | generic OR cybersecurity OR ml OR hardware |

### BasePractice
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | SWE.1.BP1 |
| short_id | string | YES | BP1 |
| description | string | YES | Specify the software requirements... |
| source_document | string | YES | ASPICE_PAM_4.1 OR CS_PAM_2.0 |

### ProcessOutcome
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | SWE.1.OUT.1 |
| outcome_number | integer | YES | 1 |
| description | string | YES | The software requirements are specified |
| source_document | string | YES | ASPICE_PAM_4.1 |

### InformationItem
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | 04-04 |
| name | string | YES | Software Architecture |
| characteristics | string | YES | Full IIC text from Annex B |
| source_document | string | YES | ASPICE_PAM_4.1 OR CS_PAM_2.0 OR SHARED |

### DomainCharacteristic
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | 04-04-CS |
| domain | string | YES | cybersecurity |
| characteristics_text | string | YES | CS-specific additions to IIC |
| source_document | string | YES | CS_PAM_2.0 |

### CapabilityLevel
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | CL2 |
| level | integer | YES | 2 |
| name | string | YES | Managed process |
| description | string | YES | The implemented process is now managed... |

### ProcessAttribute
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | PA 2.1 |
| name | string | YES | Process performance management |
| scope_statement | string | YES | The performance management process attribute... |

### ProcessAttributeAchievement
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | PA2.1.ACH.1 |
| achievement_number | integer | YES | 1 |
| description | string | YES | A strategy for the performance of the process is defined |

### GenericPractice
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | GP 2.1.1 |
| description | string | YES | Identify the objectives and define a strategy... |

### Note
| Property | Type | Required | Example |
|---|---|---|---|
| id | string | YES | SWE.1.BP1.NOTE.1 |
| note_number | integer | YES | 1 |
| text | string | YES | Characteristics of requirements are defined in... |
| type | string | YES | explanatory |

---

## Relationship Types (21 total)

| Relationship | From Node | To Node | Properties | Description |
|---|---|---|---|---|
| SUPPLEMENTS | Document | Document | none | CS PAM supplements PAM 4.1 |
| DEFINES | Document | ProcessCategory | none | Document defines the category |
| DEFINES | Document | ProcessGroup | none | Document defines the group |
| EXTENDS_PROCESS_GROUP | Document | ProcessGroup | none | CS PAM extends MAN and ACQ |
| PART_OF | ProcessGroup | ProcessCategory | none | Group belongs to category |
| BELONGS_TO | Process | ProcessGroup | none | Process belongs to group |
| HAS_OUTCOME | Process | ProcessOutcome | none | Process has defined outcome |
| HAS_BASE_PRACTICE | Process | BasePractice | none | Process contains base practice |
| PRODUCES | BasePractice | InformationItem | none | BP outputs this II |
| USES | Process | InformationItem | none | Process uses this II as input |
| SATISFIES | BasePractice | ProcessOutcome | none | BP contributes to outcome |
| DEMONSTRATED_BY | ProcessAttributeAchievement | InformationItem | none | Achievement shown by this II |
| HAS_ACHIEVEMENT | ProcessAttribute | ProcessAttributeAchievement | none | PA has numbered achievement |
| HAS_GENERIC_PRACTICE | ProcessAttribute | GenericPractice | none | PA contains GP |
| ACHIEVES | GenericPractice | ProcessAttributeAchievement | none | GP satisfies achievement |
| CROSS_REFERENCES | BasePractice | Process | note_text | BP normatively references another process |
| HAS_NOTE | BasePractice | Note | none | BP has explanatory note |
| REQUIRES_FOR_LEVEL | CapabilityLevel | ProcessAttribute | rating_required | CL requires PA at this rating |
| APPLIES_TO | ProcessAttribute | CapabilityLevel | none | PA belongs to this CL |
| HAS_EXTENSION | InformationItem | DomainCharacteristic | none | Shared II has CS-specific IIC extension |
| BIDIRECTIONAL_TRACEABILITY | InformationItem | InformationItem | established_by, type | Annex D normative traceability pairs |
| CONSISTENCY | InformationItem | InformationItem | established_by | Annex D consistency pairs |

---

## Controlled Vocabulary

### source_document values
- ASPICE_PAM_4.1
- CS_PAM_2.0
- SHARED

### domain values (Process node)
- generic
- cybersecurity
- ml
- hardware

### type values (Document node)
- base
- supplement

### rating_required values (REQUIRES_FOR_LEVEL relationship)
- Largely_or_Fully
- Fully

### type values (Note node)
- explanatory

---

## Expected Node Counts (from PAM 4.1 + CS PAM 2.0)

| Label | Expected Count | Tolerance |
|---|---|---|
| Document | 2 | 0 |
| ProcessCategory | 3 | 0 |
| ProcessGroup | 12 | 0 |
| Process | 38 | 0 |
| CapabilityLevel | 6 | 0 |
| ProcessAttribute | 9 | 0 |
| GenericPractice | 27 | 10% |
| BasePractice | 175 | 15% |
| ProcessOutcome | 155 | 15% |
| InformationItem | 97 | 10% |
| ProcessAttributeAchievement | 38 | 10% |
| Note | 220 | 20% |

---

## Annex D Traceability Pairs (CS PAM 2.0 — Normative)

| From II | To II | Established By | Type |
|---|---|---|---|
| 17-53 | 17-51 | SEC.1.BP2 | BIDIRECTIONAL_TRACEABILITY |
| 17-51 | 08-59 | SEC.4.BP4 | BIDIRECTIONAL_TRACEABILITY |
| 17-00 | 08-60 | SEC.2.BP2 + SEC.3.BP4 | BIDIRECTIONAL_TRACEABILITY |
| 08-59 | 13-24 | SEC.4.BP4 | BIDIRECTIONAL_TRACEABILITY |
| 08-60 | 15-52 | SEC.3.BP4 | BIDIRECTIONAL_TRACEABILITY |
| 17-51 | 17-00 | SEC.1.BP2 | CONSISTENCY |
| 17-00 | 04-06 | SEC.2.BP2 | CONSISTENCY |
| 04-06 | 04-05 | SEC.2.BP6 | CONSISTENCY |

---

## All 38 Expected Processes

### PAM 4.1 Processes (32)
ACQ.4, SPL.2,
SYS.1, SYS.2, SYS.3, SYS.4, SYS.5,
VAL.1,
SWE.1, SWE.2, SWE.3, SWE.4, SWE.5, SWE.6,
MLE.1, MLE.2, MLE.3, MLE.4,
HWE.1, HWE.2, HWE.3, HWE.4,
SUP.1, SUP.8, SUP.9, SUP.10, SUP.11,
MAN.3, MAN.5, MAN.6,
PIM.3, REU.2

### CS PAM 2.0 Processes (6)
ACQ.2, MAN.7, SEC.1, SEC.2, SEC.3, SEC.4

---

## All 9 ProcessAttributes with Capability Level Mapping

| PA ID | PA Name | Capability Level | Rating Required |
|---|---|---|---|
| PA 1.1 | Process performance | CL1 | Largely or Fully |
| PA 2.1 | Process performance management | CL2 | Largely or Fully |
| PA 2.2 | Work product management | CL2 | Largely or Fully |
| PA 3.1 | Process definition | CL3 | Largely or Fully |
| PA 3.2 | Process deployment | CL3 | Largely or Fully |
| PA 4.1 | Quantitative analysis | CL4 | Largely or Fully |
| PA 4.2 | Quantitative control | CL4 | Largely or Fully |
| PA 5.1 | Process innovation | CL5 | Largely or Fully |
| PA 5.2 | Process innovation implementation | CL5 | Largely or Fully |
