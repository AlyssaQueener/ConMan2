from graph_patch.GraphPatch import GraphPatch
from neo4j_core.neo4j_model import PrimaryNode, ConnectionNode
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from neo4j_core.neo4j_connection import Neo4jConnection
import json

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

path = "./00_sampleData/IFC_stepP21/diss-casestudy/ARC-v1-purified.ifc"

ifc_interf = IfcGraphInterface()
ifc_interf.ifc_2_graph(path, "TEST")

prim_and_conn = PrimaryNode.nodes.all() + ConnectionNode.nodes.all()

graph_patch = GraphPatch()

for node in prim_and_conn:
    graph_patch.create_unique_path_mappings(node)

with open("./TEST_UNIQUE_PATHS_TO_NODE.json", "w") as f:
    json.dump(graph_patch.unique_paths_to_node_ids_mapping, f, indent=4)

with open("./TEST_NODE_TO_UNIQUE_PATHS.json", "w") as f:
    json.dump(graph_patch.node_ids_to_unique_paths_mapping, f, indent=4)
