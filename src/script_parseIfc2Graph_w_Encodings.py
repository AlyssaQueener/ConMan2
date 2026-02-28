from datetime import datetime

from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface_Simple import IfcGraphInterfaceSimple
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface

paths = [
    "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1.ifc",
    # "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc",
    "src/00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc"
    # "./00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v3.ifc"
    # "./wat_denn.ifc"
]

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
neo4j_ifc_interface = IfcGraphInterfaceSimple()

neo4j_original = IfcGraphInterface()

neo4j_encoded = IfcEncodedGraphInterface()



# enable next line to truncate the database before loading new data
db.cypher_query("MATCH (n) DETACH DELETE n")
test_path = "src/01_sampleData/basic-geometric-changes/base-w-wall-2x3.ifc"
test_path_2 = "src/01_sampleData/basic-geometric-changes/translated-wall.ifc"
ifc_4="src/02_sampleData/test.ifc"

ifc_4_test = "src/01_sample_data/base-example-wall-ifc4.ifc"

counter = 0
timestamp = "translated_wall_init"
timestamp_updt = "translated_wall_updt"

#for path in paths:
    # timestamp = f"ts{datetime.now().strftime("%Y%m%d%H%M%S")}"
    #print(f"Processing '{path}' with Timestamp '{counter}'")
    #neo4j_ifc_interface.ifc_2_graph(path, timestamp=str(counter))
    #counter += 1
    
#neo4j_ifc_interface.ifc_2_graph(test_path, timestamp)

neo4j_encoded.ifc_2_graph(ifc_4_test, timestamp)