
# Parsing and Importing Data from UniProt into Neo4j

This repository contains Python code for parsing data from a UniProt XML file and importing it into a Neo4j graph database.

## Installation

To run this code, you will need to have the following software installed:

- Python 3.x
- pip
- Neo4j
- Airflow
After installing Python and pip, run the following command to install the necessary Python packages:

```bash
  pip install neo4j xml airflow
```

## Usage

### step 1: Download and Extract the UniProt XML File
Download the latest UniProt XML file from the UniProt website and extract it to a local directory.

### Step 2: Set the XML and XSD File Paths
Open the import_data.py file and set the `xml_file_path` variable to the path of the UniProt XML file you downloaded in Step 1.

You should also set the `xsd_file_path` variable to the path of the UniProt XSD schema file.

### Step 3: Set Up the Neo4j Database
Make sure you have a local instance of Neo4j running on your machine. You can download Neo4j from the Neo4j website.

Once you have Neo4j running, open the `import_data.py` file and set the uri, username, and password variables to the appropriate values for your Neo4j instance.

### Step 4: Run the Airflow DAG
To run the code, you will use Airflow, which is a platform for programmatically authoring, scheduling, and monitoring workflows.

First, start the Airflow web server by running the following command:

```
airflow webserver
```

Then, in a new terminal window, start the Airflow scheduler by running the following command:
```
airflow scheduler
```

Finally, go to the Airflow web interface at http://localhost:8080 and turn on the parse_uniprot_xml DAG. This will start the DAG and run the import_data.py file.

## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [@anicetojunior](https://www.github.com/anicetojunior)
