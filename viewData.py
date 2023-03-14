from neo4j import GraphDatabase

# Create a driver instance for the Neo4j database
driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "password"))

# Define a Cypher query to fetch all protein nodes and their full names
query = """
MATCH (p:Protein)-[:IN_ORGANISM]->(o:Organism)
MATCH (p)-[:HAS_FULL_NAME]->(f:FullName)
MATCH (p)-[:FROM_GENE]->(g:Gene)
MATCH (p)-[:HAS_REFERENCE]->(r:Reference)
MATCH (p)-[:HAS_FEATURE]->(fe:Feature)
RETURN p.name AS protein_name, o.name AS organism_name, f.name AS full_name,
       COLLECT(DISTINCT g.name) AS gene_names, COLLECT(DISTINCT r.text) AS reference_texts,
       COLLECT(DISTINCT fe.name) AS feature_descriptions
"""

# Execute the query and fetch the results
with driver.session() as session:
    results = session.run(query)

    # Print the results
    for record in results:
        print(record)