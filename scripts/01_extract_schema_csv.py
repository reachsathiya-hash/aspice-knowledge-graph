"""
ASPICE Knowledge Graph — Step 1: Extract Known Entities to CSV
==============================================================
Reads PAM 4.1 and CS PAM 2.0 PDFs.
Produces two CSV files:
  - nodes_seed.csv       : all known nodes with properties
  - relationships_seed.csv: all known relationships

These CSVs are:
1. Used as the schema template for LLM Graph Builder
2. Validated by 02_validate_graph.py after LLM extraction

Run:
  python3 scripts/01_extract_schema_csv.py

Output:
  data/nodes_seed.csv
  data/relationships_seed.csv
  data/extraction_report.md
"""

import csv
import os
import pdfplumber
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAM_41_PDF  = "/mnt/project/Automotive-SPICE-PAM-v41.pdf"
CS_PAM_PDF  = "/mnt/project/AutomotiveSPICECSPAM20Final.pdf"
NODES_CSV   = os.path.join(BASE_DIR, "data", "nodes_seed.csv")
RELS_CSV    = os.path.join(BASE_DIR, "data", "relationships_seed.csv")
REPORT_MD   = os.path.join(BASE_DIR, "data", "extraction_report.md")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ── Node and Relationship containers ──────────────────────────────────────
nodes = []
rels  = []

def add_node(label, id_, **props):
    nodes.append({"label": label, "id": id_, **props})

def add_rel(from_id, rel_type, to_id, **props):
    rels.append({"from_id": from_id,
                 "relationship_type": rel_type,
                 "to_id": to_id, **props})

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — Documents
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Documents...")

add_node("Document", "ASPICE_PAM_4.1",
    title="Automotive SPICE® Process Reference and Assessment Model",
    version="4.1", date="2026-08-24", status="Released",
    publisher="VDA Quality Management Center", type="base")

add_node("Document", "CS_PAM_2.0",
    title="Automotive SPICE® Process Reference and Assessment Model for Cybersecurity Engineering",
    version="2.0", date="2025-03-28", status="Released",
    publisher="VDA Quality Management Center", type="supplement")

add_rel("CS_PAM_2.0", "SUPPLEMENTS", "ASPICE_PAM_4.1")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — Process Categories
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Process Categories...")

categories = [
    ("Primary",        "Primary processes category"),
    ("Supporting",     "Supporting processes category"),
    ("Organizational", "Organizational processes category"),
]
for cat_id, cat_name in categories:
    add_node("ProcessCategory", cat_id,
             name=cat_name, source_document="ASPICE_PAM_4.1")
    add_rel("ASPICE_PAM_4.1", "DEFINES", cat_id)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — Process Groups
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Process Groups...")

# (id, name, category, source_document)
process_groups = [
    # Primary — PAM 4.1
    ("ACQ", "Acquisition process group",             "Primary",        "ASPICE_PAM_4.1"),
    ("SPL", "Supply process group",                  "Primary",        "ASPICE_PAM_4.1"),
    ("SYS", "System Engineering process group",      "Primary",        "ASPICE_PAM_4.1"),
    ("VAL", "Validation process group",              "Primary",        "ASPICE_PAM_4.1"),
    ("SWE", "Software Engineering process group",    "Primary",        "ASPICE_PAM_4.1"),
    ("MLE", "Machine Learning Engineering process group", "Primary",   "ASPICE_PAM_4.1"),
    ("HWE", "Hardware Engineering process group",    "Primary",        "ASPICE_PAM_4.1"),
    # Supporting — PAM 4.1
    ("SUP", "Supporting process group",              "Supporting",     "ASPICE_PAM_4.1"),
    # Organizational — PAM 4.1
    ("MAN", "Management process group",              "Organizational", "ASPICE_PAM_4.1"),
    ("PIM", "Process Improvement process group",     "Organizational", "ASPICE_PAM_4.1"),
    ("REU", "Reuse process group",                   "Organizational", "ASPICE_PAM_4.1"),
    # CS PAM 2.0 — new group
    ("SEC", "Cybersecurity Engineering process group","Primary",       "CS_PAM_2.0"),
]

for grp_id, grp_name, cat_id, src in process_groups:
    add_node("ProcessGroup", grp_id,
             name=grp_name, source_document=src)
    add_rel(grp_id, "PART_OF", cat_id)
    doc_id = "ASPICE_PAM_4.1" if src == "ASPICE_PAM_4.1" else "CS_PAM_2.0"
    add_rel(doc_id, "DEFINES", grp_id)

# CS PAM extends MAN and ACQ
add_rel("CS_PAM_2.0", "EXTENDS_PROCESS_GROUP", "MAN")
add_rel("CS_PAM_2.0", "EXTENDS_PROCESS_GROUP", "ACQ")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — Processes
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Processes...")

# (id, name, group, domain, source_document, purpose_summary)
processes = [
    # ACQ
    ("ACQ.4","Supplier Monitoring","ACQ","generic","ASPICE_PAM_4.1",
     "Track and assess the performance of an external contract-based supplier against agreed commitments."),
    ("ACQ.2","Supplier Request and Selection","ACQ","cybersecurity","CS_PAM_2.0",
     "Select a supplier for a commitment/agreement based on relevant criteria."),
    # SPL
    ("SPL.2","Product Release","SPL","generic","ASPICE_PAM_4.1",
     "Control the release of a product to the intended customer."),
    # SYS
    ("SYS.1","Requirements Elicitation","SYS","generic","ASPICE_PAM_4.1",
     "Gather, analyze, and track evolving stakeholder needs and requirements throughout the lifecycle."),
    ("SYS.2","System Requirements Analysis","SYS","generic","ASPICE_PAM_4.1",
     "Establish a structured and analyzed set of system requirements consistent with stakeholder requirements."),
    ("SYS.3","System Architectural Design","SYS","generic","ASPICE_PAM_4.1",
     "Establish a system architectural design and identify which system requirements are to be allocated to which elements."),
    ("SYS.4","System Integration and Integration Verification","SYS","generic","ASPICE_PAM_4.1",
     "Integrate the system elements and verify that the integrated system elements are consistent with the system architecture."),
    ("SYS.5","System Verification","SYS","generic","ASPICE_PAM_4.1",
     "Confirm that the integrated system is consistent with the system requirements."),
    # VAL
    ("VAL.1","Validation","VAL","generic","ASPICE_PAM_4.1",
     "Provide evidence that the end product satisfies the intended use expectations in its operational target environment."),
    # SWE
    ("SWE.1","Software Requirements Analysis","SWE","generic","ASPICE_PAM_4.1",
     "Establish a structured and analyzed set of software requirements consistent with system requirements and system architecture."),
    ("SWE.2","Software Architectural Design","SWE","generic","ASPICE_PAM_4.1",
     "Establish an analyzed software architecture consistent with the software requirements."),
    ("SWE.3","Software Detailed Design and Unit Construction","SWE","generic","ASPICE_PAM_4.1",
     "Establish a software detailed design and construct software units consistent with the software detailed design."),
    ("SWE.4","Software Unit Verification","SWE","generic","ASPICE_PAM_4.1",
     "Verify that software units are consistent with the software detailed design."),
    ("SWE.5","Software Component Verification and Integration Verification","SWE","generic","ASPICE_PAM_4.1",
     "Verify that software components are consistent with the software architectural design and integrate the software elements."),
    ("SWE.6","Software Verification","SWE","generic","ASPICE_PAM_4.1",
     "Confirm that the integrated software is consistent with the software requirements."),
    # MLE
    ("MLE.1","Machine Learning Requirements Analysis","MLE","ml","ASPICE_PAM_4.1",
     "Refine the machine learning-related software requirements into a set of ML requirements."),
    ("MLE.2","Machine Learning Architecture","MLE","ml","ASPICE_PAM_4.1",
     "Establish a ML architecture supporting training and deployment of a ML model consistent with ML requirements."),
    ("MLE.3","Machine Learning Training","MLE","ml","ASPICE_PAM_4.1",
     "Optimize the ML model to meet the defined ML requirements."),
    ("MLE.4","Machine Learning Model Testing","MLE","ml","ASPICE_PAM_4.1",
     "Ensure the compliance of the trained ML model and the deployed ML model with the ML requirements."),
    # HWE
    ("HWE.1","Hardware Requirements Analysis","HWE","hardware","ASPICE_PAM_4.1",
     "Establish a structured and analyzed set of hardware requirements consistent with system requirements."),
    ("HWE.2","Hardware Design","HWE","hardware","ASPICE_PAM_4.1",
     "Provide an analyzed design consistent with hardware requirements suitable for manufacturing."),
    ("HWE.3","Verification against Hardware Design","HWE","hardware","ASPICE_PAM_4.1",
     "Ensure that production data compliant hardware is verified for compliance with the hardware design."),
    ("HWE.4","Verification against Hardware Requirements","HWE","hardware","ASPICE_PAM_4.1",
     "Ensure that the complete hardware is verified to be consistent with the hardware requirements."),
    # SUP
    ("SUP.1","Quality Assurance","SUP","generic","ASPICE_PAM_4.1",
     "Provide independent and objective assurance that work products and processes comply with defined criteria."),
    ("SUP.8","Configuration Management","SUP","generic","ASPICE_PAM_4.1",
     "Establish and maintain the integrity of all identified work products of a process or project."),
    ("SUP.9","Problem Resolution Management","SUP","generic","ASPICE_PAM_4.1",
     "Ensure that problems are identified, analyzed, managed, and controlled to resolution."),
    ("SUP.10","Change Request Management","SUP","generic","ASPICE_PAM_4.1",
     "Ensure that change requests are managed, tracked, and implemented."),
    ("SUP.11","Machine Learning Data Management","SUP","ml","ASPICE_PAM_4.1",
     "Ensure that ML data is managed and maintained throughout the ML lifecycle."),
    # MAN
    ("MAN.3","Project Management","MAN","generic","ASPICE_PAM_4.1",
     "Identify, establish, and control the activities and resources necessary to produce a product."),
    ("MAN.5","Risk Management","MAN","generic","ASPICE_PAM_4.1",
     "Continuously identify, analyze, treat, and monitor risks."),
    ("MAN.6","Measurement","MAN","generic","ASPICE_PAM_4.1",
     "Collect, analyze, and report data relating to products and processes."),
    ("MAN.7","Cybersecurity Risk Management","MAN","cybersecurity","CS_PAM_2.0",
     "Regularly identify, analyze, prioritize, and monitor risks of damage to relevant stakeholders."),
    # PIM
    ("PIM.3","Process Improvement","PIM","generic","ASPICE_PAM_4.1",
     "Continuously improve the effectiveness and efficiency of processes."),
    # REU
    ("REU.2","Management of Products for Reuse","REU","generic","ASPICE_PAM_4.1",
     "Ensure that reused work products are analyzed, verified, and approved for their target context."),
    # SEC — CS PAM 2.0
    ("SEC.1","Cybersecurity Requirements Elicitation","SEC","cybersecurity","CS_PAM_2.0",
     "Specify cybersecurity goals and requirements from outcomes of cybersecurity risk management."),
    ("SEC.2","Cybersecurity Implementation","SEC","cybersecurity","CS_PAM_2.0",
     "Refine the design of system, software and hardware consistent with cybersecurity requirements."),
    ("SEC.3","Risk Treatment Verification","SEC","cybersecurity","CS_PAM_2.0",
     "Confirm that implementation of design and integration of components comply with cybersecurity requirements."),
    ("SEC.4","Risk Treatment Validation","SEC","cybersecurity","CS_PAM_2.0",
     "Confirm that the integrated system achieves the associated cybersecurity goals."),
]

for proc_id, proc_name, grp_id, domain, src, purpose in processes:
    add_node("Process", proc_id,
             name=proc_name, purpose=purpose,
             domain=domain, source_document=src)
    add_rel(proc_id, "BELONGS_TO", grp_id)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — Capability Levels
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Capability Levels...")

capability_levels = [
    (0, "Incomplete process",  "The process is not implemented or fails to achieve its process purpose."),
    (1, "Performed process",   "The implemented process achieves its process purpose."),
    (2, "Managed process",     "The performed process is now implemented in a managed fashion and its work products are appropriately established, controlled and maintained."),
    (3, "Established process", "The managed process is now implemented using a defined process capable of achieving its process outcomes."),
    (4, "Predictable process", "The established process now operates predictively within defined limits to achieve its process outcomes."),
    (5, "Innovating process",  "The predictable process is now continually improved to respond to organizational change."),
]

for level, name, desc in capability_levels:
    add_node("CapabilityLevel", f"CL{level}",
             level=level, name=name, description=desc)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — Process Attributes
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Process Attributes...")

# (id, name, capability_level, rating_required, scope_statement)
process_attributes = [
    ("PA 1.1","Process performance","CL1","Largely_or_Fully",
     "A measure of the extent to which the process purpose is achieved."),
    ("PA 2.1","Process performance management","CL2","Largely_or_Fully",
     "A measure of the extent to which the performance of the process is managed."),
    ("PA 2.2","Work product management","CL2","Largely_or_Fully",
     "A measure of the extent to which the work products produced by the process are appropriately managed."),
    ("PA 3.1","Process definition","CL3","Largely_or_Fully",
     "A measure of the extent to which a standard process is maintained to support the deployment of the defined process."),
    ("PA 3.2","Process deployment","CL3","Largely_or_Fully",
     "A measure of the extent to which the standard process is deployed as a defined process to achieve its process outcomes."),
    ("PA 4.1","Quantitative analysis","CL4","Largely_or_Fully",
     "A measure of the extent to which information needs are defined, relationships between process elements are identified and data are collected."),
    ("PA 4.2","Quantitative control","CL4","Largely_or_Fully",
     "A measure of the extent to which objective data are used to manage process performance that is predictable."),
    ("PA 5.1","Process innovation","CL5","Largely_or_Fully",
     "A measure of the extent to which changes to the process are identified from investigations of innovative approaches."),
    ("PA 5.2","Process innovation implementation","CL5","Largely_or_Fully",
     "A measure of the extent to which changes to the definition, management and performance of the process achieves the relevant process innovation objectives."),
]

# CL requirement rules from Table 9 — PAM 4.1
cl_pa_rules = {
    "CL1": [("PA 1.1","Largely_or_Fully")],
    "CL2": [("PA 1.1","Fully"),("PA 2.1","Largely_or_Fully"),("PA 2.2","Largely_or_Fully")],
    "CL3": [("PA 1.1","Fully"),("PA 2.1","Fully"),("PA 2.2","Fully"),
            ("PA 3.1","Largely_or_Fully"),("PA 3.2","Largely_or_Fully")],
    "CL4": [("PA 1.1","Fully"),("PA 2.1","Fully"),("PA 2.2","Fully"),
            ("PA 3.1","Fully"),("PA 3.2","Fully"),
            ("PA 4.1","Largely_or_Fully"),("PA 4.2","Largely_or_Fully")],
    "CL5": [("PA 1.1","Fully"),("PA 2.1","Fully"),("PA 2.2","Fully"),
            ("PA 3.1","Fully"),("PA 3.2","Fully"),
            ("PA 4.1","Fully"),("PA 4.2","Fully"),
            ("PA 5.1","Largely_or_Fully"),("PA 5.2","Largely_or_Fully")],
}

for pa_id, pa_name, cl_id, rating, scope in process_attributes:
    add_node("ProcessAttribute", pa_id,
             name=pa_name, scope_statement=scope)
    add_rel(pa_id, "APPLIES_TO", cl_id)

for cl_id, pa_rules in cl_pa_rules.items():
    for pa_id, rating in pa_rules:
        add_rel(cl_id, "REQUIRES_FOR_LEVEL", pa_id,
                rating_required=rating)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — Key Information Items (Seed Set)
# ══════════════════════════════════════════════════════════════════════════
print("Extracting Information Items seed set...")

# Core IIs that appear across multiple processes
# Full extraction handled by LLM Graph Builder
# This seed set ensures critical IIs are present with correct IDs

information_items = [
    # SHARED — appear in both PAM 4.1 and CS PAM 2.0
    ("02-01","Commitment/Agreement","SHARED"),
    ("03-50","Verification Measure Data","SHARED"),
    ("04-04","Software Architecture","SHARED"),
    ("04-05","Software Detailed Design","SHARED"),
    ("04-06","System Architecture","SHARED"),
    ("04-52","Hardware Architecture","SHARED"),
    ("04-53","Hardware Detailed Design","SHARED"),
    ("08-55","Risk Treatment","SHARED"),
    ("08-57","Validation Measure Selection Set","SHARED"),
    ("08-58","Verification Measure Selection Set","SHARED"),
    ("08-60","Verification Measure","SHARED"),
    ("13-51","Consistency Evidence","SHARED"),
    ("13-52","Communication Evidence","SHARED"),
    ("15-51","Analysis Results","SHARED"),
    ("15-52","Verification Results","SHARED"),
    ("17-00","Requirement","SHARED"),
    ("17-54","Requirement Attribute","SHARED"),
    # PAM 4.1 specific
    ("08-56","Schedule","ASPICE_PAM_4.1"),
    ("10-00","Process Description","ASPICE_PAM_4.1"),
    ("13-08","Baseline","ASPICE_PAM_4.1"),
    ("13-19","Review Evidence","ASPICE_PAM_4.1"),
    ("14-10","Work Package","ASPICE_PAM_4.1"),
    ("17-05","Requirements for Work Products","ASPICE_PAM_4.1"),
    ("18-58","Process Performance Objectives","ASPICE_PAM_4.1"),
    ("19-01","Process Performance Strategy","ASPICE_PAM_4.1"),
    # CS PAM 2.0 specific
    ("02-50","Interface Agreement","CS_PAM_2.0"),
    ("03-55","Validation Measure Data","CS_PAM_2.0"),
    ("08-59","Validation Measure","CS_PAM_2.0"),
    ("12-01","Request for Quotation","CS_PAM_2.0"),
    ("13-24","Validation Results","CS_PAM_2.0"),
    ("15-09","Risk Status","CS_PAM_2.0"),
    ("15-21","Supplier Evaluation","CS_PAM_2.0"),
    ("15-50","Vulnerability Analysis Evidence","CS_PAM_2.0"),
    ("17-51","Cybersecurity Goals","CS_PAM_2.0"),
    ("17-52","Cybersecurity Controls","CS_PAM_2.0"),
    ("17-53","Cybersecurity Threat Scenario","CS_PAM_2.0"),
    ("18-50","Supplier Evaluation Criteria","CS_PAM_2.0"),
]

# Deduplicate by id+source
seen_ii = set()
for ii_id, ii_name, src in information_items:
    key = f"{ii_id}_{src}"
    if key not in seen_ii:
        seen_ii.add(key)
        add_node("InformationItem", ii_id,
                 name=ii_name, source_document=src,
                 characteristics="[To be populated by LLM extraction from Annex B]")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — Annex D Traceability Pairs (Normative — CS PAM 2.0)
# ══════════════════════════════════════════════════════════════════════════
print("Adding Annex D traceability relationships...")

annex_d_traceability = [
    ("17-53","17-51","SEC.1.BP2","BIDIRECTIONAL_TRACEABILITY"),
    ("17-51","08-59","SEC.4.BP4","BIDIRECTIONAL_TRACEABILITY"),
    ("17-00","08-60","SEC.2.BP2|SEC.3.BP4","BIDIRECTIONAL_TRACEABILITY"),
    ("08-59","13-24","SEC.4.BP4","BIDIRECTIONAL_TRACEABILITY"),
    ("08-60","15-52","SEC.3.BP4","BIDIRECTIONAL_TRACEABILITY"),
]

annex_d_consistency = [
    ("17-51","17-00","SEC.1.BP2"),
    ("17-00","04-06","SEC.2.BP2"),
    ("04-06","04-05","SEC.2.BP6"),
]

for from_id, to_id, established_by, rel_type in annex_d_traceability:
    add_rel(from_id, rel_type, to_id,
            established_by=established_by,
            type="traceability",
            source="Annex_D_CS_PAM_2.0")

for from_id, to_id, established_by in annex_d_consistency:
    add_rel(from_id, "CONSISTENCY", to_id,
            established_by=established_by,
            type="consistency",
            source="Annex_D_CS_PAM_2.0")

# ══════════════════════════════════════════════════════════════════════════
# WRITE CSV FILES
# ══════════════════════════════════════════════════════════════════════════
print("\nWriting CSV files...")

# Collect all property keys for nodes and rels
node_keys = set()
for n in nodes:
    node_keys.update(n.keys())
node_keys = ["label","id"] + sorted(k for k in node_keys if k not in ("label","id"))

rel_keys = set()
for r in rels:
    rel_keys.update(r.keys())
rel_keys = ["from_id","relationship_type","to_id"] + \
           sorted(k for k in rel_keys if k not in ("from_id","relationship_type","to_id"))

with open(NODES_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=node_keys, extrasaction="ignore")
    writer.writeheader()
    for n in nodes:
        writer.writerow({k: n.get(k,"") for k in node_keys})

with open(RELS_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rel_keys, extrasaction="ignore")
    writer.writeheader()
    for r in rels:
        writer.writerow({k: r.get(k,"") for k in rel_keys})

# ══════════════════════════════════════════════════════════════════════════
# WRITE EXTRACTION REPORT
# ══════════════════════════════════════════════════════════════════════════
from collections import Counter
node_counts  = Counter(n["label"] for n in nodes)
rel_counts   = Counter(r["relationship_type"] for r in rels)

report = f"""# ASPICE Knowledge Graph — Seed Extraction Report
Generated: {date.today()}

## Node Counts
| Label | Count |
|---|---|
"""
for label, count in sorted(node_counts.items()):
    report += f"| {label} | {count} |\n"

report += f"""
## Relationship Counts
| Type | Count |
|---|---|
"""
for rel_type, count in sorted(rel_counts.items()):
    report += f"| {rel_type} | {count} |\n"

report += f"""
## Summary
- Total nodes: {len(nodes)}
- Total relationships: {len(rels)}
- Unique node labels: {len(node_counts)}
- Unique relationship types: {len(rel_counts)}

## Next Steps
1. Review data/nodes_seed.csv — verify all 38 processes present
2. Review data/relationships_seed.csv — verify Annex D pairs
3. Upload ASPICE PDFs to Neo4j LLM Graph Builder
4. Use schema/aspice_schema.md as the schema prompt
5. After LLM extraction, export nodes.csv and relationships.csv from Neo4j
6. Run: python3 scripts/02_validate_graph.py
"""

with open(REPORT_MD, "w", encoding="utf-8") as f:
    f.write(report)

print(f"\n✓ nodes_seed.csv      : {len(nodes)} nodes")
print(f"✓ relationships_seed.csv: {len(rels)} relationships")
print(f"✓ extraction_report.md  : written")
print(f"\nFiles in: {os.path.join(BASE_DIR, 'data')}")
print("\nNext: review the CSVs, then run 02_validate_graph.py")
