from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
import json
from data_handler.DataHandler import DataHandler
    
class GraphPatch:

    unique_paths_to_node_ids_mapping = {"init": {}, "updt": {}}
    node_ids_to_unique_paths_mapping = {"init": {}, "updt": {}}

    topological_patch_pattern = {
        "init": {},
        "updt": {}
    }

    semantic_patch_pattern = {}

    ########################
    ### Helper Functions ###
    ########################

    def create_unique_path_mappings(self, node, timestamp, unique_path=None):

        if node.element_id not in self.node_ids_to_unique_paths_mapping[timestamp]:

            if unique_path == None:
                if type(node) == PrimaryNode:
                    unique_path = [{"primary_node": node.GlobalId}]
                if type(node) == ConnectionNode:
                    unique_path = [{"connection_node": node.GlobalId}]

            self.node_ids_to_unique_paths_mapping[timestamp][node.element_id] = DataHandler.path_to_hash(unique_path)
            self.unique_paths_to_node_ids_mapping[timestamp][DataHandler.path_to_hash(unique_path)] = node.element_id

            for child in node.relation_to.all():
                rel = node.relation_to.relationship(child)
                new_path = unique_path + [{"rel_type": rel.rel_type, "list_index": rel.list_index, "EntityType": child.EntityType}]
                self.create_unique_path_mappings(child, timestamp, new_path)



    def create_topological_patch_pattern(self, node, timestamp, pushout_id, visited=None):
        if node.element_id in visited:
            return
        visited.add(node.element_id)

        if self.topological_patch_pattern[timestamp].get(pushout_id) is None:
            self.topological_patch_pattern[timestamp][pushout_id] = {"pushout_nodes": {}, "pushout_relations": {}, "gluing_relations": {}}

        if node.pushout_id is None:
            node.pushout_id = pushout_id
            self.topological_patch_pattern[timestamp][pushout_id]["pushout_nodes"][node.element_id] = node.__properties__
            node.save()
            for adjacent in node.relation_to.all() + node.relation_from.all():
                relation_to = node.relation_to.relationship(adjacent)
                relation_from = node.relation_from.relationship(adjacent)
                # If receiving end is also not equiv, assign pushout id to relation
                if not adjacent.equivalent_to.all() and adjacent.timestamp == timestamp:
                    if relation_to is not None:
                        if relation_to.pushout_id is None:
                            relation_to.pushout_id = pushout_id
                            self.topological_patch_pattern[timestamp][pushout_id]["pushout_relations"][relation_to.element_id] = {"source": node.element_id, "target": adjacent.element_id, "properties": relation_to.__properties__}
                            relation_to.save()
                    if relation_from is not None:
                        if relation_from.pushout_id is None:
                            relation_from.pushout_id = pushout_id
                            self.topological_patch_pattern[timestamp][pushout_id]["pushout_relations"][relation_from.element_id] = {"source": adjacent.element_id, "target": node.element_id, "properties": relation_from.__properties__}
                            relation_from.save()
                    self.create_topological_patch_pattern(adjacent, timestamp, pushout_id, visited)
                # If receiving end is equiv, assign gluing id = pushout id
                elif adjacent.equivalent_to.all() is not None and adjacent.timestamp == timestamp:
                    if relation_to:
                        if relation_to.gluing_id is None:
                            relation_to.gluing_id = pushout_id
                            self.topological_patch_pattern[timestamp][pushout_id]["gluing_relations"][relation_to.element_id] = {"pushout": node.element_id, "context": self.node_ids_to_unique_paths_mapping[timestamp][adjacent.element_id], "properties": relation_to.__properties__, "direction": "pushout_to_context"}
                            relation_to.save()
                    if relation_from:
                        if relation_from.gluing_id is None:
                            relation_from.gluing_id = pushout_id
                            self.topological_patch_pattern[timestamp][pushout_id]["gluing_relations"][relation_from.element_id] = {"context": self.node_ids_to_unique_paths_mapping[timestamp][adjacent.element_id], "pushout": adjacent.element_id, "properties": relation_from.__properties__, "direction": "context_to_context"}
                            relation_from.save()


    def create_semantic_patch_pattern(self, equivalent_nodes_init, timestamp_init):
        for node_init in equivalent_nodes_init:
            node_updt = node_init.equivalent_to.all()[0]
            unique_path = self.node_ids_to_unique_paths_mapping[timestamp_init][node_init.element_id]
            for property_key, property_value in node_init.__properties__.items():
                if property_key not in ["timestamp", "element_id_property"]:
                    if property_value != node_updt.__properties__.get(property_key):
                        if unique_path not in self.semantic_patch_pattern:
                            self.semantic_patch_pattern[unique_path] = {}
                        self.semantic_patch_pattern[unique_path][property_key] = {}
                        self.semantic_patch_pattern[unique_path][property_key]["init"] = property_value
                        self.semantic_patch_pattern[unique_path][property_key]["updt"] = node_updt.__properties__.get(property_key)


    def load_patch_from_file(self, path_topo, path_sema):
        with open(path_sema, "r") as f:
            self.semantic_patch_pattern = json.load(f)
        with open(path_topo, "r") as f:
            self.topological_patch_pattern = json.load(f)


    ######################
    ### Main Functions ###
    ######################

    def create_patch(self, timestamp_init:str, timestamp_updt:str):

        prim_and_con_init = list(PrimaryNode.nodes.filter(timestamp=timestamp_init)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_init))
        prim_and_con_updt = list(PrimaryNode.nodes.filter(timestamp=timestamp_updt)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_updt))

        for node in prim_and_con_init:
            self.create_unique_path_mappings(node, timestamp_init)
        for node in prim_and_con_updt:
            self.create_unique_path_mappings(node, timestamp_updt)

        with open(f"Patch_unique_paths_to_node_ids_mapping.json", "w") as f:
            json.dump(self.unique_paths_to_node_ids_mapping, f, indent=4)
        with open(f"Patch_node_ids_to_unique_paths_mapping.json", "w") as f:
            json.dump(self.node_ids_to_unique_paths_mapping, f, indent=4)

        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()
        equivalent_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()

        
        self.create_semantic_patch_pattern(equivalent_nodes_init, timestamp_init)


        pushout_id_counter_init = 0
        pushout_id_counter_updt = 0

        visited_init = set()
        visited_updt = set()

        for node_init in pushout_nodes_init:
            if node_init.pushout_id is None and node_init.element_id not in visited_init:
                self.create_topological_patch_pattern(node_init, timestamp_init, pushout_id_counter_init, visited_init)
                pushout_id_counter_init += 1


        for node_updt in pushout_nodes_updt:
            if node_updt.pushout_id is None and node_updt.element_id not in visited_updt:
                self.create_topological_patch_pattern(node_updt, timestamp_updt, pushout_id_counter_updt, visited_updt)
                pushout_id_counter_updt += 1

        with open(f"Patch_Topo_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(self.topological_patch_pattern, f, indent=4)

        with open(f"Patch_Sema_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(self.semantic_patch_pattern, f, indent=4)


    # def apply_patch(self, timestamp_init, timestamp_updt):
    #     for 