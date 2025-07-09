from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
import json
from data_handler.DataHandler import DataHandler
    
class GraphPatch:

    def __init__(self):
        # INSTANCE variables (unique per object)
        self.unique_paths_to_node_mapping = {"init": {}, "updt": {}}
        self.node_ids_to_unique_paths_mapping = {"init": {}, "updt": {}}
        self.topological_patch_pattern = {"init": {}, "updt": {}}
        self.semantic_patch_pattern = {}
        self.nodes_to_delete = []


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
        for i in range(1, len(path)-1):
            for contestant in latest_node.relation_to.match(rel_type=path[i]["rel_type"], list_index=path[i]["list_index"]):
                if contestant.EntityType == path[i]["EntityType"]:
                    latest_node = contestant
            i += 1
        return latest_node



    def create_topological_patch_pattern(self, node, timestamp, pushout_id, visited=None):
        if node.element_id in visited:
            return
        visited.add(node.element_id)

        if self.topological_patch_pattern[timestamp].get(pushout_id) is None:
            self.topological_patch_pattern[timestamp][pushout_id] = {"pushout_nodes": {}, "pushout_relations": {}, "gluing_relations": {}}

        if node.pushout_id is None:
            node.pushout_id = pushout_id
            self.topological_patch_pattern[timestamp][pushout_id]["pushout_nodes"][node.element_id] = {"properties": {**dict(node.__properties__)}, "node_type": type(node).__name__}
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
                            self.topological_patch_pattern[timestamp][pushout_id]["gluing_relations"][relation_from.element_id] = {"context": self.node_ids_to_unique_paths_mapping[timestamp][adjacent.element_id], "pushout": node.element_id, "properties": relation_from.__properties__, "direction": "context_to_pushout"}
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


    def delete_pushout_node(self, node, pushout_pattern):
        for gluing_relation in pushout_pattern["gluing_relations"]:
            if self.node_ids_to_unique_paths_mapping[node.element_id] == gluing_relation["context"]:
                return
            

    def find_nodes_to_delete(self, node, context_nodes):
        # Traverses nodes until a context node is hit. no checking with the patch relations.
        if node in self.nodes_to_delete:
            return
        for adjacent in node.relation_to.all():
            if adjacent in context_nodes:
                return
            else:
                self.nodes_to_delete.append(node)
        for adjacent in node.relation_from.all():
            if adjacent in context_nodes:
                return
            else:
                self.nodes_to_delete.append(node)


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


    def apply_patch(self, timestamp_init: str, timestamp_updt:str):

        prim_and_con_init = list(PrimaryNode.nodes.filter(timestamp=timestamp_init)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_init))
        for node in prim_and_con_init:
            self.create_unique_path_mappings(node, timestamp_init)

        # Deletion of init part

        # Delete all nodes without unique paths as they are not reachable in any way and so always have to be patched out
        for node in Node.nodes.all():
            if node.element_id not in self.node_ids_to_unique_paths_mapping[timestamp_init]:
                for adjacent in node.relation_to.all():
                    node.relation_to.disconnect(adjacent)
                for adjacent in node.relation_from.all():
                    node.relation_from.disconnect(adjacent)
                node.delete()

        for pushout_id in self.topological_patch_pattern[timestamp_init].keys():
            pushout_pattern = self.topological_patch_pattern[timestamp_init][pushout_id]
            context_nodes = []
            gluing_nodes = []
            for gluing_relation_id, gluing_relation in pushout_pattern["gluing_relations"].items():
                # context_node = self.unique_paths_to_node_mapping[timestamp_init][gluing_relation["context"]]
                context_node = self.find_node_from_unique_path(unique_path=gluing_relation["context"], timestamp=timestamp_init)
                if context_node not in context_nodes:
                    context_nodes.append(context_node)
                gluing_node_entry = pushout_pattern["pushout_nodes"][gluing_relation["pushout"]]
                gluing_relation_rel_type = gluing_relation["properties"]["rel_type"]
                gluing_relation_list_index = gluing_relation["properties"]["list_index"]
                if gluing_relation["direction"] == "pushout_to_context":
                    pushout_contestants = context_node.relation_from.all()
                    for pushout_contestant in pushout_contestants:
                        rel_type = context_node.relation_from.relationship(pushout_contestant).rel_type
                        list_index = context_node.relation_from.relationship(pushout_contestant).list_index
                        if (
                            gluing_relation_rel_type == rel_type
                            and gluing_relation_list_index == list_index
                            and gluing_node_entry["properties"]["EntityType"] == pushout_contestant.EntityType
                            and pushout_contestant not in gluing_nodes
                        ):
                            gluing_nodes.append(pushout_contestant)
                elif gluing_relation["direction"] == "context_to_pushout":
                    pushout_contestants = context_node.relation_to.all()
                    for pushout_contestant in pushout_contestants:
                        rel_type = context_node.relation_to.relationship(pushout_contestant).rel_type
                        list_index = context_node.relation_to.relationship(pushout_contestant).list_index
                        if (
                            gluing_relation_rel_type == rel_type
                            and gluing_relation_list_index == list_index
                            and gluing_node_entry["properties"]["EntityType"] == pushout_contestant.EntityType
                            and pushout_contestant not in gluing_nodes
                        ):
                            gluing_nodes.append(pushout_contestant)
                            self.nodes_to_delete.append(pushout_contestant)

            for gluing_node in gluing_nodes:
                self.find_nodes_to_delete(gluing_node, context_nodes)

            for node in self.nodes_to_delete:
                try:
                    for adjacent in node.relation_to.all():
                        node.relation_to.disconnect(adjacent)
                    for adjacent in node.relation_from.all():
                        node.relation_from.disconnect(adjacent)
                    node.delete()
                except:
                    pass

        # Insertion of updt part

        for pushout_id in self.topological_patch_pattern[timestamp_updt].keys():
            pushout_node_id_to_added_node_mapping = {}
            added_node_id_to_pushout_id_mapping = {}
            pushout_pattern = self.topological_patch_pattern[timestamp_updt][pushout_id]
            for node_id, node in pushout_pattern["pushout_nodes"].items():
                node_class = globals()[node["node_type"]]
                node_obj = node_class(**node["properties"])
                delattr(node_obj, "element_id_property")
                node_obj.save()
                pushout_node_id_to_added_node_mapping[node["properties"]["element_id_property"]] = node_obj
                added_node_id_to_pushout_id_mapping[node_obj.element_id] = pushout_node_id_to_added_node_mapping[node["properties"]["element_id_property"]]

            if pushout_pattern["pushout_relations"]:
                for rel_id, relation in pushout_pattern["pushout_relations"].items():
                    del relation["properties"]["element_id_property"]
                    source_node = pushout_node_id_to_added_node_mapping[relation["source"]]
                    target_node = pushout_node_id_to_added_node_mapping[relation["target"]]
                    source_node.relation_to.connect(target_node, relation["properties"])
            
            if pushout_pattern["gluing_relations"]:
                for rel_id, relation in pushout_pattern["gluing_relations"].items():
                    del relation["properties"]["element_id_property"]
                    # context_node = self.unique_paths_to_node_mapping[timestamp_init][relation["context"]]
                    context_node = self.find_node_from_unique_path(unique_path=relation["context"], timestamp=timestamp_init)
                    gluing_node = pushout_node_id_to_added_node_mapping[relation["pushout"]]
                    if relation["direction"] == "pushout_to_context":
                        gluing_node.relation_to.connect(context_node, relation["properties"])
                    elif relation["direction"] == "context_to_pushout":
                        context_node.relation_to.connect(gluing_node, relation["properties"])


        # Semantic patch
        for unique_path in self.semantic_patch_pattern.keys():
            node = self.find_node_from_unique_path(unique_path=unique_path, timestamp=timestamp_init)

            # setattr(node, "timestamp", timestamp_updt)

            for attr in self.semantic_patch_pattern[unique_path].keys():
                setattr(node, attr, self.semantic_patch_pattern[unique_path][attr][timestamp_updt])
                node.save()