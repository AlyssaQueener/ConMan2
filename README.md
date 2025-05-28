# Versioning Manager as BIM Level 3 CDE

## Installation and Setup

### Forking the repo

Start with creating a fork of this repository by clicking the fork symbol in the upper right corner. 
You will be asked to specify the target hub (normally, only your personal space can be chosen).
Once forking is done, run `git clone` to download the repo on your machine. 

### Installation and preliminary settings

The codebase acts as an intermediate server between an end-user and a running neo4j graph database. 
Therefore, please download and install the following products on your machine before continuing: 

 - Download and install the latest version of [neo4j Desktop](https://neo4j.com/download-v2/)
   You can test its successful installation by creating and starting a new database instance. 

   The DB browser of running neo4j instances is accessible port 7474 (http). 

    Default credentials: 
    | var   | value      |
    | ----- |:----------:|
    | user  | `neo4j`    |
    | pw    | `password` |

- Install all Python dependencies by running:
```shell
pip install -r requirements.txt
```


## Translating IFC models from/to graphs

A good getting-started point is the import of an IFC model into the graph database. 
The python script `script_parseIfc2Graph.py` provides all necessary settings and method calls. 
Please specify the correct path to the model(s) you'd like to parse into the database. 

Once a model is parsed into the database, it gets accessed using its timestamp label (referred as `tsYYYYMMDDTHHMMSS` (e.g., `ts20121017T152740`)). 

The graph can be queried using the CYPHER query language, e.g.: 
```cypher
MATCH (n:ts20121017T152740) RETURN n LIMIT 35
```

A graph representation of an IFC model can be parsed back into an SPF-based representation using the python script `script_parseGraph2Ifc.py` 

# Python packages and dependencies
| Package         | URL           | License |
| --------------- |:-------------:| ------- |
|[IfcOpenShell](http://ifcopenshell.org/)| | |
|[Neo4j Driver](https://pypi.org/project/neo4j/)| | |