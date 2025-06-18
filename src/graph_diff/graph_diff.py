from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties

from neomodel import Traversal #???
import json

# Query for all nodes without equivalence
# match (n:Node) where not (n)-[:equivalent_to]-(:Node) return n

class GraphDiff:

    node_matching_table = []

    ########################
    ### Helper Functions ###
    ########################

    def create_equivalence_relations_primary(self, equiv_node_init, equiv_node_updt, unique_path_init=[], unique_path_updt=[]):
        # Reset unique path if the current node has a unique id
        if type(equiv_node_init) == PrimaryNode:
            unique_path_init = [equiv_node_init.GlobalId]
        if type(equiv_node_updt) == PrimaryNode:
            unique_path_updt = [equiv_node_updt.GlobalId]

        for child_init in equiv_node_init.relation_to.all():
            rel_init = equiv_node_init.relation_to.relationship(child_init)
            new_path_init = unique_path_init + [{"rel_type": rel_init.rel_type, "list_index": rel_init.list_index, "EntityType": child_init.EntityType}]
            
            for child_updt in equiv_node_updt.relation_to.all():
                rel_updt = equiv_node_updt.relation_to.relationship(child_updt)
                new_path_updt = unique_path_updt + [{"rel_type": rel_updt.rel_type, "list_index": rel_updt.list_index, "EntityType": child_updt.EntityType}]
                
                if (
                    rel_init.rel_type == rel_updt.rel_type
                    and rel_init.list_index == rel_updt.list_index
                    and child_init.EntityType == child_updt.EntityType
                    and not child_init.equivalent_to.all()
                    and not child_updt.equivalent_to.all()
                ):
                    child_init.equivalent_to.connect(child_updt)
                    self.node_matching_table.append([new_path_init.copy(), new_path_updt.copy()])
                    self.create_equivalence_relations_primary(child_init, child_updt, new_path_init, new_path_updt)


    # def create_equivalence_relations_connection(self, equiv_node_init, equiv_node_updt):
    #     for child_init in equiv_node_init.relation_to.all():
    #         for child_updt in equiv_node_updt.relation_to.all():
    #             rel_init = equiv_node_init.relation_to.relationship(child_init)
    #             rel_updt = equiv_node_updt.relation_to.relationship(child_updt)
    #             if (
    #                 rel_init.rel_type == rel_updt.rel_type
    #                 and rel_init.list_index == rel_updt.list_index
    #                 and child_init.EntityType == child_updt.EntityType
    #                 and child_init.equivalent_to is None
    #                 and child_updt.equivalent_to is None
    #             ):
    #                 equiv_node_init.equivalent_to.connect(equiv_node_updt)

    # def get_pushout_pattern(self, timestamp_init, timestamp_updt):
    #     pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
    #     pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()

    #     for node in pushout_nodes_init:
    #         setattr(node, "pushout", "TRUE")



    ######################
    ### Main Functions ###
    ######################

    def run_diff(self, timestamp_init:str, timestamp_updt:str):

        project_init = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_init)
        project_updt = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_updt)
        #Looks directed but is undirectedly treated.
        project_init.equivalent_to.connect(project_updt)

        # self.create_equivalence_relations(project_init, project_updt)
        for primary_node_init in PrimaryNode.nodes.filter(timestamp=timestamp_init):
            primary_node_updt = PrimaryNode.nodes.get(GlobalId=primary_node_init.GlobalId, timestamp=timestamp_updt)
            primary_node_init.equivalent_to.connect(primary_node_updt)
            self.create_equivalence_relations_primary(primary_node_init, primary_node_updt)

        # for connection_node_init in ConnectionNode.nodes.filter(timestamp=timestamp_init):
        #     connection_node_updt = ConnectionNode.nodes.get(GlobalId=connection_node_init.GlobalId, timestamp=timestamp_updt)


        # self.get_pushout_pattern(timestamp_init, timestamp_updt)