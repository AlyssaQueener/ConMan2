from datetime import datetime

from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface

paths = [
    # "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc",
    # "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc",
    "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc",
    # "./00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v3.ifc"
    # "./wat_denn.ifc"
]

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
neo4j_ifc_interface = IfcGraphInterface()

db.cypher_query("MATCH (n) DETACH DELETE n")

counter = 0

for path in paths:
    # timestamp = f"ts{datetime.now().strftime("%Y%m%d%H%M%S")}"
    print(f"Processing '{path}' with Timestamp '{counter}'")
    neo4j_ifc_interface.ifc_2_graph(path, timestamp=str(counter))
    counter += 1