# Versioning Manager as BIM Level 3 CDE

## Installation and Setup

### Forking the Repo

Start with creating a fork of this repository by clicking the fork symbol in the upper right corner. 
You will be asked to specify the target hub (normally, only your personal space can be chosen).
Once forking is done, run `git clone` to download the repo on your machine.

### Installation and Preliminary Settings

One the repository is cloned, navigate to `<...>/conman2/src/`. This is the base directory of the application.

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

- OPTIONAL: Download and install [Anaconda](https://www.anaconda.com/products/individual).

- Install the Python requirements using: `pip install -r requirements.txt`.

## Translating IFC Models from/to Graphs

A good getting-started point is the import of an IFC model into the graph database. 
The python script `script_parseIfc2Graph.py` provides all necessary settings and method calls. 
Please specify the correct path to the model(s) you'd like to parse into the database. 

A graph representation of an IFC model can be parsed back into an SPF-based representation using the python script `script_parseGraph2Ifc.py`.

## Caveats Concerning Edge Case IFC Classes
The IFC schema includes cases where the general translation of entities, relations, and attributes does not work. One of these cases is the attribute _TrueNorth_,  which the IFC class _IfcGeometricRepresentationSubContext_ derives from its parent class _IfcGeometricRepresentationContext_. It is therefore, ignored [here](https://gitlab.lrz.de/sebastian.esser/conman2/-/blob/7086b80518b6f310adba0fe5fa6154ca92cf30de/src/ifc_graph_interface/IfcGraphInterface.py#L199). If similar cases arise, add the respective key name to the check there.

Should similar

## Python Packages and Dependencies
| Package         | URL           | License |
| --------------- |:-------------:| ------- |
|[IfcOpenShell](http://ifcopenshell.org/)| | |
|[Neomodel](https://neomodel.readthedocs.io/)| | |
