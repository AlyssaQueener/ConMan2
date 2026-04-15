from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcEncodedGraphInterface import IfcEncodedGraphInterface
from graph_diff.GraphDiffSimple import GraphDiffSimple
from graph_patch.GraphPatchSimple import GraphPatchSimple
from graph_transformer.transformer import Transformer
from data_handler.clean_up import Clean_up
#Transform graph
transformer = Transformer()
#transformer.drop_projection('one_hot')
#result = transformer.projection_query_delta_one_hot()
#print(result)

#transformer.generate_graphsage_embeddings_one_hot()

from change_interpreter.knn import KNN
knn = KNN()
knn.drop_projection('knn_one_hot')
result_p = knn.projection_query_knn_one_hot()

r = knn.run_knn_filtered()
#r = knn.run_cluster_stream_one_hot()
#print(r)
#result_k = knn.run_cluster_write_one_hot()
print("*****+ Result KNN **********")
result = knn.write_similarity()
#print(result)



