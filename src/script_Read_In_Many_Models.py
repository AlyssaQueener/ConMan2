from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

models = [
    {
        "path_init": "src/05_SampleData/large-house/v1-large-house.ifc",
        "timestamp_init": "v1-large-house",
        "path_updt": "src/05_SampleData/large-house/v2-large-house.ifc",
        "timestamp_updt": "v2-large-house-updt",
        "graph_type": "v1-v2-large-house"
    },
    {
        "path_init": "src/05_SampleData/large-house/v2-large-house.ifc",
        "timestamp_init": "v2-large-house",
        "path_updt": "src/05_SampleData/large-house/v3-large-house.ifc",
        "timestamp_updt": "v3-large-house-updt",
        "graph_type": "v2-v3-large-house"
    },
    {
        "path_init": "src/05_SampleData/large-house/v3-large-house.ifc",
        "timestamp_init": "v3-large-house",
        "path_updt": "src/05_SampleData/large-house/v4-large-house.ifc",
        "timestamp_updt": "v4-large-house-updt",
        "graph_type": "v3-v4-large-house"
    },
    {
        "path_init": "src/05_SampleData/house-4/v1-house-4.ifc",
        "timestamp_init": "v1-house-4",
        "path_updt": "src/05_SampleData/house-4/v2-house-4.ifc",
        "timestamp_updt": "v2-house-4-updt",
        "graph_type": "v1-v2-house-4"
    },
    {
        "path_init": "src/05_SampleData/house-4/v2-house-4.ifc",
        "timestamp_init": "v2-house-4",
        "path_updt": "src/05_SampleData/house-4/v3-house-4.ifc",
        "timestamp_updt": "v3-house-4-updt",
        "graph_type": "v2-v3-house-4"
    },
    {
        "path_init": "src/05_SampleData/house-4/v3-house-4.ifc",
        "timestamp_init": "v3-house-4",
        "path_updt": "src/05_SampleData/house-4/v4-house-4.ifc",
        "timestamp_updt": "v4-house-4-updt",
        "graph_type": "v3-v4-house-4"
    },
    {
        "path_init": "src/05_SampleData/house-4/v4-house-4.ifc",
        "timestamp_init": "v4-house-4",
        "path_updt": "src/05_SampleData/house-4/v5-house-4.ifc",
        "timestamp_updt": "v5-house-4-updt",
        "graph_type": "v4-v5-house-4"
    },
    {
        "path_init": "src/05_SampleData/house-2/v1-house-2.ifc",
        "timestamp_init": "v1-house-2",
        "path_updt": "src/05_SampleData/house-2/v2-house-2.ifc",
        "timestamp_updt": "v2-house-2-updt",
        "graph_type": "v1-v2-house-2"
    },
    {
        "path_init": "src/05_SampleData/house-2/v2-house-2.ifc",
        "timestamp_init": "v2-house-2",
        "path_updt": "src/05_SampleData/house-2/v3-house-2.ifc",
        "timestamp_updt": "v3-house-2-updt",
        "graph_type": "v2-v3-house-2"
    },
    {
        "path_init": "src/05_SampleData/house-3/v1-house3.ifc",
        "timestamp_init": "v1-house-3",
        "path_updt": "src/05_SampleData/house-3/v2-house-3.ifc",
        "timestamp_updt": "v2-house-3-updt",
        "graph_type": "v1-v2-house-3"
    }
]

for m in models:
    path_init = m["path_init"]
    timestamp_init = m["timestamp_init"]
    path_updt = m["path_updt"]
    timestamp_updt = m["timestamp_updt"]
    graph_type = m["graph_type"]
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
        