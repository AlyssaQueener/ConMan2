
from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import *
from llama_index.embeddings.ollama import OllamaEmbedding

class KNN:
    db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
    
    def run_knn(self):
        print("########## Running KNN ##########")
        train_query = """
        CALL gds.knn.stream('knn', {
            topK: 10,
            nodeProperties: ['graphsage_embedding'],
            randomSeed: 42,
            concurrency: 1,
            sampleRate: 1.0,
            deltaThreshold: 0.0
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).entity_type AS node1Type,
        gds.util.asNode(node2).entity_type AS node2Type,
        similarity
        ORDER BY similarity DESC
        LIMIT 50
        """
        result, meta = self.db.cypher_query(train_query)
        print(result)
        return result
    
    def run_knn_filtered(self):
        print("########## Running KNN ##########")
        train_query = """
        CALL gds.knn.filtered.stream('knn_no_entity', {
            nodeLabels: ['PrimaryNode'],
            topK: 15,
            nodeProperties: {
                graphsage_embedding_no_entity: 'COSINE'
            },
            randomSeed: 42,
            concurrency: 1,
            sampleRate: 1.0,
            deltaThreshold: 0.0
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).EntityType AS node1Type,
        gds.util.asNode(node2).EntityType AS node2Type,
        similarity
        ORDER BY similarity DESC
        LIMIT 50
        """
        result, meta = self.db.cypher_query(train_query)
        print(result)
        return result
    
    def run_cluster_stream(self):
        stream_query = """
        CALL gds.kmeans.stream('knn', {
        nodeProperty: 'graphsage_embedding',
        k: 5,
        randomSeed: 42
        })
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).EntityType AS name, gds.util.asNode(nodeId).change_type AS change, communityId
        ORDER BY communityId, name, change ASC
        """
        result, meta = self.db.cypher_query(stream_query)
        print(result)
        return result
    
    def run_cluster_stream_one_hot(self):
        stream_query = """
        CALL gds.kmeans.stream('knn_one_hot', {
        nodeProperty: 'graphsage_embedding_one_hot',
        k: 15,
        randomSeed: 42
        })
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).EntityType AS name, gds.util.asNode(nodeId).change_type AS change, communityId
        ORDER BY communityId, name, change ASC
        """
        result, meta = self.db.cypher_query(stream_query)
        print(result)
        return result
    
    def run_cluster_stream_no_entity(self):
        stream_query = """
        CALL gds.kmeans.stream('knn_no_entity', {
        nodeProperty: 'graphsage_embedding_no_entity',
        k: 10,
        randomSeed: 42
        })
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).EntityType AS name, gds.util.asNode(nodeId).change_type AS change, communityId
        ORDER BY communityId, name, change ASC
        """
        result, meta = self.db.cypher_query(stream_query)
        print(result)
        return result
    
    def run_cluster_mutate(self):
        train_query = """
        CALL gds.kmeans.mutate('knn', {
            nodeProperty: 'graphsage_embedding',
            k: 5,
            randomSeed: 42,
            mutateProperty: 'kmeans'
        })
        YIELD communityDistribution
        """
        result, meta = self.db.cypher_query(train_query)
        print(result)
        return result
    
    def run_cluster_mutate_no_entity(self):
        train_query = """
        CALL gds.kmeans.mutate('knn_no_entity', {
            nodeProperty: 'graphsage_embedding_no_entity',
            k: 6,
            randomSeed: 42,
            mutateProperty: 'kmeans_no_entity'
        })
        YIELD communityDistribution
        """
        result, meta = self.db.cypher_query(train_query)
        print(result)
        return result
    
    def run_cluster_write_one_hot(self):
        query = """
        CALL gds.kmeans.write('knn_one_hot', {
        nodeProperty: 'graphsage_embedding_one_hot',
        k: 15,
        randomSeed: 42,
        writeProperty: 'kmeans_one_hot_new'
        })
        YIELD nodePropertiesWritten
        """
        result, meta = self.db.cypher_query(query)
        print(result)
        return result
    
    def run_cluster_write_no_entity(self):
        query = """
        CALL gds.kmeans.write('knn_no_entity', {
        nodeProperty: 'graphsage_embedding_no_entity',
        k: 10,
        randomSeed: 42,
        writeProperty: 'kmeans_no_entity_new'
        })
        YIELD nodePropertiesWritten
        """
        result, meta = self.db.cypher_query(query)
        print(result)
        return result
    
    def write_similarity(self):
        """
        Generate GraphSAGE embeddings and write them back to nodes
        """
    
        print("########## Write similar rel ##########")
        write_query = """
        CALL gds.knn.write('knn_no_entity', {
            topK: 15,
            nodeProperties: ['graphsage_embedding_no_entity'],
            writeRelationshipType: 'SIMILAR',
            writeProperty: 'score',
            randomSeed: 42,
            concurrency: 1,
            sampleRate: 1.0,
            deltaThreshold: 0.0
        })
        YIELD nodesCompared, relationshipsWritten, similarityDistribution
        RETURN nodesCompared, relationshipsWritten, similarityDistribution.mean AS meanSimilarity
        """
    
        result, meta = self.db.cypher_query(write_query)
        print(result)
    
        return result
    
            
    
    def projection_query_knn(self):
        query = """
        CALL gds.graph.project(
            'knn',
            {
                
                PrimaryNode: { properties: [
                    'graphsage_embedding'
                    ]
                }
            },
            ['*']
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    
    def projection_query_knn_one_hot(self):
        query = """
        CALL gds.graph.project(
            'knn_one_hot',
            {
                
                PrimaryNode: { properties: [
                    'graphsage_embedding_one_hot'
                    ]
                }
            },
            ['*']
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    def projection_query_for_certain_graph_types(self):
        query = """
        CALL gds.graph.project.cypher(
            'knn_no_entity',
            'MATCH (n:PrimaryNode) 
            WHERE n.graph_type IN $allowed_types 
            RETURN id(n) AS id, labels(n) AS labels, 
            n.graphsage_embedding_no_entity AS graphsage_embedding_no_entity',
            MATCH (a)-[r]->(b) RETURN id(a) AS source, id(b) AS target, type(r) AS type',
            {parameters: {allowed_types: ["tc", "rotation", "translation", "size", 
                                   "rotation-2", "size-2", "room-size", "translation-2",
                                   "v1-v2-test", "v2-v3-test", "v3-v4-test"]}
                                   }
            )
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    def projection_query_knn_no_entity(self):
        query = """
        CALL gds.graph.project(
            'knn_no_entity',
            {
                
                PrimaryNode: { properties: [
                    'graphsage_embedding_no_entity'
                    ]
                }
            },
            ['*']
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    def drop_projection(self, graph_name):
        print("########## Cleaning up existing projection ##########")
        drop_query = f"""
            CALL gds.graph.exists('{graph_name}')
            YIELD exists
            WITH exists
            WHERE exists
            CALL gds.graph.drop('knn_no_entity')
            YIELD graphName
            RETURN graphName
        """
        try:
            result, meta = self.db.cypher_query(drop_query)
            if result:
                print(f"Dropped existing graph: {result[0][0]}")
        except Exception as e:
            print(f"No existing graph to drop: {e}")
            
    
    
    
    







