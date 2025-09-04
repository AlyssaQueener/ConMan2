from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import *
from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch

# This script demonstrates the example from the Dissertation (https://mediatum.ub.tum.de/doc/1736912/1736912.pdf#page=120).
# It does not in any way adhere to the IFC standard and is simply used to show the logic of the graph-based Diff and Patch creation.
# The nodes are still IFC entites, as this is relevant for some parts of the logic.

# Connect to the db and clear it.
print("Clearing the database.")
db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Define custom timestamps
timestamp_init = "diss_init"
timestamp_updt = "diss_updt"

# Create the nodes using neomodel.
print("Creating initial and updated graph.")
node_1 = PrimaryNode(
    GlobalId="1",
    EntityType="IfcProject",
    p21_id="#1",
    timestamp=timestamp_init
).save()

node_2 = PrimaryNode(
    GlobalId="2",
    EntityType="IfcWall",
    p21_id="#2",
    timestamp=timestamp_init
).save()

node_3 = SecondaryNode(
    EntityType="IfcDirection",
    p21_id="#3",
    timestamp=timestamp_init
).save()

node_4 = PrimaryNode(
    GlobalId="1",
    EntityType="IfcProject",
    p21_id="#1",
    timestamp=timestamp_updt
).save()

node_5 = ConnectionNode(
    GlobalId="5",
    EntityType="IfcRelAssociatesMaterial",
    p21_id="#5",
    timestamp=timestamp_updt
).save()

node_6 = SecondaryNode(
    EntityType="IfcDirection",
    p21_id="#5",
    timestamp=timestamp_updt
).save()

node_7 = SecondaryNode(
    EntityType="IfcMaterial",
    p21_id="#7",
    timestamp=timestamp_updt
).save()

node_8 = PrimaryNode(
    GlobalId="8",
    EntityType="IfcWall",
    p21_id="#8",
    timestamp=timestamp_updt
).save()

# Connect the nodes using neomodel.
node_1.relation_to.connect(node_2, {"rel_type": "a", "list_index": 0})
node_1.relation_to.connect(node_3, {"rel_type": "b", "list_index": 1})
node_2.relation_to.connect(node_3, {"rel_type": "c", "list_index": 0})
node_4.relation_to.connect(node_5, {"rel_type": "d", "list_index": 0})
node_4.relation_to.connect(node_6, {"rel_type": "b", "list_index": 1})
node_5.relation_to.connect(node_7, {"rel_type": "e", "list_index": 0})
node_5.relation_to.connect(node_8, {"rel_type": "f", "list_index": 1})

input("The initial and updated graphs have been created in the Neo4j database. You can look at the structure now. Press Enter to continue...")

# Run the Diff between the models to find equivalent nodes and add equivalent_to edges.
print("Running the diff between the initial and updated graph.")
graph_diff = GraphDiff()
graph_diff.run_diff(timestamp_init, timestamp_updt)

# Create the Patch based on the Diff results.
print("Creating the patch based on the diff results.")
graph_patch = GraphPatch(timestamp_init, timestamp_updt)
graph_patch.create_patch("1", timestamp_init, timestamp_updt)

input("The patch has been created and saved to files (./patch_data/Patch_Topo_diss_init_diss_updt.json and ./patch_data/Patch_Sema_diss_init_diss_updt.json). You can look at the graph with the 'equivalent_to' edges added and the structure of the patch files now. Press Enter to continue...")

# Now, we demonstrate the application of the patch to the initial graph.
print("Clearing the database again.")
db.cypher_query("MATCH (n) DETACH DELETE n")

# Recreate the init graph using neomodel.
print("Recreating the initial graph.")
node_1 = PrimaryNode(
    GlobalId="1",
    EntityType="IfcProject",
    p21_id="#1",
    timestamp=timestamp_init
).save()

node_2 = PrimaryNode(
    GlobalId="2",
    EntityType="IfcWall",
    p21_id="#2",
    timestamp=timestamp_init
).save()

node_3 = SecondaryNode(
    EntityType="IfcDirection",
    p21_id="#3",
    timestamp=timestamp_init
).save()

node_1.relation_to.connect(node_2, {"rel_type": "a", "list_index": 0})
node_1.relation_to.connect(node_3, {"rel_type": "b", "list_index": 1})
node_2.relation_to.connect(node_3, {"rel_type": "c", "list_index": 0})

input("The initial graph has been recreated in the Neo4j database. You can look at the structure now. Press Enter to continue...")

# Load the Patch from file and apply it to the init graph.
print("Loading and applying the patch to the initial graph.")
graph_patch = GraphPatch(timestamp_init, timestamp_updt)
graph_patch.load_patch_from_file(path_sema="./patch_data/Patch_Sema_1_diss_init_diss_updt.json", path_topo="./patch_data/Patch_Topo_1_diss_init_diss_updt.json")
graph_patch.apply_patch(timestamp_init, timestamp_updt)

print("The patch has been applied. You can look at the updated graph structure now.")