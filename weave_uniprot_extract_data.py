from datetime import datetime
from neo4j import GraphDatabase
import xml.etree.ElementTree as ET
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Set the path to your XML file
xml_file_path = "path/to/file/Q9Y261.xml"

# Set the path to the Uniprot schema file
xsd_file_path = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot.xsd"

# Connect to the Neo4j database
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))

tree = ET.parse(xml_file_path)
root = tree.getroot()

# Define the Cypher queries to create the nodes and relationships
create_fullname_query = "MERGE (f:FullName {name: $name})"
create_protein_query = "MERGE (p:Protein {name: $name})"
create_organism_query = "MERGE (o:Organism {name: $name})"
create_gene_query = "MERGE (g:Gene {name: $name})"
create_reference_query = "CREATE (r:Reference {text: $text})"
create_feature_query = "CREATE (f:Feature {name: $name})"
create_relationship_query =  "MATCH (p:Protein {name: $protein_name}) " \
                             "MATCH (o:Organism {name: $organism_name}) " \
                             "MERGE (p)-[:IN_ORGANISM]->(o) " \
                             "WITH p " \
                             "MATCH (p:Protein {name: $protein_name}) " \
                             "MATCH (f:FullName {name: $accession_name}) " \
                             "MERGE (p)-[:HAS_FULL_NAME]->(f) " \
                             "WITH p " \
                             "UNWIND $gene_names AS gene_name " \
                             "MATCH (g:Gene {name: gene_name}) " \
                             "MERGE (p)-[:FROM_GENE]->(g) " \
                             "WITH p " \
                             "UNWIND $reference_texts AS reference_text " \
                             "MATCH (r:Reference {text: reference_text}) " \
                             "MERGE (p)-[:HAS_REFERENCE]->(r)" \
                             "WITH p " \
                             "UNWIND $feature_descriptions as feature_description " \
                             "MATCH (f:Feature {name: feature_description}) " \
                             "MERGE (p)-[:HAS_FEATURE]->(f)"

# Define a function to execute the Cypher queries
def add_data_to_database(accession_name, protein_name, gene_names, organism_names, reference_texts, feature_descriptions, session):
    # Create the fullname node
    session.run(create_fullname_query, name=accession_name)

    # Create the protein node
    session.run(create_protein_query, name=protein_name)

    # Create the organism node
    for organism_name in organism_names:
        session.run(create_organism_query, name=organism_name)

    # Create the gene nodes
    for gene_name in gene_names:
        session.run(create_gene_query, name=gene_name)

    # Create the gene nodes
    for feature in feature_descriptions:
        session.run(create_feature_query, name=feature)

    # Create the reference nodes
    for reference_text in reference_texts:
        session.run(create_reference_query, text=reference_text)

    # Create the relationships
    session.run(create_relationship_query, accession_name=accession_name,protein_name=protein_name,
                organism_name=organism_names[0], gene_names=gene_names,
                feature_descriptions=feature_descriptions, reference_texts=reference_texts)

def insert_data():
    # Iterate over the entries in the XML file and add the data to the database
    with driver.session() as session:
        # Access the protein, gene, organism, and reference elements
        for entry in root.findall("{http://uniprot.org/uniprot}entry"):
            # Get the FullName name
            accession = entry.find("{http://uniprot.org/uniprot}protein/{http://uniprot.org/uniprot}recommendedName/{http://uniprot.org/uniprot}fullName")
            accession_name = accession.text if accession is not None else None

            # Get the protein name
            protein = entry.find("{http://uniprot.org/uniprot}accession")
            protein_name = protein.text if protein is not None else None

            # Get the gene name(s)
            genes = entry.findall("{http://uniprot.org/uniprot}gene/{http://uniprot.org/uniprot}name[@type='primary']")
            gene_names = [gene.text for gene in genes]

            # Get the organism name(s)
            organisms = entry.findall("{http://uniprot.org/uniprot}organism/{http://uniprot.org/uniprot}name")
            organism_names = [organism.text for organism in organisms]

            # Get the feature(s)
            features = entry.findall("{http://uniprot.org/uniprot}feature")
            feature_descriptions = [feature.get("description") for feature in features if feature.get("description") is not None]

            # Get the references
            references = entry.findall("{http://uniprot.org/uniprot}reference")
            reference_texts = [ref.find("{http://uniprot.org/uniprot}citation/{http://uniprot.org/uniprot}title").text for ref in references]

            # Insert data on Neo4j
            add_data_to_database(accession_name, protein_name, gene_names, organism_names, reference_texts, feature_descriptions, session)

            # Do something with the extracted information
            print("Accession name: ", accession_name)
            print("Protein name: ", protein_name)
            print("Gene name(s): ", gene_names)
            print("Organism name(s): ", organism_names)
            print("Feature description(s)", feature_descriptions)
            print("Reference texts: ", reference_texts)

    session.close()

dag = DAG(
    'weave_uniprot_to_neo4j',
    start_date=datetime(2023, 3, 13),
    schedule_interval=None
)

insert_data_task = PythonOperator(
    task_id='insert_data',
    python_callable=insert_data,
    dag=dag
)