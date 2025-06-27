from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties

from neomodel import Traversal #???
import json

# Query for all nodes without equivalence
# match (n:Node) where not (n)-[:equivalent_to]-(:Node) return n

class GraphDiff:

    unique_paths = {}

    ########################
    ### Helper Functions ###
    ########################

    def create_equivalence_relations_primary(self, equiv_node_init, equiv_node_updt, unique_path_init=[], unique_path_updt=[]):
        # Reset unique path if the current node has a unique id
        if type(equiv_node_init) == PrimaryNode:
            unique_path_init = [{"primary_node": equiv_node_init.GlobalId}]
            self.unique_paths[equiv_node_init.element_id] = [{"primary_node": equiv_node_init.GlobalId}]
        if type(equiv_node_updt) == PrimaryNode:
            unique_path_updt = [{"primary_node": equiv_node_updt.GlobalId}]
            self.unique_paths[equiv_node_updt.element_id] = [{"primary_node": equiv_node_updt.GlobalId}]

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
                    self.unique_paths[child_init.element_id] = json.dumps(new_path_init.copy())
                    self.unique_paths[child_updt.element_id] = json.dumps(new_path_updt.copy())
                    self.create_equivalence_relations_primary(child_init, child_updt, new_path_init, new_path_updt)


    def create_equivalence_relations_connection(self, connection_node_init, connection_node_updt):

        common_children_count = 0

        for child_init in connection_node_init.relation_to.all():
            for child_updt in connection_node_updt.relation_to.all():
                if child_init.equivalent_to.relationship(child_updt) is not None:
                    common_children_count += 1

        unique_children_count_init = len(connection_node_init.relation_to.all()) - common_children_count
        unique_children_count_updt = len(connection_node_updt.relation_to.all()) - common_children_count

        iou = common_children_count / (unique_children_count_init + common_children_count + unique_children_count_updt)
        if iou == 1.0:
            connection_node_init.equivalent_to.connect(connection_node_updt)
            self.unique_paths[connection_node_init.element_id] = {"connection_node": connection_node_init.GlobalId}
            self.unique_paths[connection_node_updt.element_id] = {"connection_node": connection_node_updt.GlobalId}           


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

        for connection_node_init in ConnectionNode.nodes.filter(timestamp=timestamp_init):
            for connection_node_updt in ConnectionNode.nodes.filter(timestamp=timestamp_updt):
                self.create_equivalence_relations_connection(connection_node_init, connection_node_updt)