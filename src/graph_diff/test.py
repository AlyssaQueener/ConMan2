from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, SecondaryNode, ConnectionNode, InlineNode
from graph_diff.graph_diff import GraphDiff

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

db.cypher_query("match (n) detach delete n")

# Init

proj_init = PrimaryNode(
    EntityType="IfcProject",
    p21_id="#1",
    GlobalId="1234",
    timestamp="1"
).save()

wall_init_same = PrimaryNode(
    EntityType="IfcWall",
    p21_id="#2",
    GlobalId="2345",
    timestamp="1",
    size="2,3"
).save()

wall_init_diff = PrimaryNode(
    EntityType="IfcWall",
    GlobalId="3456",
    p21_id="#3",
    timestamp="1",
    size="2,7"
).save()

window_init_only = SecondaryNode(
    EntityType="IfcWindow",
    p21_id="#4",
    timestamp="1"
).save()

window_init_same = SecondaryNode(
    EntityType="IfcWindow",
    p21_id="#5",
    timestamp="1"
).save()

# Updt

proj_updt = PrimaryNode(
    EntityType="IfcProject",
    p21_id="#1",
    GlobalId="1234",
    timestamp="2"
).save()

wall_updt_same = PrimaryNode(
    EntityType="IfcWall",
    p21_id="#2",
    GlobalId="2345",
    timestamp="2",
    size="2,3"
).save()

wall_updt_diff = PrimaryNode(
    EntityType="IfcWall",
    p21_id="#3",
    GlobalId="3456",
    timestamp="2",
    size="2,11"
).save()

window_updt_same = SecondaryNode(
    EntityType="IfcWindow",
    p21_id="#5",
    timestamp="2"
).save()


proj_init.relation.connect(wall_init_same, {"rel_type": "wall", "list_index": 0}).save()
proj_init.relation.connect(wall_init_diff, {"rel_type": "wall", "list_index": 1}).save()

proj_updt.relation.connect(wall_updt_same, {"rel_type": "wall", "list_index": 0}).save()
proj_updt.relation.connect(wall_updt_diff, {"rel_type": "wall", "list_index": 1}).save()

wall_init_same.relation.connect(window_init_same, {"rel_type": "wall", "list_index": 0})
wall_updt_same.relation.connect(window_updt_same, {"rel_type": "wall", "list_index": 0})

wall_init_same.relation.connect(window_init_only, {"rel_type": "wall", "list_index": 1}).save()

graph_diff = GraphDiff()

graph_diff.run_diff("1", "2")