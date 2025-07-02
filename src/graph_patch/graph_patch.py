from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
    
class GraphPatch:

    unique_paths = {}

    ########################
    ### Helper Functions ###
    ########################

    def create_pushout_and_gluing_pattern(self, node, timestamp, pushout_id, visited=None):
        if node.element_id in visited:
            return
        visited.add(node.element_id)

        if node.pushout_id is None:
            node.pushout_id = pushout_id
            node.save()
            for adjacent in node.relation_to.all() + node.relation_from.all():
                relation_to = node.relation_to.relationship(adjacent)
                relation_from = node.relation_from.relationship(adjacent)
                # print(adjacent.equivalent_to.all())
                # print(relation_to)
                # If receiving end is also not equiv, assign pushout id to relation
                if not adjacent.equivalent_to.all() and adjacent.timestamp == timestamp:
                    if relation_to is not None:
                        if relation_to.pushout_id is None:
                            relation_to.pushout_id = pushout_id
                            relation_to.save()
                    if relation_from is not None:
                        if relation_from.pushout_id is None:
                            relation_from.pushout_id = pushout_id
                            relation_from.save()
                    self.create_pushout_and_gluing_pattern(adjacent, timestamp, pushout_id, visited)
                # If receiving end is equiv, assign gluing id = pushout id
                elif adjacent.equivalent_to.all() is not None and adjacent.timestamp == timestamp:
                    if relation_to:
                        if relation_to.gluing_id is None:
                            relation_to.gluing_id = pushout_id
                            relation_to.context_node = self.unique_paths[adjacent.element_id]
                            relation_to.save()
                    if relation_from:
                        if relation_from.gluing_id is None:
                            relation_from.gluing_id = pushout_id
                            relation_from.context_node = self.unique_paths[adjacent.element_id]
                            relation_from.save()

    ######################
    ### Main Functions ###
    ######################

    def create_patch(self, timestamp_init:str, timestamp_updt:str, unique_paths):

        self.unique_paths = unique_paths

        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()

        pushout_edges_init = None # filter alles relationships die zwishcen zwei knoten aus pushout init bestehen
        # und für updt

        id_counter_init = 0
        id_counter_updt = 0

        visited_init = set()
        visited_updt = set()

        for node_init in pushout_nodes_init:
            if node_init.pushout_id is None and node_init.element_id not in visited_init:
                self.create_pushout_and_gluing_pattern(node_init, timestamp_init, id_counter_init, visited_init)
                id_counter_init += 1


        for node_updt in pushout_nodes_updt:
            if node_updt.pushout_id is None and node_updt.element_id not in visited_updt:
                self.create_pushout_and_gluing_pattern(node_updt, timestamp_updt, id_counter_updt, visited_updt)
                id_counter_updt += 1

        