from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties, GenericGeoNode
import json
import os
from data_handler.DataHandler import DataHandler

class GraphPatchSimple:

    node_ids_to_unique_paths_mapping = {}
    init_side_node_ids_to_unique_paths_mapping = {} #includes pushout nodes in path, used to identify non-danlging pushout nodes to delete

    topological_patch_pattern = {}
    semantic_patch_pattern = {}
    nodes_to_delete = []

    ########################
    ### Helper Functions ###
    ########################

    def create_unique_path_mappings(self, node, timestamp, unique_path=None):
        """
        Starting from a Primary or ConnectionNode, create unique paths for every reachable node in the graph. These are used to identify nodes without GlobalIds across different versions of a model.
        """
        # Check if node already has an entry in the dictionaaries that map a node to a unique path and vice-versa.
        if node.element_id not in self.node_ids_to_unique_paths_mapping[timestamp]:
            # If the node is a PrimaryNode or a ConnectionNode, reset the path because this is the base for a unique path.
            if type(node) == PrimaryNode:
                unique_path = [{"primary_node": node.GlobalId}]
            if type(node) == ConnectionNode:
                unique_path = [{"connection_node": node.GlobalId}]
            # Create entries in the dicts for the node and its unique path.
            self.node_ids_to_unique_paths_mapping[timestamp][node.element_id] = DataHandler.path_to_string(unique_path)
            # Create a unique path to a child element and then recursively run the function until a leaf node is reached.
            for child in node.relation_to.all():
                if child.equivalent_to.all():
                    rel = node.relation_to.relationship(child)
                    if isinstance(child, GenericGeoNode):
                        new_path = unique_path + [{"rel_type": rel.rel_type, "EntityType": child.EntityType}]
                    else:
                        new_path = unique_path + [{"rel_type": rel.rel_type, "list_index": rel.list_index, "EntityType": child.EntityType}]
                    self.create_unique_path_mappings(child, timestamp, new_path)

    def create_init_side_unique_path_mappings(self, node, timestamp, unique_path=None):
        if node.element_id not in self.init_side_node_ids_to_unique_paths_mapping[timestamp]:
            # If the node is a PrimaryNode or a ConnectionNode, reset the path because this is the base for a unique path.
            if type(node) == PrimaryNode:
                unique_path = [{"primary_node": node.GlobalId}]
            if type(node) == ConnectionNode:
                unique_path = [{"connection_node": node.GlobalId}]
            # Create entries in the dicts for the node and its unique path.
            self.init_side_node_ids_to_unique_paths_mapping[timestamp][node.element_id] = DataHandler.path_to_string(unique_path)
            # Create a unique path to a child element and then recursively run the function until a leaf node is reached.
            for child in node.relation_to.all():
                rel = node.relation_to.relationship(child)
                new_path = unique_path + [{"rel_type": rel.rel_type, "list_index": rel.list_index, "EntityType": child.EntityType}]
                self.create_init_side_unique_path_mappings(child, timestamp, new_path)

    def find_node_from_unique_path(self, unique_path: str, timestamp):
        """
        Function translates a unique path str to a unique path to find a node by its unique path in the graph db.
        """
        path = DataHandler.string_to_path(unique_path)
        # Path can either start with a PrimaryNode or with a ConnectionNode. Retrieve that start node by its GlobalId to start the search.
        if "primary_node" in path[0]:
            start_node = PrimaryNode.nodes.get(timestamp=timestamp, GlobalId=path[0]["primary_node"])
        elif "connection_node" in path[0]:
            start_node = ConnectionNode.nodes.get(timestamp=timestamp, GlobalId=path[0]["connection_node"])
        latest_node = start_node
        # Traverse the graph using the unique path as a template to find the node in question.
        for i in range(1, len(path)):
            # A unique step in the unique path is defined by the relation type, the list index of the relation, and the entity type of the target node.
            match_kwargs = {"rel_type": path[i]["rel_type"]}
            if "list_index" in path[i]:
                match_kwargs["list_index"] = path[i]["list_index"]
            for contestant in latest_node.relation_to.match(**match_kwargs):
                if contestant.EntityType == path[i]["EntityType"]:
                    latest_node = contestant
            i += 1
            for contestant in latest_node.relation_to.match(rel_type=path[i]["rel_type"], list_index=path[i]["list_index"]):
                if contestant.EntityType == path[i]["EntityType"]:
                    latest_node = contestant
            i += 1
        return latest_node
    
    
    def create_semantic_patch_pattern(self, equivalent_nodes_init, timestamp_init, timestamp_updt):
        """
        Among the nodes that are deemed equivalent during the Diff, compare the attributes and note and differences.
        """
        for node_init in equivalent_nodes_init:
            # Find the corresponding equivalent node in the db.
            node_updt = node_init.equivalent_to.all()[0]
            unique_path = self.node_ids_to_unique_paths_mapping[timestamp_init][node_init.element_id]

            for property_key, property_value in node_init.__properties__.items():
                # Exclude checking for the attributes timestamp and node id, as these are supposed to be different..
                if property_key not in ["timestamp", "element_id_property"]:
                    # Compare the attribute values.
                    property_value_updt = node_updt.__properties__.get(property_key)
                    if property_value != property_value_updt:
                        if unique_path not in self.semantic_patch_pattern:
                            self.semantic_patch_pattern[unique_path] = {}
                        if property_value is None:
                            adjacent =  node_init.relation_to.match(rel_type=property_key)[0]
                            if adjacent.equivalent_to.all():
                                self.semantic_patch_pattern[unique_path][property_key] = {}
                                self.semantic_patch_pattern[unique_path][property_key][timestamp_init] = {
                                    "path": self.node_ids_to_unique_paths_mapping[timestamp_init][adjacent.element_id],
                                    "rel_type": property_key,
                                    "list_index": node_init.relation_to.relationship(adjacent).list_index
                                }
                                self.semantic_patch_pattern[unique_path][property_key][timestamp_updt] = property_value_updt
                            else:
                                continue
                        elif property_value_updt is None:
                            adjacent =  node_updt.relation_to.match(rel_type=property_key)[0]
                            if adjacent.equivalent_to.all():
                                self.semantic_patch_pattern[unique_path][property_key] = {}
                                self.semantic_patch_pattern[unique_path][property_key][timestamp_updt] = {
                                    "path": self.node_ids_to_unique_paths_mapping[timestamp_updt][adjacent.element_id],
                                    "rel_type": property_key,
                                    "list_index": node_updt.relation_to.relationship(adjacent).list_index
                                }
                                self.semantic_patch_pattern[unique_path][property_key][timestamp_init] = property_value
                            else:
                                continue
                        else:
                            self.semantic_patch_pattern[unique_path][property_key] = {}
                            self.semantic_patch_pattern[unique_path][property_key][timestamp_init] = property_value
                            self.semantic_patch_pattern[unique_path][property_key][timestamp_updt] = property_value_updt
                            
    def semantic_patch(self, equivalent_nodes_init, timestamp_init, timestamp_updt, semantic_patch):
        """
        Among the nodes that are deemed equivalent during the Diff, compare the attributes and note and differences in nodes. 
        """
        for node_init in equivalent_nodes_init:
            # Find the corresponding equivalent node in the db.
            node_updt = node_init.equivalent_to.all()[0]

            for property_key, property_value in node_init.__properties__.items():
                # Exclude checking for the attributes timestamp and node id, as these are supposed to be different..
                if property_key not in ["timestamp", "element_id_property"]:
                    # Compare the attribute values.
                    property_value_updt = node_updt.__properties__.get(property_key)
                    if property_value != property_value_updt:
                        setattr(node_init, "change_type", "modified")
                        setattr(node_init, "changed_value", property_key)
                        setattr(node_init, "old_value", property_value )
                        setattr(node_init, "new_value", property_value_updt )
                        pattern = {
                            "EntityType" : node_init.EntityType,
                            "changed_value": property_key,
                            "old_value": property_value,
                            "new_value": property_value_updt
                        }
                        semantic_patch.append(pattern)




   
    def load_patch_from_file(self, path_topo, path_sema):
        """
        To apply a patch to a model, the previously created json-based patch files have to be loaded.
        """
        with open(path_sema, "r") as f:
            self.semantic_patch_pattern = json.load(f)
        with open(path_topo, "r") as f:
            self.topological_patch_pattern = json.load(f)

    def load_semantic_patch_from_file(self,path_sema):
        """
        To apply a semantic patch to a model, the previously created json-based patch files have to be loaded.
        """
        with open(path_sema, "r") as f:
            self.semantic_patch_pattern = json.load(f)
       



    ######################
    ### Main Functions ###
    ######################
    
    def modify_semantic(self, project_id: str, timestamp_init:str, timestamp_updt:str):
        """
        Use the two models that have been diffed and create a semanicpatch.
        """
        semantic_patch_pattern= {}
        
        equivalent_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()

        self.semantic_patch(equivalent_nodes_init, timestamp_init, timestamp_updt, semantic_patch_pattern)
        with open(f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(semantic_patch_pattern, f, indent=4)
        path_semantic = f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json"
        return path_semantic

   
    def create_patch_semantic(self, project_id: str, timestamp_init:str, timestamp_updt:str):
        """
        Use the two models that have been diffed and create a semanicpatch.
        """
        self.node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.semantic_patch_pattern = {}

        # Get all Primary and Connection Nodes.
        prim_and_con_init = list(PrimaryNode.nodes.filter(timestamp=timestamp_init)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_init))
        prim_and_con_updt = list(PrimaryNode.nodes.filter(timestamp=timestamp_updt)) + list(ConnectionNode.nodes.filter(timestamp=timestamp_updt))

        # Create unique paths starting from all Primary and all Connection nodes.
        for node in prim_and_con_init:
            if node.equivalent_to.all():
                # This mapping is the universal one for both models to identify context nodes.
                self.create_unique_path_mappings(node, timestamp_init)
        for node in prim_and_con_updt:
            if node.equivalent_to.all():
                self.create_unique_path_mappings(node, timestamp_updt)

        equivalent_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()

        self.create_semantic_patch_pattern(equivalent_nodes_init, timestamp_init, timestamp_updt)
        with open(f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(self.semantic_patch_pattern, f, indent=4)
        path_semantic = f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json"
        return path_semantic


