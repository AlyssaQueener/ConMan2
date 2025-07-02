from neo4j_core.neo4j_connection import Neo4jConnection
from graph_patch.GraphPatch import GraphPatch

timestamp_init = "0"
timestamp_updt = "1"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
graph_patch = GraphPatch()

graph_patch.create_patch(timestamp_init, timestamp_updt)