from datetime import datetime

from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface

paths = [
    '00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2-ARC-Model_v1_AFTER_NEO4J.ifc',
    '00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v1_AFTER_NEO4J.ifc',
    '00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v2_AFTER_NEO4J.ifc',
    '00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v3_AFTER_NEO4J.ifc'
]

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
neo4j_ifc_interface = IfcGraphInterface()

counter = 0
for path in paths:
    # timestamp = f"ts{datetime.now().strftime("%Y%m%d%H%M%S")}"
    print(f"Processing '{path}' with Timestamp '{counter}'")
    neo4j_ifc_interface.graph_2_ifc(path, timestamp=str(counter))
    counter += 1