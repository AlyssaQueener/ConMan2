from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch

# paths = [
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc",
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v2-purified.ifc",
#     "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc"
# ]

path_init = "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc"
path_updt = "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v3-purified.ifc"

timestamp_init = "init"
timestamp_updt = "updt"



##################
# Patch Creation #
##################

print('''##################
# Patch Creation #
##################''')

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiff()
creation_graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatch()
creation_graph_patch.create_patch(timestamp_init, timestamp_updt)



#####################
# Patch Application #
#####################

print('''#####################
# Patch Application #
#####################''')

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
application_neo4j_ifc_interface = IfcGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
application_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)

# Load Patch from File
application_graph_patch = GraphPatch()
application_graph_patch.load_patch_from_file(path_sema="./Patch_Sema_init_updt.json", path_topo="./Patch_Topo_init_updt.json")

#Apply Patch
print(f"Applying Patch.")
application_graph_patch.apply_patch(timestamp_init, timestamp_updt)

application_neo4j_ifc_interface.graph_2_ifc("./wat_denn.ifc", timestamp="init")
