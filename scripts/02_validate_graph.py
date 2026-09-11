"""
ASPICE Knowledge Graph — Step 2: Validate Extracted Graph
=========================================================
Reads nodes.csv and relationships.csv exported from Neo4j
after LLM Graph Builder extraction.

Runs three layers of validation:
  Layer 1 — Structural    (format, IDs, required fields)
  Layer 2 — Ontological   (allowed connections, cardinality)
  Layer 3 — Domain Fidelity (counts, process IDs, Annex D)

Run:
  python3 scripts/02_validate_graph.py \
      --nodes data/nodes.csv \
      --rels  data/relationships.csv

Output:
  data/validation_report.md
  Exit code 0 = READY, Exit code 1 = NOT READY
"""

import csv
import re
import sys
import os
import argparse
from datetime import date
from collections import Counter, defaultdict

# ── CLI ────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Validate ASPICE Knowledge Graph CSVs")
parser.add_argument("--nodes", default="data/nodes.csv", help="Path to nodes CSV")
parser.add_argument("--rels",  default="data/relationships.csv", help="Path to relationships CSV")
parser.add_argument("--out",   default="data/validation_report.md", help="Output report path")
args = parser.parse_args()

# ── Load CSVs ──────────────────────────────────────────────────────────────
print(f"Loading {args.nodes}...")
nodes_raw = []
with open(args.nodes, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        nodes_raw.append(row)

print(f"Loading {args.rels}...")
rels_raw = []
with open(args.rels, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rels_raw.append(row)

print(f"Loaded {len(nodes_raw)} nodes, {len(rels_raw)} relationships\n")

# ── Helper containers ─────────────────────────────────────────────────────
node_by_id    = {n["id"]: n for n in nodes_raw}
node_ids      = set(node_by_id.keys())
label_of      = {n["id"]: n.get("label","") for n in nodes_raw}

failures = []
warnings = []
passed   = 0

def PASS(msg):
    global passed
    passed += 1
    print(f"  ✓ {msg}")

def FAIL(check_id, msg):
    failures.append((check_id, msg))
    print(f"  ✗ [{check_id}] {msg}")

def WARN(msg):
    warnings.append(msg)
    print(f"  ⚠ {msg}")

# ══════════════════════════════════════════════════════════════════════════
# LAYER 1 — STRUCTURAL VALIDATION
# ══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("LAYER 1 — Structural Validation")
print("=" * 60)

# L1-01: No duplicate node IDs
ids = [n["id"] for n in nodes_raw]
dupes = [i for i, c in Counter(ids).items() if c > 1]
if dupes:
    FAIL("L1-01", f"Duplicate node IDs: {dupes[:10]}")
else:
    PASS("L1-01 No duplicate node IDs")

# L1-02: All nodes have label and id
missing = [n for n in nodes_raw if not n.get("id") or not n.get("label")]
if missing:
    FAIL("L1-02", f"{len(missing)} nodes missing id or label")
else:
    PASS("L1-02 All nodes have id and label")

# L1-03: Node labels in approved list
VALID_LABELS = {
    "Document","ProcessCategory","ProcessGroup","Process",
    "BasePractice","ProcessOutcome","InformationItem",
    "DomainCharacteristic","CapabilityLevel","ProcessAttribute",
    "ProcessAttributeAchievement","GenericPractice","Note"
}
bad_labels = [n["id"] for n in nodes_raw if n.get("label") not in VALID_LABELS]
if bad_labels:
    FAIL("L1-03", f"{len(bad_labels)} nodes with invalid labels: {bad_labels[:5]}")
else:
    PASS("L1-03 All node labels in approved list")

# L1-04: source_document controlled vocabulary
# Document nodes are exempt — they ARE the source document
VALID_SOURCES = {"ASPICE_PAM_4.1","CS_PAM_2.0","SHARED",""}
bad_sources = [n["id"] for n in nodes_raw
               if n.get("label") != "Document"
               and n.get("source_document","") not in VALID_SOURCES]
if bad_sources:
    FAIL("L1-04", f"{len(bad_sources)} nodes with invalid source_document: {bad_sources[:5]}")
else:
    PASS("L1-04 source_document values valid")

# L1-05: Process IDs follow naming convention
proc_nodes = [n for n in nodes_raw if n.get("label")=="Process"]
bad_proc_ids = [n["id"] for n in proc_nodes
                if not re.match(r'^[A-Z]{2,3}\.\d+$', n["id"])]
if bad_proc_ids:
    FAIL("L1-05", f"Process IDs not matching pattern: {bad_proc_ids}")
else:
    PASS("L1-05 Process IDs follow naming convention")

# L1-06: BasePractice IDs follow naming convention
bp_nodes = [n for n in nodes_raw if n.get("label")=="BasePractice"]
bad_bp_ids = [n["id"] for n in bp_nodes
              if not re.match(r'^[A-Z]{2,3}\.\d+\.BP\d+$', n["id"])]
if bad_bp_ids:
    FAIL("L1-06", f"BasePractice IDs not matching pattern: {bad_bp_ids[:5]}")
else:
    PASS("L1-06 BasePractice IDs follow naming convention")

# L1-07: InformationItem IDs follow naming convention
ii_nodes = [n for n in nodes_raw if n.get("label")=="InformationItem"]
bad_ii_ids = [n["id"] for n in ii_nodes
              if not re.match(r'^\d{2}-\d{2,3}$', n["id"])]
if bad_ii_ids:
    FAIL("L1-07", f"InformationItem IDs not matching pattern: {bad_ii_ids[:5]}")
else:
    PASS("L1-07 InformationItem IDs follow naming convention")

# L1-08: CapabilityLevel values CL0 to CL5
cl_nodes = [n for n in nodes_raw if n.get("label")=="CapabilityLevel"]
bad_cl = [n["id"] for n in cl_nodes
          if not re.match(r'^CL[0-5]$', n["id"])]
if bad_cl:
    FAIL("L1-08", f"CapabilityLevel IDs invalid: {bad_cl}")
else:
    PASS("L1-08 CapabilityLevel IDs valid CL0-CL5")

# L1-09: ProcessAttribute IDs follow convention
pa_nodes = [n for n in nodes_raw if n.get("label")=="ProcessAttribute"]
bad_pa = [n["id"] for n in pa_nodes
          if not re.match(r'^PA \d\.\d$', n["id"])]
if bad_pa:
    FAIL("L1-09", f"ProcessAttribute IDs invalid: {bad_pa}")
else:
    PASS("L1-09 ProcessAttribute IDs follow PA X.X convention")

# L1-10: Relationship types in approved list
VALID_REL_TYPES = {
    "SUPPLEMENTS","DEFINES","EXTENDS_PROCESS_GROUP",
    "PART_OF","BELONGS_TO","HAS_OUTCOME","HAS_BASE_PRACTICE",
    "PRODUCES","USES","SATISFIES","DEMONSTRATED_BY",
    "HAS_ACHIEVEMENT","HAS_GENERIC_PRACTICE","ACHIEVES",
    "CROSS_REFERENCES","HAS_NOTE","REQUIRES_FOR_LEVEL",
    "APPLIES_TO","HAS_EXTENSION","BIDIRECTIONAL_TRACEABILITY",
    "CONSISTENCY"
}
bad_rels = [r["relationship_type"] for r in rels_raw
            if r.get("relationship_type") not in VALID_REL_TYPES]
if bad_rels:
    FAIL("L1-10", f"{len(bad_rels)} invalid relationship types: {list(set(bad_rels))[:5]}")
else:
    PASS("L1-10 All relationship types in approved list")

# L1-11: No orphan relationships
orphan_from = [r for r in rels_raw if r.get("from_id") not in node_ids]
orphan_to   = [r for r in rels_raw if r.get("to_id") not in node_ids]
if orphan_from or orphan_to:
    FAIL("L1-11", f"{len(orphan_from)} orphan from_ids, {len(orphan_to)} orphan to_ids")
else:
    PASS("L1-11 No orphan relationships")

# L1-12: No self-relationships
self_rels = [r for r in rels_raw if r.get("from_id")==r.get("to_id")]
if self_rels:
    FAIL("L1-12", f"{len(self_rels)} self-referencing relationships")
else:
    PASS("L1-12 No self-referencing relationships")

# L1-13: No duplicate relationships
rel_tuples = [(r.get("from_id"),r.get("relationship_type"),r.get("to_id"))
              for r in rels_raw]
dupe_rels = [t for t, c in Counter(rel_tuples).items() if c > 1]
if dupe_rels:
    FAIL("L1-13", f"{len(dupe_rels)} duplicate relationships: {dupe_rels[:3]}")
else:
    PASS("L1-13 No duplicate relationships")

# L1-14: BIDIRECTIONAL_TRACEABILITY has established_by property
bt_rels = [r for r in rels_raw if r.get("relationship_type")=="BIDIRECTIONAL_TRACEABILITY"]
missing_est = [r for r in bt_rels if not r.get("established_by","").strip()]
if missing_est:
    FAIL("L1-14", f"{len(missing_est)} BIDIRECTIONAL_TRACEABILITY missing established_by")
else:
    PASS("L1-14 BIDIRECTIONAL_TRACEABILITY has established_by property")

# ══════════════════════════════════════════════════════════════════════════
# LAYER 2 — ONTOLOGICAL CONSISTENCY
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("LAYER 2 — Ontological Consistency")
print("=" * 60)

# Allowed connection matrix
ALLOWED = {
    ("Document",          "SUPPLEMENTS",           "Document"),
    ("Document",          "DEFINES",               "ProcessCategory"),
    ("Document",          "DEFINES",               "ProcessGroup"),
    ("Document",          "EXTENDS_PROCESS_GROUP", "ProcessGroup"),
    ("ProcessGroup",      "PART_OF",               "ProcessCategory"),
    ("Process",           "BELONGS_TO",            "ProcessGroup"),
    ("Process",           "HAS_OUTCOME",           "ProcessOutcome"),
    ("Process",           "HAS_BASE_PRACTICE",     "BasePractice"),
    ("Process",           "USES",                  "InformationItem"),
    ("BasePractice",      "PRODUCES",              "InformationItem"),
    ("BasePractice",      "SATISFIES",             "ProcessOutcome"),
    ("BasePractice",      "CROSS_REFERENCES",      "Process"),
    ("BasePractice",      "HAS_NOTE",              "Note"),
    ("ProcessAttribute",  "HAS_ACHIEVEMENT",       "ProcessAttributeAchievement"),
    ("ProcessAttribute",  "HAS_GENERIC_PRACTICE",  "GenericPractice"),
    ("ProcessAttribute",  "APPLIES_TO",            "CapabilityLevel"),
    ("ProcessAttribute",  "DEMONSTRATED_BY",       "InformationItem"),
    ("ProcessAttributeAchievement","DEMONSTRATED_BY","InformationItem"),
    ("GenericPractice",   "ACHIEVES",              "ProcessAttributeAchievement"),
    ("CapabilityLevel",   "REQUIRES_FOR_LEVEL",    "ProcessAttribute"),
    ("InformationItem",   "HAS_EXTENSION",         "DomainCharacteristic"),
    ("InformationItem",   "BIDIRECTIONAL_TRACEABILITY","InformationItem"),
    ("InformationItem",   "CONSISTENCY",           "InformationItem"),
}

# L2-01: All relationships match allowed connection matrix
invalid_connections = []
for r in rels_raw:
    from_label = label_of.get(r.get("from_id",""), "UNKNOWN")
    to_label   = label_of.get(r.get("to_id",""),   "UNKNOWN")
    triple = (from_label, r.get("relationship_type",""), to_label)
    if triple not in ALLOWED:
        invalid_connections.append(triple)

if invalid_connections:
    FAIL("L2-01", f"{len(invalid_connections)} invalid connections. "
         f"Examples: {list(set(invalid_connections))[:3]}")
else:
    PASS("L2-01 All relationships match allowed connection matrix")

# L2-02: Every Process has at least one BasePractice
proc_ids = [n["id"] for n in nodes_raw if n.get("label")=="Process"]
proc_to_bps = defaultdict(list)
for r in rels_raw:
    if r.get("relationship_type")=="HAS_BASE_PRACTICE":
        proc_to_bps[r["from_id"]].append(r["to_id"])

no_bps = [pid for pid in proc_ids if len(proc_to_bps[pid])==0]
if no_bps:
    FAIL("L2-02", f"{len(no_bps)} processes have no BasePractices: {no_bps}")
else:
    PASS("L2-02 Every Process has at least one BasePractice")

# L2-03: Every Process has at least one ProcessOutcome
proc_to_outcomes = defaultdict(list)
for r in rels_raw:
    if r.get("relationship_type")=="HAS_OUTCOME":
        proc_to_outcomes[r["from_id"]].append(r["to_id"])
no_outcomes = [pid for pid in proc_ids if len(proc_to_outcomes[pid])==0]
if no_outcomes:
    FAIL("L2-03", f"{len(no_outcomes)} processes have no ProcessOutcomes: {no_outcomes}")
else:
    PASS("L2-03 Every Process has at least one ProcessOutcome")

# L2-04: Every Process BELONGS_TO exactly one ProcessGroup
proc_to_groups = defaultdict(list)
for r in rels_raw:
    if r.get("relationship_type")=="BELONGS_TO":
        proc_to_groups[r["from_id"]].append(r["to_id"])
bad_group_count = [pid for pid in proc_ids if len(proc_to_groups[pid])!=1]
if bad_group_count:
    FAIL("L2-04", f"{len(bad_group_count)} processes not in exactly one ProcessGroup: {bad_group_count}")
else:
    PASS("L2-04 Every Process BELONGS_TO exactly one ProcessGroup")

# L2-05: Every ProcessGroup PART_OF exactly one ProcessCategory
grp_ids = [n["id"] for n in nodes_raw if n.get("label")=="ProcessGroup"]
grp_to_cats = defaultdict(list)
for r in rels_raw:
    if r.get("relationship_type")=="PART_OF":
        grp_to_cats[r["from_id"]].append(r["to_id"])
bad_cat_count = [gid for gid in grp_ids if len(grp_to_cats[gid])!=1]
if bad_cat_count:
    FAIL("L2-05", f"{len(bad_cat_count)} ProcessGroups not in exactly one ProcessCategory: {bad_cat_count}")
else:
    PASS("L2-05 Every ProcessGroup PART_OF exactly one ProcessCategory")

# L2-06: Capability level PA requirements from Table 9
CL_PA_REQUIREMENTS = {
    "CL1": ["PA 1.1"],
    "CL2": ["PA 1.1","PA 2.1","PA 2.2"],
    "CL3": ["PA 1.1","PA 2.1","PA 2.2","PA 3.1","PA 3.2"],
    "CL4": ["PA 1.1","PA 2.1","PA 2.2","PA 3.1","PA 3.2","PA 4.1","PA 4.2"],
    "CL5": ["PA 1.1","PA 2.1","PA 2.2","PA 3.1","PA 3.2",
            "PA 4.1","PA 4.2","PA 5.1","PA 5.2"],
}
cl_to_pas = defaultdict(list)
for r in rels_raw:
    if r.get("relationship_type")=="REQUIRES_FOR_LEVEL":
        cl_to_pas[r["from_id"]].append(r["to_id"])

cl_missing = []
for cl_id, required_pas in CL_PA_REQUIREMENTS.items():
    if cl_id in node_ids:
        for pa in required_pas:
            if pa not in cl_to_pas[cl_id]:
                cl_missing.append(f"{cl_id} missing {pa}")
if cl_missing:
    FAIL("L2-06", f"Capability level model gaps: {cl_missing}")
else:
    PASS("L2-06 Capability level model complete per Table 9")

# ══════════════════════════════════════════════════════════════════════════
# LAYER 3 — DOMAIN FIDELITY
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("LAYER 3 — Domain Fidelity")
print("=" * 60)

node_counts = Counter(n["label"] for n in nodes_raw)

# L3-01: Node count check with tolerances
EXPECTED_COUNTS = {
    "Document":                  (2,   0.0),
    "ProcessCategory":           (3,   0.0),
    "ProcessGroup":              (12,  0.0),
    "Process":                   (38,  0.0),
    "CapabilityLevel":           (6,   0.0),
    "ProcessAttribute":          (9,   0.0),
    "GenericPractice":           (27,  0.30),
    "BasePractice":              (175, 0.35),
    "ProcessOutcome":            (155, 0.40),
    "InformationItem":           (97,  0.30),
    "ProcessAttributeAchievement":(38, 0.15),
    "Note":                      (220, 0.25),
}

count_failures = []
for label, (expected, tol) in EXPECTED_COUNTS.items():
    actual = node_counts.get(label, 0)
    if tol == 0.0:
        if actual != expected:
            count_failures.append(f"{label}: expected {expected}, got {actual}")
    else:
        lower = int(expected * (1 - tol))
        upper = int(expected * (1 + tol))
        if not (lower <= actual <= upper):
            count_failures.append(f"{label}: expected {lower}-{upper}, got {actual}")
        elif actual < expected * 0.85:
            WARN(f"{label}: got {actual}, expected ~{expected} — check extraction completeness")

if count_failures:
    FAIL("L3-01", f"Node count mismatches: {count_failures}")
else:
    PASS("L3-01 Node counts within expected ranges")

# L3-02: All 32 PAM 4.1 processes present
PAM_41_PROCESSES = {
    "ACQ.4","SPL.2",
    "SYS.1","SYS.2","SYS.3","SYS.4","SYS.5",
    "VAL.1",
    "SWE.1","SWE.2","SWE.3","SWE.4","SWE.5","SWE.6",
    "MLE.1","MLE.2","MLE.3","MLE.4",
    "HWE.1","HWE.2","HWE.3","HWE.4",
    "SUP.1","SUP.8","SUP.9","SUP.10","SUP.11",
    "MAN.3","MAN.5","MAN.6",
    "PIM.3","REU.2"
}
actual_proc_ids = set(n["id"] for n in nodes_raw if n.get("label")=="Process")
missing_pam = PAM_41_PROCESSES - actual_proc_ids
if missing_pam:
    FAIL("L3-02", f"Missing PAM 4.1 processes: {sorted(missing_pam)}")
else:
    PASS("L3-02 All 32 PAM 4.1 processes present")

# L3-03: All 6 CS PAM processes present
CS_PROCESSES = {"ACQ.2","MAN.7","SEC.1","SEC.2","SEC.3","SEC.4"}
missing_cs = CS_PROCESSES - actual_proc_ids
if missing_cs:
    FAIL("L3-03", f"Missing CS PAM 2.0 processes: {sorted(missing_cs)}")
else:
    PASS("L3-03 All 6 CS PAM 2.0 processes present")

# L3-04: All 9 ProcessAttributes present
PA_EXPECTED = {"PA 1.1","PA 2.1","PA 2.2","PA 3.1","PA 3.2",
               "PA 4.1","PA 4.2","PA 5.1","PA 5.2"}
actual_pa_ids = set(n["id"] for n in nodes_raw if n.get("label")=="ProcessAttribute")
missing_pa = PA_EXPECTED - actual_pa_ids
if missing_pa:
    FAIL("L3-04", f"Missing ProcessAttributes: {sorted(missing_pa)}")
else:
    PASS("L3-04 All 9 ProcessAttributes present")

# L3-05: All 6 CapabilityLevels present
CL_EXPECTED = {"CL0","CL1","CL2","CL3","CL4","CL5"}
actual_cl_ids = set(n["id"] for n in nodes_raw if n.get("label")=="CapabilityLevel")
missing_cl = CL_EXPECTED - actual_cl_ids
if missing_cl:
    FAIL("L3-05", f"Missing CapabilityLevels: {sorted(missing_cl)}")
else:
    PASS("L3-05 All 6 CapabilityLevels present")

# L3-06: Annex D traceability pairs exist
ANNEX_D_PAIRS = [
    ("17-53","BIDIRECTIONAL_TRACEABILITY","17-51","SEC.1.BP2"),
    ("17-51","BIDIRECTIONAL_TRACEABILITY","08-59","SEC.4.BP4"),
    ("08-59","BIDIRECTIONAL_TRACEABILITY","13-24","SEC.4.BP4"),
    ("08-60","BIDIRECTIONAL_TRACEABILITY","15-52","SEC.3.BP4"),
]
rel_lookup = set(
    (r.get("from_id"),r.get("relationship_type"),r.get("to_id"))
    for r in rels_raw
)
missing_annex_d = []
for from_id, rel_type, to_id, bp in ANNEX_D_PAIRS:
    if (from_id, rel_type, to_id) not in rel_lookup:
        missing_annex_d.append(f"{from_id} -[{rel_type}]-> {to_id} (via {bp})")
if missing_annex_d:
    FAIL("L3-06", f"Missing Annex D traceability pairs: {missing_annex_d}")
else:
    PASS("L3-06 All Annex D normative traceability pairs present")

# L3-07: CS-specific Information Items present
CS_SPECIFIC_IIS = {
    "02-50","03-55","08-59","12-01","13-24",
    "15-09","15-21","15-50","17-51","17-52","17-53","18-50"
}
actual_ii_ids = set(n["id"] for n in nodes_raw if n.get("label")=="InformationItem")
missing_cs_ii = CS_SPECIFIC_IIS - actual_ii_ids
if missing_cs_ii:
    FAIL("L3-07", f"Missing CS PAM Information Items: {sorted(missing_cs_ii)}")
else:
    PASS("L3-07 All CS PAM-specific Information Items present")

# L3-08: REVIEW flags — not failures, need human check
print("\n--- Review Flags (need human validation) ---")

for pid in sorted(actual_proc_ids):
    bp_count = len(proc_to_bps.get(pid, []))
    if bp_count < 3:
        WARN(f"{pid} has only {bp_count} BasePractices — verify extraction")

produced_ii_ids = set(r["to_id"] for r in rels_raw if r.get("relationship_type")=="PRODUCES")
unproduced = actual_ii_ids - produced_ii_ids
if unproduced:
    WARN(f"{len(unproduced)} InformationItems with no PRODUCES relationship: {sorted(unproduced)[:5]}")

# ══════════════════════════════════════════════════════════════════════════
# WRITE VALIDATION REPORT
# ══════════════════════════════════════════════════════════════════════════
total_checks = passed + len(failures)
status = "✅ READY" if len(failures) == 0 else "❌ NOT READY"

report = f"""# ASPICE Knowledge Graph — Validation Report
Generated: {date.today()}
Status: {status}

## Summary
| Metric | Value |
|---|---|
| Total checks | {total_checks} |
| Passed | {passed} |
| Failed | {len(failures)} |
| Warnings | {len(warnings)} |
| Total nodes | {len(nodes_raw)} |
| Total relationships | {len(rels_raw)} |

"""

if failures:
    report += "## Failures — Must Fix Before Loading to Neo4j\n"
    for check_id, msg in failures:
        report += f"- **[{check_id}]** {msg}\n"
    report += "\n"

if warnings:
    report += "## Warnings — Review Required\n"
    for w in warnings:
        report += f"- ⚠ {w}\n"
    report += "\n"

report += "## Node Counts\n| Label | Count |\n|---|---|\n"
for label, count in sorted(Counter(n["label"] for n in nodes_raw).items()):
    report += f"| {label} | {count} |\n"

report += "\n## Relationship Counts\n| Type | Count |\n|---|---|\n"
for rel_type, count in sorted(Counter(r["relationship_type"] for r in rels_raw).items()):
    report += f"| {rel_type} | {count} |\n"

os.makedirs(os.path.dirname(args.out), exist_ok=True)
with open(args.out, "w", encoding="utf-8") as f:
    f.write(report)

print("\n" + "=" * 60)
print(f"RESULT: {status}")
print(f"Passed: {passed}/{total_checks} checks")
if failures:
    print(f"Failed: {len(failures)} checks — see {args.out}")
print(f"Report: {args.out}")
print("=" * 60)

sys.exit(0 if len(failures) == 0 else 1)
