import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

FHIR_ONTOLOGY_DATA = {
    "nodes": [
        {"label": "FHIR_Condition", "props": {"fhir_id": "c-101", "icd10_code": "M23.2", "display_name": "Lateral Meniscus Tear"}},
        {"label": "FHIR_Condition", "props": {"fhir_id": "c-102", "icd10_code": "M54.5", "display_name": "Lumbar Radiculopathy"}},
        {"label": "FHIR_Procedure", "props": {"fhir_id": "p-201", "cpt_code": "73721", "display_name": "MRI Lower Extremity Joint"}},
        {"label": "FHIR_Procedure", "props": {"fhir_id": "p-202", "cpt_code": "72148", "display_name": "MRI Lumbar Spine"}},
        {"label": "HL7_CoverageRule", "props": {"rule_id": "r-301", "requirement": "Prior Authorization Required", "copay": 250.00}},
        {"label": "HL7_CoverageRule", "props": {"rule_id": "r-302", "requirement": "6 Weeks Physical Therapy Prerequisite Required", "copay": 40.00}}
    ],
    "relationships": [
        {"source_id": "c-101", "target_id": "p-201", "type": "INDICATES_PROCEDURE"},
        {"source_id": "c-102", "target_id": "p-202", "type": "INDICATES_PROCEDURE"},
        {"source_id": "p-201", "target_id": "r-301", "type": "GOVERNED_BY_RULE"},
        {"source_id": "p-202", "target_id": "r-302", "type": "GOVERNED_BY_RULE"}
    ]
}

def seed_fhir_graph():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        print("🧹 Flushing graph database topology...")
        session.run("MATCH (n) DETACH DELETE n")
        
        print("🧬 Injecting standardized FHIR & HL7 ontology nodes...")
        for node in FHIR_ONTOLOGY_DATA["nodes"]:
            session.run(f"CREATE (n:{node['label']}) SET n = $props", props=node["props"])
            
        print("🕸️ Wiring standardized semantic relation paths...")
        fallback_cypher = """
        MATCH (s), (t) 
        WHERE (s.fhir_id = $source_id) AND (t.fhir_id = $target_id OR t.rule_id = $target_id)
        FOREACH (_ IN CASE WHEN $type = 'INDICATES_PROCEDURE' THEN ELSE [] END | CREATE (s)-[:INDICATES_PROCEDURE]->(t))
        FOREACH (_ IN CASE WHEN $type = 'GOVERNED_BY_RULE' THEN ELSE [] END | CREATE (s)-[:GOVERNED_BY_RULE]->(t))
        """
        for rel in FHIR_ONTOLOGY_DATA["relationships"]:
            session.run(fallback_cypher, source_id=rel["source_id"], target_id=rel["target_id"], type=rel["type"])
                
    driver.close()
    print("✨ myHealthInsure Graph Ontology Ingestion Complete!")

if __name__ == "__main__":
    seed_fhir_graph()
