from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties

from neomodel import Traversal #???

class GraphDiff:

    ########################
    ### Helper Functions ###
    ########################

    def create_equivalence_relations(self, equiv_node_init, equiv_node_updt):
        for init_adjacent in equiv_node_init.relation_to.all() + equiv_node_init.relation_from.all():
            for updt_adjacent in equiv_node_updt.relation_to.all() + equiv_node_updt.relation_from.all():
                rel_init = equiv_node_init.relation_to.relationship(init_adjacent) or equiv_node_init.relation_from.relationship(init_adjacent)
                rel_updt = equiv_node_updt.relation_to.relationship(updt_adjacent) or equiv_node_updt.relation_from.relationship(updt_adjacent)
                if (
                    rel_init.rel_type == rel_updt.rel_type
                    and rel_init.list_index == rel_updt.list_index
                    and init_adjacent.EntityType == updt_adjacent.EntityType
                ):
                    # Check if this equivalence already exists
                    if updt_adjacent not in init_adjacent.equivalent_to.all():
                        init_adjacent.equivalent_to.connect(updt_adjacent)
                        self.create_equivalence_relations(init_adjacent, updt_adjacent)
                    break  # Stop after first match

    def get_pushout_pattern(self, timestamp_init, timestamp_updt):
        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()



    ######################
    ### Main Functions ###
    ######################

    def run_diff(self, timestamp_init:str, timestamp_updt:str):

        project_init = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_init)
        project_updt = Node.nodes.get(EntityType="IfcProject", timestamp=timestamp_updt)
        #Looks directed but is undirectedly treated.
        project_init.equivalent_to.connect(project_updt)

        self.create_equivalence_relations(project_init, project_updt)
        #self.get_pushout_pattern(timestamp_init, timestamp_updt)