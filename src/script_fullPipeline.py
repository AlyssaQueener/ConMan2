from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from graph_diff.graph_diff import GraphDiff
from graph_patch.graph_patch import GraphPatch

# paths = [
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc",
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc",
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc"
# ]

path_init = "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc"
path_updt = "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

timestamp_init = "init"
timestamp_updt = "updt"

# Parse IFC to Graph
neo4j_ifc_interface = IfcGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt)

# Run Diff
print(f"Running diff.")
graph_diff = GraphDiff()
graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create Patch
print(f"Creating patch.")
graph_patch = GraphPatch()
graph_patch.create_patch(timestamp_init, timestamp_updt, unique_paths=graph_diff.unique_paths)
