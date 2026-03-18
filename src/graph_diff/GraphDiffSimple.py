from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, RelProperties, GeoRelProperties, GenericGeoNode
from data_handler.DataHandler import DataHandler

from neomodel import Traversal #???
import json

# Query for all nodes without equivalence
# match (n:Node) where not (n)-[:equivalent_to]-(:Node) return n

class GraphDiffSimple:

    ########################
    ### Helper Functions ###
    ########################
    def create_equvivalence_relationships_for_geo_nodes(self, equiv_node_init, equiv_node_updt):
        for child_init in equiv_node_init.relation_geo.all():
            rel_init = equiv_node_init.relation_geo.relationship(child_init)
            # Iterate over all corresponding node's related nodes.
            for child_updt in equiv_node_updt.relation_geo.all():
                rel_updt = equiv_node_updt.relation_geo.relationship(child_updt)
                # Check if the child nodes are equivalent.
                if (
                    rel_init.rel_type == rel_updt.rel_type
                    and rel_init.list_index == rel_updt.list_index
                    and child_init.EntityType == child_updt.EntityType
                    and not child_init.equivalent_to.filter(timestamp=child_init.timestamp)
                    and not child_updt.equivalent_to.filter(timestamp=child_updt.timestamp)
                ):
                    # Create equivalent_to edge and recursively run the funciton.
                    child_init.equivalent_to.connect(child_updt)
        
    
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

    def run_diff(self, timestamp_init:str, timestamp_updt:str, graph_type:str):
        """
        Recursively compares nodes on graph for equivalence and generates equivalent_to relations between them.
        """
        project_init = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_init, graph_type=graph_type)
        project_updt = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_updt, graph_type=graph_type)
        #Looks directed but is undirectedly treated.
        project_init.equivalent_to.connect(project_updt)

        # For PrimaryNodes, find partners using the globalid, then run the recursive function.
        for primary_node_init in PrimaryNode.nodes.filter(timestamp=timestamp_init, graph_type=graph_type ):
            try:
                primary_node_updt = PrimaryNode.nodes.get(GlobalId=primary_node_init.GlobalId, timestamp=timestamp_updt, graph_type=graph_type)
            except:
                continue
            primary_node_init.equivalent_to.connect(primary_node_updt)
            self.create_equvivalence_relationships_for_geo_nodes(primary_node_init, primary_node_updt)
        # For ConnectionNodes, find all in both models, then run the Intersection over Union function.
        for connection_node_init in ConnectionNode.nodes.filter(timestamp=timestamp_init, graph_type=graph_type):
            for connection_node_updt in ConnectionNode.nodes.filter(timestamp=timestamp_updt, graph_type=graph_type):
                self.create_equivalence_relations_connection(connection_node_init, connection_node_updt)