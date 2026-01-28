from graph_transformer.transformer import Transformer

transformer = Transformer()

# Just train and generate embeddings
transformer.train_graphsage_for_change_interpretation()
transformer.generate_graphsage_embeddings()