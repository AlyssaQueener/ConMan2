from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
import json
import os
from data_handler.DataHandler import DataHandler

class GraphPatch:

    def __init__(self, timestamp_init: str, timestamp_updt: str):
        self.unique_paths_to_node_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.topological_patch_pattern = {timestamp_init: {}, timestamp_updt: {}}
        self.semantic_patch_pattern = {}
        self.nodes_to_delete = []
        self.context_nodes = []
        self.gluing_nodes_init = []
        self.gluing_nodes_updt = []

    ########################
    ### Helper Functions ###
    ########################

    def create_unique_path_mappings(self, node, timestamp, unique_path=None):
        if node.element_id not in self.node_ids_to_unique_paths_mapping[timestamp]:
            if type(node) == PrimaryNode:
                unique_path = [{"primary_node": node.GlobalId}]
            if type(node) == ConnectionNode:
                unique_path = [{"connection_node": node.GlobalId}]

            self.node_ids_to_unique_paths_mapping[timestamp][node.element_id] = DataHandler.path_to_string(unique_path)
            self.unique_paths_to_node_mapping[timestamp][DataHandler.path_to_string(unique_path)] = node

            for child in node.relation_to.all():
                rel = node.relation_to.relationship(child)
                new_path = unique_path + [{"rel_type": rel.rel_type, "list_index": rel.list_index, "EntityType": child.EntityType}]
                self.create_unique_path_mappings(child, timestamp, new_path)


    def find_node_from_unique_path(self, unique_path: str, timestamp):
        path = DataHandler.string_to_path(unique_path)
        if "primary_node" in path[0]:
            start_node = PrimaryNode.nodes.get(timestamp=timestamp, GlobalId=path[0]["primary_node"])
        elif "connection_node" in path[0]:
            start_node = ConnectionNode.nodes.get(timestamp=timestamp, GlobalId=path[0]["connection_node"])
        latest_node = start_node
        for i in range(1, len(path)):
            for contestant in latest_node.relation_to.match(rel_type=path[i]["rel_type"], list_index=path[i]["list_index"]):
                if contestant.EntityType == path[i]["EntityType"]:
                    latest_node = contestant
            i += 1
        return latest_node
    
    
    def create_semantic_patch_pattern(self, equivalent_nodes_init, timestamp_init, timestamp_updt):
        for node_init in equivalent_nodes_init:
            node_updt = node_init.equivalent_to.all()[0]
            unique_path = self.node_ids_to_unique_paths_mapping[timestamp_init][node_init.element_id]
            for property_key, property_value in node_init.__properties__.items():
                if property_key not in ["timestamp", "element_id_property"]:
                    if property_value != node_updt.__properties__.get(property_key):
                        if unique_path not in self.semantic_patch_pattern:
                            self.semantic_patch_pattern[unique_path] = {}
                        self.semantic_patch_pattern[unique_path][property_key] = {}
                        self.semantic_patch_pattern[unique_path][property_key][timestamp_init] = property_value
                        self.semantic_patch_pattern[unique_path][property_key][timestamp_updt] = node_updt.__properties__.get(property_key)


    def create_topological_patch_pattern(self, pushout_nodes, timestamp):
        for pushout_node in pushout_nodes:
            self.topological_patch_pattern[timestamp][pushout_node.element_id] = {"properties": {**dict(pushout_node.__properties__)}, "node_type": type(pushout_node).__name__, "path": "", "relation_to": {}, "context_to": {}, "context_from": {}}
            if pushout_node.element_id in self.node_ids_to_unique_paths_mapping[timestamp]:
                self.topological_patch_pattern[timestamp][pushout_node.element_id]["path"] = self.node_ids_to_unique_paths_mapping[timestamp][pushout_node.element_id]
            for adjacent in pushout_node.relation_to.all():
                if adjacent.timestamp != pushout_node.timestamp:
                    continue
                relation_to = pushout_node.relation_to.relationship(adjacent)
                if adjacent.equivalent_to.all():
                    self.topological_patch_pattern[timestamp][pushout_node.element_id]["context_to"][adjacent.element_id] = {"path": self.node_ids_to_unique_paths_mapping[timestamp][adjacent.element_id], "properties": relation_to.__properties__}
                else:
                    self.topological_patch_pattern[timestamp][pushout_node.element_id]["relation_to"][adjacent.element_id] = {"properties": relation_to.__properties__}
            for adjacent in pushout_node.relation_from.all():
                if adjacent.timestamp != pushout_node.timestamp:
                    continue
                relation_from = pushout_node.relation_from.relationship(adjacent)
                if adjacent.equivalent_to.all():
                    self.topological_patch_pattern[timestamp][pushout_node.element_id]["context_from"][adjacent.element_id] = {"path": self.node_ids_to_unique_paths_mapping[timestamp][adjacent.element_id], "properties": relation_from.__properties__}


    def load_patch_from_file(self, path_topo, path_sema):
        with open(path_sema, "r") as f:
            self.semantic_patch_pattern = json.load(f)
        with open(path_topo, "r") as f:
            self.topological_patch_pattern = json.load(f)


    def find_nodes_to_delete(self, node):
        if node not in self.nodes_to_delete:
            self.nodes_to_delete.append(node)
        else:
            return
        for adjacent in node.relation_to.all() + node.relation_from.all():
            if adjacent in self.context_nodes:
                continue
            else:
                self.find_nodes_to_delete(adjacent)


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

        pushout_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=False).all()
        pushout_nodes_updt = Node.nodes.filter(timestamp=timestamp_updt).has(equivalent_to=False).all()
        equivalent_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()

        self.create_semantic_patch_pattern(equivalent_nodes_init, timestamp_init, timestamp_updt)
        self.create_topological_patch_pattern(pushout_nodes_init, timestamp_init)
        self.create_topological_patch_pattern(pushout_nodes_updt, timestamp_updt)

        os.makedirs("patch_data", exist_ok=True)
        with open(f"patch_data/Patch_Topo_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(self.topological_patch_pattern, f, indent=4)
        with open(f"patch_data/Patch_Sema_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(self.semantic_patch_pattern, f, indent=4)

    
    def apply_patch(self, timestamp_init:str, timestamp_updt:str):
        prim_and_con_init = list(PrimaryNode.nodes.filter(timestamp=timestamp_init)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_init))
        
        for node in prim_and_con_init:
            self.create_unique_path_mappings(node, timestamp_init)

        for node in Node.nodes.all():
            if node.element_id not in self.node_ids_to_unique_paths_mapping[timestamp_init]:
                self.nodes_to_delete.append(node)

        for key, pushout_node_ref in self.topological_patch_pattern[timestamp_init].items():
            if pushout_node_ref["path"]:
                pushout_node = self.unique_paths_to_node_mapping[timestamp_init][pushout_node_ref["path"]]
                self.nodes_to_delete.append(pushout_node)
            # context_nodes_to = pushout_node["context_to"]
            # context_nodes_from = pushout_node["context_from"]
            # if context_nodes_to:
            #     for key, context_node_ref in context_nodes_to.items():
            #         context_node = self.find_node_from_unique_path(context_node_ref["path"], timestamp_init)
            #         if context_node not in self.context_nodes:
            #             self.context_nodes.append(context_node)
            #         for adjacent in context_node.relation_from.all():
            #             if adjacent.relation_to.relationship(context_node).rel_type == context_node_ref["properties"]["rel_type"] and adjacent.relation_to.relationship(context_node).list_index == context_node_ref["properties"]["list_index"]:
            #                 if adjacent not in self.gluing_nodes_init:
            #                     self.gluing_nodes_init.append(adjacent)
            # if context_nodes_from:
            #     for key, context_node_ref in context_nodes_from.items():
            #         context_node = self.find_node_from_unique_path(context_node_ref["path"], timestamp_init)
            #         if context_node not in self.context_nodes:
            #             self.context_nodes.append(context_node)
            #         for adjacent in context_node.relation_to.all():
            #             if adjacent.relation_from.relationship(context_node).rel_type == context_node_ref["properties"]["rel_type"] and adjacent.relation_from.relationship(context_node).list_index == context_node_ref["properties"]["list_index"]:
            #                 if adjacent not in self.gluing_nodes_init:
            #                     self.gluing_nodes_init.append(adjacent)

        # 288 original nodes
        # for gluing_node in self.gluing_nodes_init:
        #     self.find_nodes_to_delete(gluing_node)

        # for node in Node.nodes.all():
        #     if node.element_id not in self.node_ids_to_unique_paths_mapping:
        #         self.nodes_to_delete.append(node)

        for node in self.nodes_to_delete:
            for adjacent in node.relation_to.all():
                node.relation_to.disconnect(adjacent)
            for adjacent in node.relation_from.all():
                node.relation_from.disconnect(adjacent)
            node.delete()

        
        for key, pushout_node in self.topological_patch_pattern[timestamp_updt].items():
            pass
