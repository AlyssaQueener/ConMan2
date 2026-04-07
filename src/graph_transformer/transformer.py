from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import *
from llama_index.embeddings.ollama import OllamaEmbedding

class Transformer:
    db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
    ollama_embedding = OllamaEmbedding(
        model_name="nomic-embed-text",
        base_url="http://localhost:11434",
        # Can optionally pass additional kwargs to ollama
        # ollama_additional_kwargs={"mirostat": 0},
    )
    def merge_msc_nodes(self, timestamp_init, graph_type):
        print ("###### MSC ###########")
        msc = Node.nodes.filter(timestamp=timestamp_init, graph_type=graph_type).has(equivalent_to=True).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_init, graph_type=graph_type).has(equivalent_to=True).all() 
        for node in msc:
            equvivalent = node.equivalent_to.single()
            #print(node)
            #print("is equvivalent to")
            #print(equvivalent)
            node.equivalent_to.disconnect(equvivalent)
            # Don't disconnect first - let APOC handle it via mergeRels:true
            query = """
            MATCH (n1), (n2)
            WHERE elementId(n1) = $node1_id AND elementId(n2) = $node2_id
            WITH head(collect([n1,n2])) as nodes
            CALL apoc.refactor.mergeNodes(nodes,{properties:"discard", mergeRels:true})
            YIELD node
            SET node.timestamp = "msc"
            RETURN count(*)
            """
            result, meta = self.db.cypher_query(query, {
                'node1_id': node.element_id,
                'node2_id': equvivalent.element_id
            })
            
    
            #print(f"Merged {node.EntityType} with {equvivalent.EntityType}")

        msc_2 = Node.nodes.filter(timestamp="msc", graph_type=graph_type).all() + GenericGeoNode.nodes.filter(timestamp="msc", graph_type=graph_type).all()
        for node in msc_2:
            if hasattr(node, "change_type"):
                setattr(node, 'encoded_msc', 0.0)  
                setattr(node, 'encoded_modified', 1.0) 
                setattr(node, 'encoded_deleted', 0.0)       
                setattr(node, 'encoded_added', 0.0) 
            else:
                setattr(node, "change_type", "msc")
                setattr(node, 'encoded_msc', 1.0)  
                setattr(node, 'encoded_modified', 0.0) 
                setattr(node, 'encoded_deleted', 0.0)       
                setattr(node, 'encoded_added', 0.0)
                
            #print(node)
            node.save()
        self.db.cypher_query("MATCH ()-[r:EQUIVALENT_TO]->() DELETE r")

    def edit_pushout_nodes(self, timestamp_init, timestamp_updt, graph_type):
        print("######## Pushout init ############")
        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        for node in pushout_nodes_init:
            setattr(node, 'encoded_msc', 0.0)  
            setattr(node, 'encoded_modified', 0.0) 
            setattr(node, 'encoded_deleted', 1.0)       
            setattr(node, 'encoded_added', 0.0)
            setattr(node, "change_type", "ctdeleted")
            node.save()
        #print(pushout_nodes_init)
        print("######## Pushout updated ############")
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()
        for node in pushout_nodes_updt:
            setattr(node, 'encoded_msc', 0.0)  
            setattr(node, 'encoded_modified', 0.0) 
            setattr(node, 'encoded_deleted', 0.0)       
            setattr(node, 'encoded_added', 1.0)
            setattr(node, "change_type", "added")
            node.save()
        #print(pushout_nodes_updt)
    def create_change_graph(self, timestamp_init, timestamp_updt, graph_type):
        print('############### Apply semantic changes ###########')
        self.edit_pushout_nodes(timestamp_init, timestamp_updt, graph_type)
        self.merge_msc_nodes(timestamp_init, graph_type)

    def deletedScondaryAndInlineNodes(self):
        query = """
            MATCH (n)
            WHERE n:InlineNode OR n:SecondaryNode
            DETACH DELETE n
            
            """
        self.db.cypher_query(query)
    def embed_text(self, text):
        embedding = self.ollama_embedding.get_text_embedding(text)
        return list(embedding)
    
    def prepare_text(self, node):
        text_parts = []
        if hasattr(node, "EntityType"):
            text_parts.append(getattr(node, "EntityType"))
        if hasattr(node, "change_type"):
            change_type = getattr(node, "change_type")
            if change_type == "modified":
                text_parts.append(f"Change: {change_type}")
                if hasattr(node, "changed_value"):
                    text_parts.append(f"Changed value:{getattr(node, "changed_value")}")
                if hasattr(node, "old_value"):
                    text_parts.append(f"From:{getattr(node, "old_value")}")
                if hasattr(node, "new_value"):
                    text_parts.append(f"To:{getattr(node, "new_value")}")
            elif change_type == "msc":
                text_parts.append("Change: no change")
            else:
                text_parts.append(f"Change: {change_type}")
        attribute_string = " ".join(text_parts)
        print(attribute_string)
        return attribute_string
                    
    
    def create_text_embeddings_for_nodes(self,graph_type):
        nodes = Node.nodes.filter(graph_type=graph_type).all()
        processed = 0
        for node in nodes:
            attribute_string = self.prepare_text(node)
            embedding = self.embed_text(attribute_string)
            setattr(node, "text_embedding", embedding)
            node.save()
            processed += 1
        print(f"Processed nodes: {processed}")


    def train_graph(self, model_name='geometric-change-interpreter'):
        print("########## Training GraphSAGE ##########")
        train_query = """
        CALL gds.beta.graphSage.train(
            'test',
            {
                modelName: $model_name,
                featureProperties: [
                    'entity_type_index', 'encoded_change_type', 'delta_materials',
                    'volume',
                    'delta_volume',
                    'depth',
                    'delta_depth',
                    'width',
                    'delta_width',
                    'area',
                    'delta_area',
                    'length',
                    'delta_length',
                    'total_surface_area',
                    'delta_total_surface_area',
                    'height',
                    'delta_height',
                    'bb_min_x',
                    'delta_bb_min_x',
                    'bb_min_y',
                    'delta_bb_min_y',
                    'bb_min_z',
                    'delta_bb_min_z',
                    'bb_max_x',
                    'delta_bb_max_x',
                    'bb_max_y',
                    'delta_bb_max_y',
                    'bb_max_z',
                    'delta_bb_max_z'
                ],
                projectedFeatureDimension: 31,
                aggregator: 'mean',
                activationFunction: 'relu',
                sampleSizes: [25, 10],
                learningRate: 0.01,
                tolerance: 0.0001,
                epochs: 50,
                embeddingDimension: 128,
                randomSeed: 42
            }
        )
        YIELD modelInfo, trainMillis
        RETURN modelInfo, trainMillis
        """
        result, meta = self.db.cypher_query(train_query, {'model_name': model_name})
        print(f"Training completed in {result[0][1]}ms")
        print(f"Model info: {result[0][0]}")
        return result
    
    def generate_graphsage_embeddings(self, model_name='geometric-change-interpreter'):
        """
        Generate GraphSAGE embeddings and write them back to nodes
        """
    
        print("########## Generating GraphSAGE Embeddings ##########")
        write_query = """
        CALL gds.beta.graphSage.write(
            'test',
            {
                modelName: $model_name,
                writeProperty: 'graphsage_embedding'
            }
        )
        YIELD nodePropertiesWritten, computeMillis
        RETURN nodePropertiesWritten, computeMillis
        """
    
        result, meta = self.db.cypher_query(write_query, {'model_name': model_name})
        print(f"Updated {result[0][0]} nodes with GraphSAGE embeddings in {result[0][1]}ms")
    
        return result
    
    def generate_graphsage_embeddings_one_hot(self, model_name='one_hot'):
        """
        Generate GraphSAGE embeddings and write them back to nodes
        """
    
        print("########## Generating GraphSAGE Embeddings ##########")
        write_query = """
        CALL gds.beta.graphSage.write(
            'one_hot',
            {
                modelName: $model_name,
                writeProperty: 'graphsage_embedding_one_hot'
            }
        )
        YIELD nodePropertiesWritten, computeMillis
        RETURN nodePropertiesWritten, computeMillis
        """
    
        result, meta = self.db.cypher_query(write_query, {'model_name': model_name})
        print(f"Updated {result[0][0]} nodes with GraphSAGE embeddings in {result[0][1]}ms")
    
        return result
    
    def generate_graphsage_embeddings_no_entity(self, model_name='no_entity'):
        """
        Generate GraphSAGE embeddings and write them back to nodes
        """
    
        print("########## Generating GraphSAGE Embeddings ##########")
        write_query = """
        CALL gds.beta.graphSage.write(
            'no_entity',
            {
                modelName: $model_name,
                writeProperty: 'graphsage_embedding_no_entity'
            }
        )
        YIELD nodePropertiesWritten, computeMillis
        RETURN nodePropertiesWritten, computeMillis
        """
    
        result, meta = self.db.cypher_query(write_query, {'model_name': model_name})
        print(f"Updated {result[0][0]} nodes with GraphSAGE embeddings in {result[0][1]}ms")
    
        return result
    
    def drop_model(self,model_name='geometric-change-interpreter'):
        drop_query = """
        CALL gds.model.exists($model_name)
        YIELD exists
        WITH exists
        WHERE exists
        CALL gds.model.drop($model_name)
        YIELD modelName
        RETURN modelName
        """
        try:
            result, meta = self.db.cypher_query(drop_query, {'model_name': model_name})
            if result:
                print(f"Dropped existing model: {result[0][0]}")
        except Exception as e:
            print(f"No existing model to drop: {e}")
            
    
    def projection_query_1(self):
        query = """
        CALL gds.graph.project(
            'test',
            {
                
                PrimaryNode: { properties: [
                    'entity_type_index',
                    'delta_materials',
                    'encoded_change_type'
                    ]
                },
                ConnectionNode: { properties:
                    ['entity_type_index',
                    'encoded_change_type']
                },
                SolidNode: { properties:
                    [
                        'encoded_change_type',
                        'volume',
                        'delta_volume',
                        'depth',
                        'delta_depth',
                        'width',
                        'delta_width',
                        'area',
                        'delta_area',
                        'length',
                        'delta_length'
                    ]
                },
                BrepNode: { properties:
                    [
                        'encoded_change_type',
                        'total_surface_area',
                        'delta_total_surface_area',
                        'width',
                        'delta_width',
                        'height',
                        'delta_height',
                        'volume',
                        'delta_volume',
                        'length',
                        'delta_length'
                    ]
                },
                LocationNode: { properties:
                    [
                        'encoded_change_type',
                        'bb_min_x',
                        'delta_bb_min_x',
                        'bb_min_y',
                        'delta_bb_min_y',
                        'bb_min_z',
                        'delta_bb_min_z',
                        'bb_max_x',
                        'delta_bb_max_x',
                        'bb_max_y',
                        'delta_bb_max_y',
                        'bb_max_z',
                        'delta_bb_max_z'
                        
                    ]
                },
                SurfaceNode: { properties:
                    [
                        'encoded_change_type',
                        'width',
                        'delta_width',
                        'area',
                        'delta_area',
                        'length',
                        'delta_length'
                        
                    ]
                }

            },
            {
                RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'},
                GEO_RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'}
            }
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
            CALL gds.graph.drop('{graph_name}')
            YIELD graphName
            RETURN graphName
        """
        try:
            result, meta = self.db.cypher_query(drop_query)
            if result:
                print(f"Dropped existing graph: {result[0][0]}")
        except Exception as e:
            print(f"No existing graph to drop: {e}")
            
    def train_graph_delta(self, model_name='geometric-change-interpreter'):
        print("########## Training GraphSAGE ##########")
        train_query = """
        CALL gds.beta.graphSage.train(
            'test',
            {
                modelName: $model_name,
                featureProperties: [
                    'entity_type_index', 
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted',
                    'delta_materials',
                    'delta_volume',
                    'delta_depth',
                    'delta_width',
                    'delta_area',
                    'delta_compactness',
                    'delta_length',
                    'delta_max_face_area',
                    'delta_min_face_area',
                    'delta_n_faces',
                    'delta_height',
                    'delta_bb_min_x',
                    'delta_bb_min_y',
                    'delta_bb_min_z',
                    'delta_bb_max_x',
                    'delta_bb_max_y',
                    'delta_bb_max_z'
                ],
                projectedFeatureDimension: 22,
                aggregator: 'pool',
                activationFunction: 'relu',
                sampleSizes: [25, 10],
                learningRate: 0.001,
                tolerance: 0.0001,
                epochs: 20,
                embeddingDimension: 64,
                randomSeed: 42
            }
        )
        YIELD modelInfo, trainMillis
        RETURN modelInfo, trainMillis
        """
        result, meta = self.db.cypher_query(train_query, {'model_name': model_name})
        print(f"Training completed in {result[0][1]}ms")
        print(f"Model info: {result[0][0]}")
        return result
    
    def train_graph_delta_one_hot(self, model_name='one_hot'):
        print("########## Training GraphSAGE ##########")
        train_query = """
        CALL gds.beta.graphSage.train(
            'one_hot',
            {
                modelName: $model_name,
                featureProperties: [
                    'one_hot_entity', 
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted',
                    'delta_materials',
                    'delta_volume',
                    'delta_depth',
                    'delta_width',
                    'delta_area',
                    'delta_compactness',
                    'delta_length',
                    'delta_max_face_area',
                    'delta_min_face_area',
                    'delta_n_faces',
                    'delta_height',
                    'delta_bb_min_x',
                    'delta_bb_min_y',
                    'delta_bb_min_z',
                    'delta_bb_max_x',
                    'delta_bb_max_y',
                    'delta_bb_max_z'
                ],
                projectedFeatureDimension: 440,
                aggregator: 'pool',
                activationFunction: 'relu',
                sampleSizes: [25, 10],
                learningRate: 0.001,
                tolerance: 0.0001,
                epochs: 20,
                embeddingDimension: 64,
                randomSeed: 42
            }
        )
        YIELD modelInfo, trainMillis
        RETURN modelInfo, trainMillis
        """
        result, meta = self.db.cypher_query(train_query, {'model_name': model_name})
        print(f"Training completed in {result[0][1]}ms")
        print(f"Model info: {result[0][0]}")
        return result
    
    def train_graph_delta_n_entities(self, model_name='no_entity'):
        print("########## Training GraphSAGE ##########")
        train_query = """
        CALL gds.beta.graphSage.train(
            'no_entity',
            {
                modelName: $model_name,
                featureProperties: [
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted', 
                    'delta_materials',
                    'delta_volume',
                    'delta_depth',
                    'delta_width',
                    'delta_area',
                    'delta_compactness',
                    'delta_length',
                    'delta_max_face_area',
                    'delta_min_face_area',
                    'delta_n_faces',
                    'delta_height',
                    'delta_bb_min_x',
                    'delta_bb_min_y',
                    'delta_bb_min_z',
                    'delta_bb_max_x',
                    'delta_bb_max_y',
                    'delta_bb_max_z'
                ],
                projectedFeatureDimension: 21,
                aggregator: 'pool',
                activationFunction: 'relu',
                sampleSizes: [25, 10],
                learningRate: 0.001,
                tolerance: 0.0001,
                epochs: 20,
                embeddingDimension: 64,
                randomSeed: 42
            }
        )
        YIELD modelInfo, trainMillis
        RETURN modelInfo, trainMillis
        """
        result, meta = self.db.cypher_query(train_query, {'model_name': model_name})
        print(f"Training completed in {result[0][1]}ms")
        print(f"Model info: {result[0][0]}")
        return result
            
    def projection_query_delta(self):
        query = """
        CALL gds.graph.project(
            'test',
            {
                
                PrimaryNode: { properties: [
                    'entity_type_index',
                    'delta_materials',
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted'
                    ]
                },
                ConnectionNode: { properties:
                    ['entity_type_index',
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted']
                },
                SolidNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_volume',
                        'delta_depth',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                    ]
                },
                BrepNode: { properties:
                    [
                        'delta_max_face_area',
                        'delta_min_face_area',
                        'delta_n_faces',
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_height',
                        'delta_volume',
                        'delta_length'
                    ]
                },
                LocationNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_bb_min_x',
                        'delta_bb_min_y',
                        'delta_bb_min_z',
                        'delta_bb_max_x',
                        'delta_bb_max_y',
                        'delta_bb_max_z'
                        
                    ]
                },
                SurfaceNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                        
                    ]
                }

            },
            {
                RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'},
                GEO_RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'}
            }
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    def projection_query_delta_one_hot(self):
        query = """
        CALL gds.graph.project(
            'one_hot',
            {
                
                PrimaryNode: { properties: [
                    'one_hot_entity',
                    'delta_materials',
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted'
                    ]
                },
                ConnectionNode: { properties:
                    ['one_hot_entity',
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted']
                },
                SolidNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_volume',
                        'delta_depth',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                    ]
                },
                BrepNode: { properties:
                    [
                        'delta_max_face_area',
                        'delta_min_face_area',
                        'delta_n_faces',
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_height',
                        'delta_volume',
                        'delta_length'
                    ]
                },
                LocationNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_bb_min_x',
                        'delta_bb_min_y',
                        'delta_bb_min_z',
                        'delta_bb_max_x',
                        'delta_bb_max_y',
                        'delta_bb_max_z'
                        
                    ]
                },
                SurfaceNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                        
                    ]
                }

            },
            {
                RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'},
                GEO_RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'}
            }
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][2]}, Relationships: {result[0][3]}")
        return result
    
    def projection_query_delta_w_entity(self):
        query = """
        CALL gds.graph.project(
            'no_entity',
            {
                
                PrimaryNode: { properties: [
                    'delta_materials',
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted'
                    ]
                },
                ConnectionNode: { properties:
                    [
                    'encoded_msc',
                    'encoded_modified',
                    'encoded_added',
                    'encoded_deleted'
                    ]
                },
                SolidNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_volume',
                        'delta_depth',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                    ]
                },
                BrepNode: { properties:
                    [
                        'delta_max_face_area',
                        'delta_min_face_area',
                        'delta_n_faces',
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_height',
                        'delta_volume',
                        'delta_length'
                    ]
                },
                LocationNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_bb_min_x',
                        'delta_bb_min_y',
                        'delta_bb_min_z',
                        'delta_bb_max_x',
                        'delta_bb_max_y',
                        'delta_bb_max_z'
                        
                    ]
                },
                SurfaceNode: { properties:
                    [
                        'encoded_msc',
                        'encoded_modified',
                        'encoded_added',
                        'encoded_deleted',
                        'delta_width',
                        'delta_area',
                        'delta_length',
                        'delta_compactness'
                        
                    ]
                }

            },
            {
                RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'},
                GEO_RELATION_TO: {orientation: 'UNDIRECTED', aggregation: 'SINGLE'}
            }
        )
        YIELD
            graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
        RETURN graphName, nodeProjection.SolidNode AS bookProjection, nodes, rels
        """
        result, meta = self.db.cypher_query(query)
        return result
    
        
    
    
    
    







