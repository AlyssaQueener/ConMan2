from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import *
from operator import add

class GraphEmbeddingCalculator:
    db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
    
    @staticmethod
    def calculate_mean_graph_embedding(graph_type):
        """
        Calculate mean graph embeddings aggregated by change type
        """
        graph_embeddings_mean_statistic = {}
        nodes = Node.nodes.filter(graph_type=graph_type).all() + GenericGeoNode.nodes.filter(graph_type=graph_type).all()
        
        # Initialize accumulators for each change type
        graph_embedding_added = None
        graph_embedding_deleted = None
        graph_embedding_msc = None
        graph_embedding_modified = None
        
        count_added = 0
        count_deleted = 0
        count_msc = 0
        count_modified = 0
        
        for node in nodes:
            if not hasattr(node, 'graphsage_embedding'):
                continue
                
            embedding = getattr(node, 'graphsage_embedding')
            change_type = getattr(node, 'change_type', None)
            
            # MSC nodes
            if change_type == 'msc':
                if graph_embedding_msc is None:
                    graph_embedding_msc = embedding.copy()
                else:
                    graph_embedding_msc = list(map(add, graph_embedding_msc, embedding))
                count_msc += 1
            
            # Added nodes
            elif change_type == 'added':
                if graph_embedding_added is None:
                    graph_embedding_added = embedding.copy()
                else:
                    graph_embedding_added = list(map(add, graph_embedding_added, embedding))
                count_added += 1
            
            # Deleted nodes
            elif change_type == 'ctdeleted':
                if graph_embedding_deleted is None:
                    graph_embedding_deleted = embedding.copy()
                else:
                    graph_embedding_deleted = list(map(add, graph_embedding_deleted, embedding))
                count_deleted += 1
            
            # Modified nodes
            elif change_type == 'modified':
                if graph_embedding_modified is None:
                    graph_embedding_modified = embedding.copy()
                else:
                    graph_embedding_modified = list(map(add, graph_embedding_modified, embedding))
                count_modified += 1
                
        if graph_embedding_modified is None and graph_embedding_added is None and graph_embedding_deleted is None:
            return "No changes"
        
        #####
        if graph_embedding_added is None:
            if graph_embedding_deleted is None:
                graph_embedding_all_changes = graph_embedding_modified
            elif graph_embedding_modified is None:
                graph_embedding_all_changes = graph_embedding_deleted
            else:
                 graph_embedding_all_changes = list(map(add, graph_embedding_deleted, graph_embedding_modified))
        elif graph_embedding_deleted is None:
            if graph_embedding_added is None:
                graph_embedding_all_changes = graph_embedding_modified
            elif graph_embedding_modified is None:
                graph_embedding_all_changes = graph_embedding_added
            else:
                graph_embedding_all_changes = list(map(add, graph_embedding_added, graph_embedding_modified))
        elif graph_embedding_modified is None:
            if graph_embedding_added is None:
                graph_embedding_all_changes = graph_embedding_deleted
            if graph_embedding_deleted is None:
                graph_embedding_all_changes = graph_embedding_added
            else:
                graph_embedding_all_changes = list(map(add, graph_embedding_added, graph_embedding_deleted))
        else:
            i = list(map(add, graph_embedding_added, graph_embedding_deleted))
            graph_embedding_all_changes = list(map(add, i, graph_embedding_modified))
            
        ####   
        count_all_changes = count_added + count_deleted + count_modified
        if graph_embedding_all_changes and count_all_changes > 0:
            graph_embedding_all_changes = [x / count_all_changes for x in graph_embedding_all_changes]
        else:
            graph_embedding_all_changes = None
        
        # Calculate means by dividing by counts
        if graph_embedding_added and count_added > 0:
            graph_embedding_added = [x / count_added for x in graph_embedding_added]
        else:
            graph_embedding_added = None
            
        if graph_embedding_deleted and count_deleted > 0:
            graph_embedding_deleted = [x / count_deleted for x in graph_embedding_deleted]
        else:
            graph_embedding_deleted = None
            
        if graph_embedding_msc and count_msc > 0:
            graph_embedding_msc = [x / count_msc for x in graph_embedding_msc]
        else:
            graph_embedding_msc = None
            
        if graph_embedding_modified and count_modified > 0:
            graph_embedding_modified = [x / count_modified for x in graph_embedding_modified]
        else:
            graph_embedding_modified = None
        
        # Create complete graph embedding (concatenate all change types)
        embeddings_complete = []
        for emb in [graph_embedding_added, graph_embedding_deleted, graph_embedding_modified, graph_embedding_msc]:
            if emb is not None:
                embeddings_complete.extend(emb)
            else:
                # Pad with zeros if change type doesn't exist
                embeddings_complete.extend([0.0] * 128)  # assuming embedding dimension is 128
        
        count_total = count_added + count_deleted + count_modified + count_msc


        
        graph_embeddings_mean_statistic = {
            "Complete Graph": {
                "embedding": embeddings_complete,
                "node_count": count_total
            },
            "Graph Added": {
                "embedding": graph_embedding_added,
                "node_count": count_added
            },
            "Graph Deleted": {
                "embedding": graph_embedding_deleted,
                "node_count": count_deleted
            },
            "Graph MSC": {
                "embedding": graph_embedding_msc,
                "node_count": count_msc
            },
            "Graph Modified": {
                "embedding": graph_embedding_modified,
                "node_count": count_modified
            },
            "All changes": {
                "embedding": graph_embedding_all_changes,
                "node count": count_all_changes
            }
        }
        
        return graph_embeddings_mean_statistic
    
graph_calc = GraphEmbeddingCalculator()

full_result = {}


complete_embedding_move_wall = []
complete_embedding_change_size_wall= []
complete_embedding_add_c = []
complete_embedding_move_c= []
complete_embedding_change_w_t = []



graph_type_list = ['move_wall',
'change_size_wall',
'add_column',
'move_column',
'change_wall_type']
for i,graph_type in enumerate(graph_type_list):
    stats = graph_calc.calculate_mean_graph_embedding(graph_type)
    
    print(f"\n{graph_type}:")
    #print(f"  Total nodes: {stats['Complete Graph']['node_count']}")
    #print(f"  Total embedding: {stats['Complete Graph']['embedding']}")
    #print(f"  Added: {stats['Graph Added']['node_count']}")
    #print(f"  Added: {stats['Graph Added']['embedding']}")
    #print(f"  Deleted: {stats['Graph Deleted']['node_count']}")
    #print(f"  Deleted: {stats['Graph Deleted']['embedding']}")
    #print(f"  Modified: {stats['Graph Modified']['node_count']}")
    #print(f"  Modified: {stats['Graph Modified']['embedding']}")
    #print(f"  MSC: {stats['Graph MSC']['node_count']}")
    #print(f"  MSC: {stats['Graph MSC']['embedding']}")
    #print(f"  Complete embedding dimension: {len(stats['Complete Graph']['embedding'])}")

    if graph_type == "move_wall":
        complete_embedding_move_wall = stats['All changes']['embedding']
    if graph_type == "change_size_wall":
        complete_embedding_change_size_wall= stats['All changes']['embedding']
    if graph_type == "move_column":
        complete_embedding_move_c = stats['All changes']['embedding']
    if graph_type == "add_column":
        complete_embedding_add_c= stats['All changes']['embedding']
    if graph_type == "change_wall_type":
        complete_embedding_change_w_t= stats['All changes']['embedding']
   

    full_result[graph_type] = stats


from scipy.spatial.distance import cosine




similarity = 1 - cosine(complete_embedding_move_wall, complete_embedding_change_size_wall)
similarity_1 = 1 - cosine(complete_embedding_move_wall, complete_embedding_add_c)
similarity_2 = 1 - cosine(complete_embedding_move_wall, complete_embedding_move_c)
similarity_3 = 1 - cosine(complete_embedding_move_wall, complete_embedding_change_w_t)

similarity_4 = 1 - cosine(complete_embedding_change_size_wall, complete_embedding_add_c)
similarity_5 = 1 - cosine(complete_embedding_change_size_wall, complete_embedding_move_c )
similarity_6 = 1 - cosine(complete_embedding_change_size_wall, complete_embedding_change_w_t)

similarity_7 = 1 - cosine(complete_embedding_add_c, complete_embedding_move_c)
similarity_8 = 1 - cosine(complete_embedding_add_c, complete_embedding_change_w_t)

similarity_9 = 1 - cosine(complete_embedding_move_c, complete_embedding_change_w_t)



#print(f"Similarity between rotated and translated: {similarity}")

print("Similarity Move wall- Size wall")
print(similarity)

print("Similarity Move wall- add Column")
print(similarity_1)

print("Similarity Move wall - move column")
print(similarity_2)

print("Similarity Move wall - change wall type")
print(similarity_3)

print("Similarity size wall- add column")
print(similarity_4)
###
print("Similarity Size wall - Move Column")
print(similarity_5)

print("Similarity Size wall- change Type wall")
print(similarity_6)

print("Similarity add column - move column")
print(similarity_7)

print("Similarity add column - wall type")
print(similarity_8)
###

print("Similarity move column- wall typet")
print(similarity_9)

