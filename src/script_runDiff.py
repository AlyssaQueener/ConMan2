from neo4j_core.neo4j_connection import Neo4jConnection
from graph_diff.graph_diff import GraphDiff

timestamp_init = "1"
timestamp_updt = "2"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
graph_diff = GraphDiff()

graph_diff.run_diff(timestamp_init, timestamp_updt)