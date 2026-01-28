from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up

#### examples with slab
path_init = "src/01_sampleData/basic-geometric-changes/init-version-2x3-coordination-view.ifc"
path_updt="src/01_sampleData/basic-geometric-changes/translated-slab-2x3.ifc"
#path_updt="src/01_sampleData/basic-geometric-changes/rotated-slab-2x3.ifc"

#path_init = "src/01_sampleData/basic-geometric-changes/base-w-wall-2x3.ifc"
#path_updt = "src/01_sampleData/basic-geometric-changes/moved-window-2x3.ifc"
#path_updt = "src/01_sampleData/basic-geometric-changes/scaled-wall-2x3.ifc"

#project_id = "1ODmFv4Jv9ZO9fO_v2Tu_8"
timestamp_init = "init_translated_slab"
timestamp_updt = "updt_translated_slab"

graph_type = "translated_slab"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt)

project_id = creation_neo4j_ifc_interface.get_project_id_from_timestamp(timestamp_init)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiff()
creation_graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatch()
path_semantic = creation_graph_patch.create_patch_semantic(project_id, timestamp_init, timestamp_updt)

clean_up = Clean_up()

cleaned_path = clean_up.clean_semantic(path_semantic, timestamp_init, timestamp_updt)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(cleaned_path,timestamp_init,timestamp_updt,graph_type)
graph_transformer.create_text_embeddings_for_nodes(graph_type)



