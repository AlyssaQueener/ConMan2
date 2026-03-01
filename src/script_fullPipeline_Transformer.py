from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from ifc_graph_interface.IfcGraphInterface_Simple import IfcGraphInterfaceSimple
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up



path_init = "src/01_sample_data/base-example-wall-ifc4.ifc"
#path_updt = "src/01_sampleData/basic-geometric-changes/moved-window-2x3.ifc"
path_updt = "src/01_sample_data/moved-wall.ifc"

#project_id = "1ODmFv4Jv9ZO9fO_v2Tu_8"
timestamp_init = "init_moved_wall"
timestamp_updt = "updt_moved_wall"

graph_type = "moved_wall"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt)

project_id = creation_neo4j_ifc_interface.get_project_id_from_timestamp(timestamp_init)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(project_id, timestamp_init, timestamp_updt)

clean_up = Clean_up()

#cleaned_path = clean_up.clean_semantic(path_semantic, timestamp_init, timestamp_updt)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(path_semantic,timestamp_init,timestamp_updt,graph_type)
#graph_transformer.create_text_embeddings_for_nodes(graph_type)



