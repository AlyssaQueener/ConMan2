from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from ifc_graph_interface.IfcGraphInterfaceBatched import IfcGraphInterfaceBatched
from graph_diff.GraphDiff import GraphDiff
from graph_diff.GraphDiffBatched import GraphDiffBatched

import time

path_1 = "./00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v1.ifc"
path_2 = "./00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v2.ifc"
path_3 = "./00_sampleData/IFC_stepP21/DepMod2025/2025-DepMod2HVAC-Model-v3.ifc"

timestamp_1_neomodel = "1_neomodel"
timestamp_2_neomodel = "2_neomodel"
timestamp_3_neomodel = "3_neomodel"
timestamp_1_batched = "1_batched"
timestamp_2_batched = "2_batched"
timestamp_3_batched = "3_batched"

#DB Connection
start_time_connection = time.time()
db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
print(f"\n#\nConnection took {time.time()-start_time_connection} seconds.\n#\n")

# DB Truncation
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parsing IFC with Neomodel
start_time_neomodel_parsing = time.time()
ifc_interface = IfcGraphInterface()
print(f"Parsing {path_1} with timestamp {timestamp_1_neomodel}.")
ifc_interface.ifc_2_graph(path_1, timestamp_1_neomodel)
print(f"Parsing {path_2} with timestamp {timestamp_2_neomodel}.")
ifc_interface.ifc_2_graph(path_1, timestamp_2_neomodel)
print(f"Parsing {path_3} with timestamp {timestamp_3_neomodel}.")
ifc_interface.ifc_2_graph(path_1, timestamp_3_neomodel)
print(f"\n#\nParsing with Neomodel took {time.time()-start_time_neomodel_parsing} seconds.\n#\n")

# Parsing IFC with batched CYPHER
start_time_batched_parsing = time.time()
ifc_interface_batched = IfcGraphInterfaceBatched()
print(f"Parsing {path_1} with timestamp {timestamp_1_batched}.")
ifc_interface_batched.ifc_2_graph(path_1, timestamp_1_batched, 20000)
print(f"Parsing {path_2} with timestamp {timestamp_2_batched}.")
ifc_interface_batched.ifc_2_graph(path_1, timestamp_2_batched, 20000)
print(f"Parsing {path_3} with timestamp {timestamp_3_batched}.")
ifc_interface_batched.ifc_2_graph(path_1, timestamp_3_batched, 20000)
print(f"\n#\nParsing with batching took {time.time()-start_time_batched_parsing} seconds.\n#\n")

# Diffing model with Neomodel
start_time_neomodel_diff = time.time()
graph_diff = GraphDiff()
print(f"Diffing models with timestamps {timestamp_1_neomodel} and {timestamp_2_neomodel}.")
graph_diff.run_diff(timestamp_1_neomodel, timestamp_2_neomodel)
print(f"Diffing models with timestamps {timestamp_2_neomodel} and {timestamp_3_neomodel}.")
graph_diff.run_diff(timestamp_2_neomodel, timestamp_3_neomodel)
print(f"\n#\nDiffing with Neomodel took {time.time()-start_time_neomodel_diff} seconds.\n#\n")

# Diffing model with batched CYPHER
start_time_batched_diff = time.time()
graph_diff_batched = GraphDiffBatched()
print(f"Diffing models with timestamps {timestamp_1_batched} and {timestamp_2_batched}.")
graph_diff_batched.run_diff(timestamp_1_batched, timestamp_2_batched, 20000)
print(f"Diffing models with timestamps {timestamp_2_batched} and {timestamp_3_batched}.")
graph_diff_batched.run_diff(timestamp_2_batched, timestamp_3_batched, 20000)
print(f"\n#\nDiffing with batching took {time.time()-start_time_batched_diff} seconds.\n#\n")