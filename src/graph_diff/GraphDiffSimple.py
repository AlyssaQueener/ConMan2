from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
from data_handler.DataHandler import DataHandler

from neomodel import Traversal #???
import json

# Query for all nodes without equivalence
# match (n:Node) where not (n)-[:equivalent_to]-(:Node) return n

class GraphDiffSimple:

    ########################
    ### Helper Functions ###
    ########################

    

    def create_equivalence_relations_connection(self, connection_node_init, connection_node_updt):
        """
        Traverse the two parsed models starting from ConnectionNodes and find equivalent nodes. Create equilavent_to relations between them.
        """
        # Check if a globalid exists on the nodes and if they are the same.
        if hasattr(connection_node_init, 'GlobalId'):
            if hasattr(connection_node_updt, 'GlobalId'):
                if connection_node_init.GlobalId == connection_node_updt.GlobalId:
                    connection_node_init.equivalent_to.connect(connection_node_updt)
                    return
                 


    ######################
    ### Main Functions ###
    ######################

    def run_diff(self, timestamp_init:str, timestamp_updt:str):
        """
        Recursively compares nodes on graph for equivalence and generates equivalent_to relations between them.
        """
        project_init = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_init)
        project_updt = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_updt)
        #Looks directed but is undirectedly treated.
        project_init.equivalent_to.connect(project_updt)

        # For PrimaryNodes, find partners using the globalid, then run the recursive function.
        for primary_node_init in PrimaryNode.nodes.filter(timestamp=timestamp_init):
            try:
                primary_node_updt = PrimaryNode.nodes.get(GlobalId=primary_node_init.GlobalId, timestamp=timestamp_updt)
            except:
                continue
            primary_node_init.equivalent_to.connect(primary_node_updt)
        # For ConnectionNodes, find all in both models, then run the Intersection over Union function.
        for connection_node_init in ConnectionNode.nodes.filter(timestamp=timestamp_init):
            for connection_node_updt in ConnectionNode.nodes.filter(timestamp=timestamp_updt):
                self.create_equivalence_relations_connection(connection_node_init, connection_node_updt)