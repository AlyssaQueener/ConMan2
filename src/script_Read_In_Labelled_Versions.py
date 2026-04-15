from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.ModifierWithLabel import ModifierWithLabel
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

models = [
    {
        "path_init": "src/07_VersionWithLabel/BaseTC.ifc",
        "timestamp_init": "v1-tc",
        "path_updt": "src/07_VersionWithLabel/Type-changes.ifc",
        "timestamp_updt": "v2-tc",
        "graph_type": "tc",
        "label": "TC"
    },
    {
        "path_init": "src/07_VersionWithLabel/BaseTranslation.ifc",
        "timestamp_init": "v1-translation",
        "path_updt": "src/07_VersionWithLabel/translation-graph.ifc",
        "timestamp_updt": "v2-translation",
        "graph_type": "translation",
        "label": "Translation"
    },
    {
        "path_init": "src/07_VersionWithLabel/rotation-base.ifc",
        "timestamp_init": "v1-rotation",
        "path_updt": "src/07_VersionWithLabel/rotated1.ifc",
        "timestamp_updt": "v2-rotation",
        "graph_type": "rotation",
        "label": "Rotation"
    },
    {
        "path_init": "src/07_VersionWithLabel/size-graph.ifc",
        "timestamp_init": "v1-size",
        "path_updt": "src/07_VersionWithLabel/size-2.ifc",
        "timestamp_updt": "v2-size",
        "graph_type": "size",
        "label": "Size"
    }
]

for m in models:
    path_init = m["path_init"]
    timestamp_init = m["timestamp_init"]
    path_updt = m["path_updt"]
    timestamp_updt = m["timestamp_updt"]
    graph_type = m["graph_type"]
    label = m["label"]
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
    modifier = ModifierWithLabel()
    path_semantic = modifier.modify_semantic(graph_type, timestamp_init, timestamp_updt, label)
 
    #Transform graph
    graph_transformer = Transformer()
    graph_transformer.create_change_graph(timestamp_init,timestamp_updt,graph_type)
        