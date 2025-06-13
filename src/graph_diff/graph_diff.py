from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties

from neomodel import Traversal #???

class GraphDiff:

    ########################
    ### Helper Functions ###
    ########################

    def create_mcs(self, equiv_node_init, equiv_node_updt):
        for init_child in equiv_node_init.relation.all():
            for updt_child in equiv_node_updt.relation.all():
                rel_init = equiv_node_init.relation.relationship(init_child)
                rel_updt = equiv_node_updt.relation.relationship(updt_child)
                if (
                    rel_init.rel_type == rel_updt.rel_type
                    and rel_init.list_index == rel_updt.list_index
                    and init_child.EntityType == updt_child.EntityType
                ):
                    # Check if this equivalence already exists
                    if updt_child not in init_child.equivalent_to.all():
                        init_child.equivalent_to.connect(updt_child)
                        self.create_mcs(init_child, updt_child)
                    break  # Stop after first match




    def get_children_and_paths(self, node):
        # Set needed for its diff methods.
        children_and_paths = set()
        # Get all children of the node.
        children = node.relation.all()
        # Iterate over all children and store the ingoing relation and the entity.
        for child in children:
            rel_type = node.relation.relationship(child).rel_type
            list_index = node.relation.relationship(child).list_index
            children_and_paths.add((rel_type, list_index, child.EntityType))
        return children_and_paths
    
    def get_pushout_and_mcs(self, children_and_paths_init, children_and_paths_updt):
        # Get Pushouts by diffing one from the other.
        pushout_init = children_and_paths_init - children_and_paths_updt
        pushout_updt = children_and_paths_updt - children_and_paths_init
        # Get maximal common subgraph by diffing init pushout from init full.
        mcs = children_and_paths_init - pushout_init
        return {"pushout_init": pushout_init, "pushout_updt": pushout_updt, "mcs": mcs}
    
    def recursive_diff(self, node_init, node_updt):
        children_init = self.get_children_and_paths(node_init)
        children_updt = self.get_children_and_paths(node_updt)
        pushout_and_mcs = self.get_pushout_and_mcs(children_init, children_updt)
        for node_data in pushout_and_mcs["mcs"]:
            node_init = Node.nodes.get(timestamp=node_init.timestamp, )
            node_updt = Node.nodes.get(timestamp=node_updt.timestamp)



    ######################
    ### Main Functions ###
    ######################

    def run_diff(self, timestamp_init:str, timestamp_updt:str):
        graph_init = Node.nodes.filter(timestamp=timestamp_init)
        graph_updt = Node.nodes.filter(timestamp=timestamp_updt)

        project_init = graph_init.get(EntityType="IfcProject")
        project_updt = graph_updt.get(EntityType="IfcProject")
        #Looks directed but is undirectedly treated.
        project_init.equivalent_to.connect(project_updt)

        # print(project_init.equivalent_to.all())
        # print(project_updt.equivalent_to.all())
        # print(project_init.relation.all())

        # print(f"Init: {project_init}\nUpdt: {project_updt}\n")

        # children_and_paths_init = self.get_children_and_paths(project_init)
        # children_and_paths_updt = self.get_children_and_paths(project_updt)
        # print(f"Init: {children_and_paths_init}\nUpdt: {children_and_paths_updt}")

        # pushout_and_mcs = self.get_pushout_and_mcs(children_and_paths_init, children_and_paths_updt)
        # print(pushout_and_mcs)

        self.create_mcs(project_init, project_updt)
