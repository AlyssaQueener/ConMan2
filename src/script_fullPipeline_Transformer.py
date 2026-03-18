from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up


#path_updt = "src/test2/small_changes/change_type_einzelfuncament.ifc"



path_init = "src/test2/base_base.ifc"


path_updt = "src/test2/small_changes/change-geschossdecke-move-treppe.ifc"


timestamp_init = "init_move_stairs"
timestamp_updt = "updt_move_stairs"

graph_type = "move_stairs"


db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

## Empty DB?
#db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init, graph_type=graph_type)
print(f"Parsing {path_updt} with timestamp {timestamp_updt}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt, timestamp=timestamp_updt, graph_type=graph_type)

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


#############

path_updt_1 = "src/test2/small_changes/change-size-geschossdecke.ifc"


timestamp_init_1 = "init_size_geschossdecke"
timestamp_updt_1 = "updt_size_geschossdecke"

graph_type_1 = "size_geschossdecke"





# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init_1}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init_1, graph_type=graph_type_1)
print(f"Parsing {path_updt_1} with timestamp {timestamp_updt_1}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt_1, timestamp=timestamp_updt_1, graph_type=graph_type_1)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init_1, timestamp_updt_1, graph_type_1)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type_1, timestamp_init_1, timestamp_updt_1)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init_1,timestamp_updt_1,graph_type_1)

#############

path_updt_2 = "src/test2/small_changes/change-type-geländer.ifc"


timestamp_init_2 = "init_type_geländer"
timestamp_updt_2 = "updt_type_geländer"

graph_type_2 = "type_geländer"





# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init_2}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init_2, graph_type=graph_type_2)
print(f"Parsing {path_updt_2} with timestamp {timestamp_updt_2}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt_2, timestamp=timestamp_updt_2, graph_type=graph_type_2)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init_2, timestamp_updt_2, graph_type_2)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type_2, timestamp_init_2, timestamp_updt_2)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init_2,timestamp_updt_2,graph_type_2)

#############

path_updt_3 = "src/test2/small_changes/move-door.ifc"


timestamp_init_3 = "init_move_door"
timestamp_updt_3 = "updt_move_door"

graph_type_3 = "move_door"





# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init_3}.")

creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init_3, graph_type=graph_type_3)

print(f"Parsing {path_updt_3} with timestamp {timestamp_updt_3}.")

creation_neo4j_ifc_interface.ifc_2_graph(path_updt_3, timestamp=timestamp_updt_3, graph_type=graph_type_3)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init_3, timestamp_updt_3, graph_type_3)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type_3, timestamp_init_3, timestamp_updt_3)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init_3,timestamp_updt_3,graph_type_3)

#############

path_updt_4 = "src/test2/small_changes/move-long-column.ifc"


timestamp_init_4 = "init_move_long_column"
timestamp_updt_4 = "updt_move_long_column"

graph_type_4 = "move_long_column"





# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init_4}.")

creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init_4, graph_type=graph_type_4)

print(f"Parsing {path_updt_4} with timestamp {timestamp_updt_4}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt_4, timestamp=timestamp_updt_4, graph_type=graph_type_4)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init_4, timestamp_updt_4, graph_type_4)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type_4, timestamp_init_4, timestamp_updt_4)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init_4,timestamp_updt_4,graph_type_4)

#############

path_updt_5 = "src/test2/small_changes/change_type_einzelfuncament.ifc"


timestamp_init_5 = "init_type_fundament"
timestamp_updt_5 = "updt_type_fundament"

graph_type_5 = "type_fundament"





# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init_5}.")

creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init_5, graph_type=graph_type_5)

print(f"Parsing {path_updt_4} with timestamp {timestamp_updt_4}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_updt_5, timestamp=timestamp_updt_5, graph_type=graph_type_5)

# Run Diff
print(f"Running diff.")
creation_graph_diff = GraphDiffSimple()
creation_graph_diff.run_diff(timestamp_init_5, timestamp_updt_5, graph_type_5)

# Create Patch
print(f"Creating patch.")
creation_graph_patch = GraphPatchSimple()
path_semantic = creation_graph_patch.modify_semantic(graph_type_5, timestamp_init_5, timestamp_updt_5)
 
#Transform graph
graph_transformer = Transformer()
graph_transformer.create_change_graph(timestamp_init_5,timestamp_updt_5,graph_type_5)