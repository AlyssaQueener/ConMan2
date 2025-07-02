from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
import json
    
class GraphPatch:

    unique_paths = {}

    patch_pattern = {
        "init": {},
        "updt": {}
    }

    ########################
    ### Helper Functions ###
    ########################

    def create_patch_pattern(self, node, timestamp, pushout_id, visited=None):
        if node.element_id in visited:
            return
        visited.add(node.element_id)

        if self.patch_pattern[timestamp].get(pushout_id) is None:
            self.patch_pattern[timestamp][pushout_id] = {"pushout_nodes": {}, "pushout_relations": {}, "gluing_relations": {}}

        if node.pushout_id is None:
            node.pushout_id = pushout_id
            self.patch_pattern[timestamp][pushout_id]["pushout_nodes"][node.element_id] = node.__properties__
            node.save()
            for adjacent in node.relation_to.all() + node.relation_from.all():
                relation_to = node.relation_to.relationship(adjacent)
                relation_from = node.relation_from.relationship(adjacent)
                # If receiving end is also not equiv, assign pushout id to relation
                if not adjacent.equivalent_to.all() and adjacent.timestamp == timestamp:
                    if relation_to is not None:
                        if relation_to.pushout_id is None:
                            relation_to.pushout_id = pushout_id
                            self.patch_pattern[timestamp][pushout_id]["pushout_relations"][relation_to.element_id] = {"source": node.element_id, "target": adjacent.element_id, "properties": relation_to.__properties__}
                            relation_to.save()
                    if relation_from is not None:
                        if relation_from.pushout_id is None:
                            relation_from.pushout_id = pushout_id
                            self.patch_pattern[timestamp][pushout_id]["pushout_relations"][relation_from.element_id] = {"source": adjacent.element_id, "target": node.element_id, "properties": relation_from.__properties__}
                            relation_from.save()
                    self.create_patch_pattern(adjacent, timestamp, pushout_id, visited)
                # If receiving end is equiv, assign gluing id = pushout id
                elif adjacent.equivalent_to.all() is not None and adjacent.timestamp == timestamp:
                    if relation_to:
                        if relation_to.gluing_id is None:
                            relation_to.gluing_id = pushout_id
                            self.patch_pattern[timestamp][pushout_id]["gluing_relations"][relation_to.element_id] = {"source": node.element_id, "target": self.unique_paths[adjacent.element_id], "properties": relation_to.__properties__}
                            relation_to.save()
                    if relation_from:
                        if relation_from.gluing_id is None:
                            relation_from.gluing_id = pushout_id
                            self.patch_pattern[timestamp][pushout_id]["gluing_relations"][relation_from.element_id] = {"source": self.unique_paths[adjacent.element_id], "target": adjacent.element_id, "properties": relation_from.__properties__}
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
                self.create_patch_pattern(node_init, timestamp_init, id_counter_init, visited_init)
                id_counter_init += 1


        for node_updt in pushout_nodes_updt:
            if node_updt.pushout_id is None and node_updt.element_id not in visited_updt:
                self.create_patch_pattern(node_updt, timestamp_updt, id_counter_updt, visited_updt)
                id_counter_updt += 1

        with open("Patch_Test.json", "w") as f:
            json.dump(self.patch_pattern, f)