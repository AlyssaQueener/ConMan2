from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up
#Transform graph
graph_transformer = Transformer()
graph_transformer.drop_projection('test')
result = graph_transformer.projection_query_1()
print(result)



