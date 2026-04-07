from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up
#Transform graph
transformer = Transformer()
transformer.drop_projection('no_entity')
result = transformer.projection_query_delta_w_entity()
print(result)

#transformer.drop_model()
result_training = transformer.train_graph_delta_n_entities()
print("training result")
print(result_training)
transformer.generate_graphsage_embeddings_no_entity()



