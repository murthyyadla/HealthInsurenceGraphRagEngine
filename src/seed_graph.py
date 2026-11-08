import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Force local environment variable lookups
load_dotenv()

# Read the connection configuration variables natively
NEO4J_URI = "bolt://127.0.0.1:7687"  # Use localhost when running natively outside Docker
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

def build_myhealthinsure_ontology():
    print(f"📡 Connecting to Neo4j instance at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Wipe out old corrupted elements to start fresh
            session.run("MATCH (n) DETACH DELETE n")
            
            print("🏗️ Creating structural health insurance ontology nodes...")
            # Seed standard medical conditions
            session.run("CREATE (:FHIR_Condition {fhir_id: 'C001', icd10_code: 'M23.22', display_name: 'Lateral Meniscus Tear'})")
            session.run("CREATE (:FHIR_Condition {fhir_id: 'C002', icd10_code: 'M23.23', display_name: 'Medial Meniscus Tear'})")
            
            # Seed corresponding procedures
            session.run("CREATE (:FHIR_Procedure {fhir_id: 'P001', cpt_code: '29881', display_name: 'Arthroscopic Meniscectomy'})")
            session.run("CREATE (:FHIR_Procedure {fhir_id: 'P002', cpt_code: '73721', display_name: 'Knee MRI Scan'})")
            
            # Seed corporate coverage rules
            session.run("CREATE (:HL7_CoverageRule {rule_id: 'R001', requirement: 'Prior Authorization Required', copay: '$250', co_insurance: '20%'})")
            
            print("🔗 Constructing relational architecture paths...")
            # Bind condition to procedure
            session.run("""
                MATCH (c:FHIR_Condition {fhir_id: 'C001'}), (p:FHIR_Procedure {fhir_id: 'P002'})
                CREATE (c)-[:INDICATES_PROCEDURE]->(p)
            """)
            # Bind procedure to standard coverage rule
            session.run("""
                MATCH (p:FHIR_Procedure {fhir_id: 'P002'}), (r:HL7_CoverageRule {rule_id: 'R001'})
                CREATE (p)-[:GOVERNED_BY_RULE]->(r)
            """)
            
        driver.close()
        print("✨ myHealthInsure Graph Ontology Ingestion Complete!")
    except Exception as e:
        print(f"❌ Failed to seed graph data database: {str(e)}")

if __name__ == "__main__":
    build_myhealthinsure_ontology()
