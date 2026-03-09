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
        msc = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all() 
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

        msc_2 = Node.nodes.filter(timestamp="msc").all() + GenericGeoNode.nodes.filter(timestamp="msc").all()
        for node in msc_2:
            if hasattr(node, "change_type"): 
                setattr(node, "graph_type", graph_type)
                setattr(node, "unmodified", 0.0)
                setattr(node, "modified", 1.0)
                setattr(node, "ctdeleted", 0.0)
                setattr(node, "added", 0.0)
            else:
                setattr(node, "change_type", "msc")
                setattr(node, "unmodified", 1.0)
                setattr(node, "modified", 0.0)
                setattr(node, "ctdeleted", 0.0)
                setattr(node, "added", 0.0)
                
                setattr(node, "graph_type", graph_type)
            #print(node)
            node.save()
        self.db.cypher_query("MATCH ()-[r:EQUIVALENT_TO]->() DELETE r")

    def edit_pushout_nodes(self, timestamp_init, timestamp_updt, graph_type):
        print("######## Pushout init ############")
        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        for node in pushout_nodes_init:
            setattr(node, "change_type", "ctdeleted")
            setattr(node, "unmodified", 0.0)
            setattr(node, "modified", 0.0)
            setattr(node, "ctdeleted", 1.0)
            setattr(node, "added", 0.0)
            setattr(node, "graph_type", graph_type)
            node.save()
        #print(pushout_nodes_init)
        print("######## Pushout updated ############")
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()
        for node in pushout_nodes_updt:
            setattr(node, "change_type", "added")
            setattr(node, "unmodified", 0.0)
            setattr(node, "modified", 0.0)
            setattr(node, "ctdeleted", 0.0)
            setattr(node, "added", 1.0)
            setattr(node, "graph_type", graph_type)
            node.save()
        #print(pushout_nodes_updt)
    def create_change_graph(self, path_patch_semantic, timestamp_init, timestamp_updt, graph_type):
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

    def project_graph_for_change_interpretation(self, model_name='geometric-change-interpreter'):
        """
        Train GraphSAGE on all geometric transformation scenarios together
        """
    
        # Drop existing graph projection if it exists
        print("########## Cleaning up existing projection ##########")
        drop_query_1 = """
        CALL gds.graph.exists('test_minimal')
        YIELD exists
        WITH exists
        WHERE exists
        CALL gds.graph.drop('test_minimal')
        YIELD graphName
        RETURN graphName
        """
        try:
            result, meta = self.db.cypher_query(drop_query_1)
            if result:
             print(f"Dropped existing graph: {result[0][0]}")
        except Exception as e:
            print(f"No existing graph to drop: {e}")
        drop_query = """
        CALL gds.graph.exists('geometric_transformations')
        YIELD exists
        WITH exists
        WHERE exists
        CALL gds.graph.drop('geometric_transformations')
        YIELD graphName
        RETURN graphName
        """
        try:
            result, meta = self.db.cypher_query(drop_query)
            if result:
             print(f"Dropped existing graph: {result[0][0]}")
        except Exception as e:
            print(f"No existing graph to drop: {e}")
    
        print("########## Projecting Graph ##########")
        # Project all change graphs
        project_query = """
CALL gds.graph.project(
    'geometric_transformations',
    {
        PrimaryNode: {
            properties: {
                entity_type_index: {defaultValue: 0.0},
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0},
                delta_materials: {defaultValue: 0.0}
            }
        },
        ConnectionNode: {
            properties: {
                entity_type_index: {defaultValue: 0.0},
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0}
            }
        },
        SolidNode: {
            properties: {
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0},
                volume: {defaultValue: 0.0},
                delta_volume: {defaultValue: 0.0},
                bbox_x: {defaultValue: 0.0},
                delta_bbox_x: {defaultValue: 0.0},
                bbox_y: {defaultValue: 0.0},
                delta_bbox_y: {defaultValue: 0.0},
                area: {defaultValue: 0.0},
                delta_area: {defaultValue: 0.0},
                perimeter: {defaultValue: 0.0},
                delta_perimeter: {defaultValue: 0.0},
                num_vertices: {defaultValue: 0.0},
                delta_num_vertices: {defaultValue: 0.0},
                compactness: {defaultValue: 0.0},
                delta_compactness: {defaultValue: 0.0}
            }
        },
        BrepNode: {
            properties: {
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0},                
                total_surface_area: {defaultValue: 0.0},
                delta_total_surface_area: {defaultValue: 0.0},
                max_face_area: {defaultValue: 0.0},
                delta_max_face_area: {defaultValue: 0.0},
                min_face_area: {defaultValue: 0.0},
                delta_min_face_area: {defaultValue: 0.0},
                n_faces: {defaultValue: 0.0},
                delta_n_faces: {defaultValue: 0.0},
                n_vertices: {defaultValue: 0.0},
                delta_n_vertices: {defaultValue: 0.0}
            }
        },
        LocationNode: {
            properties: {
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0},
                bb_min_x: {defaultValue: 0.0},
                delta_bb_min_x: {defaultValue: 0.0},
                bb_min_y: {defaultValue: 0.0},
                delta_bb_min_y: {defaultValue: 0.0},
                bb_min_z: {defaultValue: 0.0},
                delta_bb_min_z: {defaultValue: 0.0},
                bb_max_x: {defaultValue: 0.0},
                delta_bb_max_x: {defaultValue: 0.0},
                bb_max_y: {defaultValue: 0.0},
                delta_bb_max_y: {defaultValue: 0.0},
                bb_max_z: {defaultValue: 0.0},
                delta_bb_max_z: {defaultValue: 0.0}
            }
        },
        SurfaceNode: {
            properties: {
                unmodified: {defaultValue: 0.0},
                modified: {defaultValue: 0.0},
                ctdeleted: {defaultValue: 0.0},
                added: {defaultValue: 0.0},
                bbox_x: {defaultValue: 0.0},
                delta_bbox_x: {defaultValue: 0.0},
                bbox_y: {defaultValue: 0.0},
                delta_bbox_y: {defaultValue: 0.0},
                area: {defaultValue: 0.0},
                delta_area: {defaultValue: 0.0},
                perimeter: {defaultValue: 0.0},
                delta_perimeter: {defaultValue: 0.0},
                num_vertices: {defaultValue: 0.0},
                delta_num_vertices: {defaultValue: 0.0},
                compactness: {defaultValue: 0.0},
                delta_compactness: {defaultValue: 0.0}
            }
        }
    },
    '*'
)
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
    
        result, meta = self.db.cypher_query(project_query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][1]}, Relationships: {result[0][2]}")
        return result
        
        
    def train_graph(self, model_name='geometric-change-interpreter'):
        print("########## Training GraphSAGE ##########")
        train_query = """
        CALL gds.beta.graphSage.train(
            'geometric_transformations',
            {
                modelName: $model_name,
                featureProperties: [
                    'entity_type_index', 'unmodified', 'modified', 'ctdeleted', 'added', 'delta_materials',
                    'volume', 'delta_volume',
                    'bbox_x', 'delta_bbox_x',
                    'bbox_y', 'delta_bbox_y',
                    'area', 'delta_area',
                    'perimeter', 'delta_perimeter',
                    'num_vertices', 'delta_num_vertices',
                    'compactness', 'delta_compactness',
                    'total_surface_area', 'delta_total_surface_area',
                    'max_face_area', 'delta_max_face_area',
                    'min_face_area', 'delta_min_face_area',
                    'n_faces', 'delta_n_faces',
                    'n_vertices', 'delta_n_vertices',
                    'bb_min_x', 'delta_bb_min_x',
                    'bb_min_y', 'delta_bb_min_y',
                    'bb_min_z', 'delta_bb_min_z',
                    'bb_max_x', 'delta_bb_max_x',
                    'bb_max_y', 'delta_bb_max_y',
                    'bb_max_z', 'delta_bb_max_z'
                ],
                projectedFeatureDimension: 19,
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
            'geometric_transformations',
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
            
    
    def easy_projection(self):
        print("########## Cleaning up existing projection ##########")
        drop_query = """
        CALL gds.graph.exists('test_minimal')
        YIELD exists
        WITH exists
        WHERE exists
        CALL gds.graph.drop('test_minimal')
        YIELD graphName
        RETURN graphName
        """
        try:
            result, meta = self.db.cypher_query(drop_query)
            if result:
             print(f"Dropped existing graph: {result[0][0]}")
        except Exception as e:
            print(f"No existing graph to drop: {e}")
    
        query = """
            CALL gds.graph.project(
    'test_minimal',
    {
        PrimaryNode: {
            properties: {
                entity_type_index: {defaultValue: 0.0},
                delta_materials: {defaultValue: 0.0}
            }
        },
        ConnectionNode: {
            properties: {
                entity_type_index: {defaultValue: 0.0}
            }
        },
        SolidNode: {
            properties: {
                volume: {defaultValue: 0.0},
                delta_volume: {defaultValue: 0.0},
                bbox_x: {defaultValue: 0.0},
                delta_bbox_x: {defaultValue: 0.0},
                bbox_y: {defaultValue: 0.0},
                delta_bbox_y: {defaultValue: 0.0},
                area: {defaultValue: 0.0},
                delta_area: {defaultValue: 0.0},
                perimeter: {defaultValue: 0.0},
                delta_perimeter: {defaultValue: 0.0},
                num_vertices: {defaultValue: 0.0},
                delta_num_vertices: {defaultValue: 0.0},
                compactness: {defaultValue: 0.0},
                delta_compactness: {defaultValue: 0.0}
            }
        },
        BrepNode: {
            properties: {
                total_surface_area: {defaultValue: 0.0},
                delta_total_surface_area: {defaultValue: 0.0},
                max_face_area: {defaultValue: 0.0},
                delta_max_face_area: {defaultValue: 0.0},
                min_face_area: {defaultValue: 0.0},
                delta_min_face_area: {defaultValue: 0.0},
                n_faces: {defaultValue: 0.0},
                delta_n_faces: {defaultValue: 0.0},
                n_vertices: {defaultValue: 0.0},
                delta_n_vertices: {defaultValue: 0.0}
            }
        },
        LocationNode: {
            properties: {
                bb_min_x: {defaultValue: 0.0},
                delta_bb_min_x: {defaultValue: 0.0},
                bb_min_y: {defaultValue: 0.0},
                delta_bb_min_y: {defaultValue: 0.0},
                bb_min_z: {defaultValue: 0.0},
                delta_bb_min_z: {defaultValue: 0.0},
                bb_max_x: {defaultValue: 0.0},
                delta_bb_max_x: {defaultValue: 0.0},
                bb_max_y: {defaultValue: 0.0},
                delta_bb_max_y: {defaultValue: 0.0},
                bb_max_z: {defaultValue: 0.0},
                delta_bb_max_z: {defaultValue: 0.0}
            }
        },
        SurfaceNode: {
            properties: {
                bbox_x: {defaultValue: 0.0},
                delta_bbox_x: {defaultValue: 0.0},
                bbox_y: {defaultValue: 0.0},
                delta_bbox_y: {defaultValue: 0.0},
                area: {defaultValue: 0.0},
                delta_area: {defaultValue: 0.0},
                perimeter: {defaultValue: 0.0},
                delta_perimeter: {defaultValue: 0.0},
                num_vertices: {defaultValue: 0.0},
                delta_num_vertices: {defaultValue: 0.0},
                compactness: {defaultValue: 0.0},
                delta_compactness: {defaultValue: 0.0}
            }
        }
    },
    '*'
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;
            """
        result, meta = self.db.cypher_query(query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][1]}, Relationships: {result[0][2]}")
        return result



