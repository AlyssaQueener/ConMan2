from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up

 
#Transform graph
graph_type = "rotated-slab"
graph_transformer = Transformer()
graph_transformer.create_text_embeddings_for_nodes(graph_type)



