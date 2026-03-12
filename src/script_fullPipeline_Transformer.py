from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up


path_updt = "src/test2/small_changes/change_type_einzelfuncament.ifc"


path_init = "src/test2/base_base.ifc"


timestamp_init = "init_type_einzelfundament"
timestamp_updt = "updt_type_einzelfundament"

graph_type = "type_einzelfundament"


db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

## Empty DB?
#db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
#creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
#creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
#creation_graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
#path_semantic = creation_graph_patch.modify_semantic(graph_type, timestamp_init, timestamp_updt)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init,timestamp_updt,graph_type)



