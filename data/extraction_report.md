# ASPICE Knowledge Graph — Seed Extraction Report
Generated: 2026-09-11

## Node Counts
| Label | Count |
|---|---|
| CapabilityLevel | 6 |
| Document | 2 |
| InformationItem | 37 |
| Process | 38 |
| ProcessAttribute | 9 |
| ProcessCategory | 3 |
| ProcessGroup | 12 |

## Relationship Counts
| Type | Count |
|---|---|
| APPLIES_TO | 9 |
| BELONGS_TO | 38 |
| BIDIRECTIONAL_TRACEABILITY | 5 |
| CONSISTENCY | 3 |
| DEFINES | 15 |
| EXTENDS_PROCESS_GROUP | 2 |
| PART_OF | 12 |
| REQUIRES_FOR_LEVEL | 25 |
| SUPPLEMENTS | 1 |

## Summary
- Total nodes: 107
- Total relationships: 110
- Unique node labels: 7
- Unique relationship types: 9

## Next Steps
1. Review data/nodes_seed.csv — verify all 38 processes present
2. Review data/relationships_seed.csv — verify Annex D pairs
3. Upload ASPICE PDFs to Neo4j LLM Graph Builder
4. Use schema/aspice_schema.md as the schema prompt
5. After LLM extraction, export nodes.csv and relationships.csv from Neo4j
6. Run: python3 scripts/02_validate_graph.py
