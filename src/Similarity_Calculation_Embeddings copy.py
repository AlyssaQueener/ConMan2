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

        if graph_embedding_added is None:
            if graph_embedding_deleted is None:
                graph_embedding_all_changes = graph_embedding_modified
            else:
                 graph_embedding_all_changes = list(map(add, graph_embedding_deleted, graph_embedding_modified))
        elif graph_embedding_deleted is None:
            graph_embedding_all_changes = list(map(add, graph_embedding_added, graph_embedding_modified))
        else:
            i = list(map(add, graph_embedding_added, graph_embedding_deleted))
            graph_embedding_all_changes = list(map(add, i, graph_embedding_modified))
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
   

modified = PrimaryNode.nodes.filter(encoded_modified=1.0)

for m in modified:
    print(f"Node: {m.EntityType} - change type: {m.change_type}")
    similar_nodes = m.similar_to.all()
    for s in similar_nodes:
        print(f"   similar: {s.EntityType} changetype: {s.change_type}")
        if s.geo_modification == 1.0 and m.geo_modification == 1.0:
            geo_nodes_s = s.relation_geo.all()
            geo_nodes_m = m.relation_geo.all()
            for n in geo_nodes_s:
                if n.change_type == "modified":
                    print(n)
        
from collections import Counter

all_nodes = PrimaryNode.nodes.all()
dist = Counter(n.change_type for n in all_nodes)
print(dist)

total = 611 + 143 + 140 + 66  # = 960
baselines = {
    'msc':       611 / total,  # 0.636
    'modified':  143 / total,  # 0.149
    'added':     140 / total,  # 0.146
    'ctdeleted':  66 / total,  # 0.069
}
print("Random baselines:")
for ct, b in baselines.items():
    print(f"  {ct}: {b:.3f}")
    
from collections import defaultdict

all_nodes = PrimaryNode.nodes.all()
results = defaultdict(list)

for node in all_nodes:
    if not node.change_type:
        continue
    similar = node.similar_to.all()
    if not similar:
        continue
    matches = sum(1 for s in similar if s.change_type == node.change_type)
    results[node.change_type].append(matches / len(similar))

print(f"{'type':<12} {'recall@3':>10} {'baseline':>10} {'lift':>10} {'n':>6}")
for ct, recalls in results.items():
    mean = sum(recalls) / len(recalls)
    base = baselines[ct]
    lift = mean / base
    print(f"{ct:<12} {mean:>10.3f} {base:>10.3f} {lift:>10.2f}x {len(recalls):>6}")
        
