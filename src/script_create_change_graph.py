from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up



#path_init = "src/01_sample_data/add-column-base-example-wall.ifc"
#path_updt = "src/01_sample_data/move-column-base-example-wall.ifc"


#path_init = "src/01_sample_data/base-example-wall-ifc4.ifc"
#path_init="src/01_sample_data/add-column-base-example-wall.ifc"
path_init = "src/05_SampleData/house-4/v1-house-4.ifc"


#path_updt = "src/01_sample_data/moved-wall.ifc"
#path_updt = "src/01_sample_data/add-column-base-example-wall.ifc"
path_updt = "src/05_SampleData/house-4/v2-house-4.ifc"

#project_id = "1ODmFv4Jv9ZO9fO_v2Tu_8"
timestamp_init = "v2"

timestamp_updt = "v3"





graph_type= "v2-v3-l-h"
#base_example



db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init, graph_type=graph_type)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt,graph_type=graph_type)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init, timestamp_updt, graph_type)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type, timestamp_init, timestamp_updt)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init,timestamp_updt,graph_type)

