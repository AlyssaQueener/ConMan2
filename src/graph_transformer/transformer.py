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
            
    
            print(f"Merged {node.EntityType} with {equvivalent.EntityType}")

        msc_2 = Node.nodes.filter(timestamp="msc").all() + GenericGeoNode.nodes.filter(timestamp="msc").all()
        for node in msc_2:
            if hasattr(node, "change_type"): 
                setattr(node, "graph_type", graph_type)
            else:
                setattr(node, "change_type", "msc")
                setattr(node, "encoded_change_type", [1,0,0])
                setattr(node, "graph_type", graph_type)
            print(node)
            node.save()
        self.db.cypher_query("MATCH ()-[r:EQUIVALENT_TO]->() DELETE r")

    def edit_pushout_nodes(self, timestamp_init, timestamp_updt, graph_type):
        print("######## Pushout init ############")
        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        for node in pushout_nodes_init:
            setattr(node, "change_type", "deleted")
            setattr(node, "encoded_change_type", [0,1,0])
            setattr(node, "graph_type", graph_type)
            node.save()
        print(pushout_nodes_init)
        print("######## Pushout updated ############")
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all() + GenericGeoNode.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()
        for node in pushout_nodes_updt:
            setattr(node, "change_type", "added")
            setattr(node, "encoded_change_type", [0,0,1])
            setattr(node, "graph_type", graph_type)
            node.save()
        print(pushout_nodes_updt)
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

    def train_graphsage_for_change_interpretation(self, model_name='geometric-change-interpreter'):
        """
        Train GraphSAGE on all geometric transformation scenarios together
        """
    
        # Drop existing graph projection if it exists
        print("########## Cleaning up existing projection ##########")
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
                PrimaryNode: {properties: ['text_embedding']},
                ConnectionNode: {properties: ['text_embedding']},
                SecondaryNode: {properties: ['text_embedding']},
                InlineNode: {properties: ['text_embedding']}
            },
            '*'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
    
        result, meta = self.db.cypher_query(project_query)
        print(f"Projected graph: {result[0][0]}, Nodes: {result[0][1]}, Relationships: {result[0][2]}")
    
        print("########## Training GraphSAGE ##########")
        # Train on all scenarios
        train_query = """
        CALL gds.beta.graphSage.train(
            'geometric_transformations',
            {
                modelName: $model_name,
                featureProperties: ['text_embedding'],
                aggregator: 'mean',
                activationFunction: 'relu',
                sampleSizes: [25, 10],
                epochs: 20,
                embeddingDimension: 128
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
        



