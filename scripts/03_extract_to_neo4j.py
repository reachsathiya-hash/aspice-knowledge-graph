"""
ASPICE Knowledge Graph — Step 3 (v2): Targeted Extraction to Neo4j
==================================================================
Extracts one node type at a time per chunk.
Prevents JSON truncation errors from dense pages.

Run:
  python3 scripts/03_extract_to_neo4j.py
"""

import os, json, time, csv
import pdfplumber
import anthropic
from neo4j import GraphDatabase
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════
# CONFIG — Edit these before running
# ══════════════════════════════════════════════════════════════════════════

NEO4J_URI      = os.environ.get("NEO4J_URI", "")
NEO4J_USER     = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = "REPLACE_WITH_YOUR_PASSWORD"

ANTHROPIC_API_KEY = "REPLACE_WITH_YOUR_CLAUDE_API_KEY"

PAM_41_PDF = os.path.expanduser("~/Downloads/Automotive-SPICE-PAM-v41.pdf")
CS_PAM_PDF = os.path.expanduser("~/Downloads/Automotive-SPICE-CS-PAM-20-Final.pdf")

CHUNK_SIZE = 6
API_DELAY  = 2

# ══════════════════════════════════════════════════════════════════════════
# PROMPTS
# ══════════════════════════════════════════════════════════════════════════

PROMPTS = {

"processes": """You are an ASPICE expert. Extract ONLY Process nodes.
A Process has ID like SWE.1, MAN.3, SEC.2, a name, and purpose.
Return JSON only:
{"nodes":[{"label":"Process","id":"SWE.1","name":"Software Requirements Analysis","purpose":"The purpose is to...","domain":"generic","source_document":"ASPICE_PAM_4.1"}]}
domain: generic, cybersecurity, ml, or hardware
If none found: {"nodes":[]}""",

"outcomes": """You are an ASPICE expert. Extract ONLY ProcessOutcome nodes.
Outcomes are numbered lists under each process: "1) The software requirements are specified."
Return JSON only:
{"nodes":[{"label":"ProcessOutcome","id":"SWE.1.OUT.1","outcome_number":1,"description":"The software requirements are specified.","source_document":"ASPICE_PAM_4.1"}],"relationships":[{"from_id":"SWE.1","relationship_type":"HAS_OUTCOME","to_id":"SWE.1.OUT.1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"basepractices": """You are an ASPICE expert. Extract ONLY BasePractice nodes.
Base practices have IDs like SWE.1.BP1, MAN.3.BP4, SEC.2.BP3.
Return JSON only:
{"nodes":[{"label":"BasePractice","id":"SWE.1.BP1","description":"Specify the software requirements...","source_document":"ASPICE_PAM_4.1"}],"relationships":[{"from_id":"SWE.1","relationship_type":"HAS_BASE_PRACTICE","to_id":"SWE.1.BP1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"notes": """You are an ASPICE expert. Extract ONLY Note nodes.
Notes are numbered like "Note 1:", "Note 2:" attached to base practices.
Return JSON only:
{"nodes":[{"label":"Note","id":"SWE.1.BP1.NOTE.1","note_number":1,"text":"Characteristics of requirements are defined in...","type":"explanatory"}],"relationships":[{"from_id":"SWE.1.BP1","relationship_type":"HAS_NOTE","to_id":"SWE.1.BP1.NOTE.1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"informationitems": """You are an ASPICE expert. Extract InformationItem nodes from output tables.
Information items have numeric IDs like 04-04, 17-00, 08-56.
Also extract PRODUCES and SATISFIES relationships.
Return JSON only:
{"nodes":[{"label":"InformationItem","id":"04-04","name":"Software Architecture","source_document":"ASPICE_PAM_4.1"}],"relationships":[{"from_id":"SWE.2.BP1","relationship_type":"PRODUCES","to_id":"04-04"},{"from_id":"SWE.2.BP1","relationship_type":"SATISFIES","to_id":"SWE.2.OUT.1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"crossrefs": """You are an ASPICE expert. Extract cross-reference relationships only.
Cross references appear as "See X", "Refer to X" inside base practice text.
Return JSON only:
{"relationships":[{"from_id":"SWE.1.BP3","relationship_type":"CROSS_REFERENCES","to_id":"MAN.3"}]}
If none found: {"relationships":[]}""",

"genericpractices": """You are an ASPICE expert. Extract GenericPractice nodes from Chapter 5.
Generic practices have IDs like GP 1.1.1, GP 2.1.1, GP 3.1.2.
Return JSON only:
{"nodes":[{"label":"GenericPractice","id":"GP 2.1.1","description":"Identify the objectives and define a strategy..."}],"relationships":[{"from_id":"PA 2.1","relationship_type":"HAS_GENERIC_PRACTICE","to_id":"GP 2.1.1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"achievements": """You are an ASPICE expert. Extract ProcessAttributeAchievement nodes from Chapter 5.
Achievements are numbered lists under each PA like "1) A strategy for the performance..."
Return JSON only:
{"nodes":[{"label":"ProcessAttributeAchievement","id":"PA2.1.ACH.1","achievement_number":1,"description":"A strategy for the performance of the process is defined."}],"relationships":[{"from_id":"PA 2.1","relationship_type":"HAS_ACHIEVEMENT","to_id":"PA2.1.ACH.1"},{"from_id":"GP 2.1.1","relationship_type":"ACHIEVES","to_id":"PA2.1.ACH.1"}]}
If none found: {"nodes":[],"relationships":[]}""",

"iic": """You are an ASPICE expert. Extract InformationItem characteristics from Annex B.
Each entry has an ID like 04-04, a name, and characteristics text.
Return JSON only:
{"nodes":[{"label":"InformationItem","id":"04-04","name":"Software Architecture","characteristics":"High-level design and structure. Identifies: Overall software structure...","source_document":"ASPICE_PAM_4.1"}]}
If none found: {"nodes":[]}""",

"pa_ii": """You are an ASPICE expert. Extract DEMONSTRATED_BY relationships from Chapter 5 tables.
These show which InformationItems demonstrate ProcessAttributeAchievements.
Return JSON only:
{"relationships":[{"from_id":"PA2.1.ACH.1","relationship_type":"DEMONSTRATED_BY","to_id":"19-01"}]}
If none found: {"relationships":[]}"""
}

# ══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

def extract_text(pdf_path, start, end):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        end = min(end, len(pdf.pages))
        for i in range(start, end):
            t = pdf.pages[i].extract_text()
            if t:
                text += f"\n--- PAGE {i+1} ---\n{t}"
    return text

def call_claude(client, prompt_key, text, source_document):
    user = f"Source document: {source_document}\n\nText:\n{text}"
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=PROMPTS[prompt_key],
        messages=[{"role":"user","content":user}]
    )
    raw = response.content[0].text.strip()
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break
    return json.loads(raw)

def write_nodes(session, nodes):
    count = 0
    for node in nodes:
        label = node.get("label","")
        nid   = node.get("id","")
        if not label or not nid:
            continue
        props = {k:v for k,v in node.items() if k!="label" and v not in (None,"")}
        try:
            session.run(f"MERGE (n:{label} {{id:$id}}) SET n+=$props", id=nid, props=props)
            count += 1
        except Exception:
            pass
    return count

def write_rels(session, rels):
    count = 0
    for rel in rels:
        f  = rel.get("from_id","")
        rt = rel.get("relationship_type","")
        t  = rel.get("to_id","")
        if not all([f,rt,t]):
            continue
        props = {k:v for k,v in rel.items() if k not in ("from_id","relationship_type","to_id") and v not in (None,"")}
        try:
            session.run(f"MATCH (a{{id:$f}}) MATCH (b{{id:$t}}) MERGE (a)-[r:{rt}]->(b) SET r+=$props", f=f, t=t, props=props)
            count += 1
        except Exception:
            pass
    return count

def run_pass(pdf_path, source, prompt_key, page_ranges, client, driver, label):
    print(f"  {label}", end=" ", flush=True)
    tn=tr=te=0
    for start,end in page_ranges:
        text = extract_text(pdf_path, start, end)
        if not text.strip():
            continue
        try:
            result = call_claude(client, prompt_key, text, source)
            with driver.session() as session:
                tn += write_nodes(session, result.get("nodes",[]))
                tr += write_rels(session, result.get("relationships",[]))
            print(".", end="", flush=True)
        except json.JSONDecodeError:
            print("x", end="", flush=True); te+=1
        except Exception:
            print("!", end="", flush=True); te+=1
        time.sleep(API_DELAY)
    print(f" {tn}n {tr}r {te}e")
    return tn,tr,te

def load_seed(driver):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nodes,rels=[],[]
    with open(os.path.join(base,"data","nodes_seed.csv"),newline="",encoding="utf-8") as f:
        nodes = list(csv.DictReader(f))
    with open(os.path.join(base,"data","relationships_seed.csv"),newline="",encoding="utf-8") as f:
        rels = list(csv.DictReader(f))
    with driver.session() as session:
        n=write_nodes(session,nodes)
        r=write_rels(session,rels)
    print(f"✓ Seed: {n} nodes, {r} rels")

def ranges(pdf_path, start_page, end_page, chunk):
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
    end_page = min(end_page, total)
    return [(i, i+chunk) for i in range(start_page, end_page, chunk)]

def process_doc(pdf_path, source, client, driver):
    print(f"\n{'='*60}\n{os.path.basename(pdf_path)}\n{'='*60}")
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
    print(f"Pages: {total}")

    all_r  = ranges(pdf_path, 0, total, CHUNK_SIZE)

    if source == "ASPICE_PAM_4.1":
        proc_r = ranges(pdf_path, 27,  99, CHUNK_SIZE)
        ch5_r  = ranges(pdf_path, 98, 121, CHUNK_SIZE)
        annb_r = ranges(pdf_path,120, total, CHUNK_SIZE)
    else:
        proc_r = ranges(pdf_path, 10, 23, CHUNK_SIZE)
        ch5_r  = []
        annb_r = ranges(pdf_path, 22, total, CHUNK_SIZE)

    tn=tr=te=0
    for label, key, pgs in [
        ("Pass 1  Processes",        "processes",      all_r),
        ("Pass 2  Outcomes",         "outcomes",       proc_r),
        ("Pass 3  Base Practices",   "basepractices",  proc_r),
        ("Pass 4  Notes",            "notes",          proc_r),
        ("Pass 5  Information Items","informationitems",proc_r),
        ("Pass 6  Cross References", "crossrefs",      proc_r),
        ("Pass 7  Generic Practices","genericpractices",ch5_r),
        ("Pass 8  PA Achievements",  "achievements",   ch5_r),
        ("Pass 9  IIC Annex B",      "iic",            annb_r),
        ("Pass 10 PA->II",           "pa_ii",          ch5_r),
    ]:
        if not pgs:
            continue
        n,r,e = run_pass(pdf_path, source, key, pgs, client, driver, label)
        tn+=n; tr+=r; te+=e

    print(f"\n  Subtotal: {tn} nodes, {tr} rels, {te} errors")
    return tn,tr,te

def main():
    print("ASPICE KG — Targeted Extraction v2")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if "REPLACE_WITH" in NEO4J_URI:
        print("ERROR: Fill in CONFIG section — URI, password, API key"); return
    for path,name in [(PAM_41_PDF,"PAM 4.1"),(CS_PAM_PDF,"CS PAM")]:
        if not os.path.exists(path):
            print(f"ERROR: {name} not found at {path}"); return

    print("\nConnecting...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER,NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✓ Neo4j")
    except Exception as e:
        print(f"✗ Neo4j: {e}"); return

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✓ Claude API")
    except Exception as e:
        print(f"✗ Claude: {e}"); return

    print("\nLoading seed data...")
    load_seed(driver)

    n1,r1,e1 = process_doc(PAM_41_PDF, "ASPICE_PAM_4.1", client, driver)
    n2,r2,e2 = process_doc(CS_PAM_PDF, "CS_PAM_2.0",    client, driver)

    print(f"\n{'='*60}")
    print(f"DONE — {n1+n2} nodes, {r1+r2} rels, {e1+e2} errors")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nQuery in Neo4j Browser:")
    print("  MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY count DESC")
    driver.close()

if __name__ == "__main__":
    main()