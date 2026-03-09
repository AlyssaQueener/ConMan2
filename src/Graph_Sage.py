from graph_transformer.transformer import Transformer

transformer = Transformer()



# Just train and generate embeddings
#transformer.easy_projection()
result = transformer.project_graph_for_change_interpretation()
print("result projecting graph")
print(result)
transformer.drop_model()
result_training = transformer.train_graph()
print("training result")
print(result_training)
transformer.generate_graphsage_embeddings()