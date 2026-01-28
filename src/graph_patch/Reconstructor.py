from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, SecondaryNode, InlineNode, RelProperties
import json
import os
from data_handler.DataHandler import DataHandler

class Reconstructor:

    # node_ids_to_unique_paths_mapping = {}
    # init_side_node_ids_to_unique_paths_mapping = {} #includes pushout nodes in path, used to identify non-danlging pushout nodes to delete

    # topological_patch_pattern = {}
    # semantic_patch_pattern = {}
    # nodes_to_delete = []

    ########################
    ### Helper Functions ###
    ########################

    def load_patch_from_file(self, path_topo, path_sema):
        """
        To apply a patch to a model, the previously created json-based patch files have to be loaded.
        """
        with open(path_sema, "r") as f:
            self.semantic_patch_pattern = json.load(f)
        with open(path_topo, "r") as f:
            self.topological_patch_pattern = json.load(f)
    
    def load_patch_from_file_topo(self, path_topo):
        """
        To apply a patch to a model, the previously created json-based patch files have to be loaded.
        """
      
        with open(path_topo, "r") as f:
            self.topological_patch_pattern = json.load(f)


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
            for contestant in latest_node.relation_to.match(rel_type=path[i]["rel_type"], list_index=path[i]["list_index"]):
                if contestant.EntityType == path[i]["EntityType"]:
                    latest_node = contestant
            i += 1
        return latest_node
    
    
    def recreate_graph_from_patch_topo(self, timestamp, init):
        if init == True:
            timestamp_attribute = "deleted"
        else:
            timestamp_attribute = "added"
        pushout_node_refs = self.topological_patch_pattern[timestamp]
        pushout_node_id_to_added_node_mapping = {}
        added_node_id_to_pushout_id_mapping = {}
        for key, pushout_node_ref in pushout_node_refs.items():
            node_class = globals()[pushout_node_ref["node_type"]]
            node_obj = node_class(**pushout_node_ref["properties"])
            delattr(node_obj, "element_id_property")
            setattr(node_obj, "timestamp", timestamp_attribute)
            print(node_obj)
            node_obj.save()
            pushout_node_id_to_added_node_mapping[pushout_node_ref["properties"]["element_id_property"]] = node_obj
            added_node_id_to_pushout_id_mapping[node_obj.element_id] = pushout_node_id_to_added_node_mapping[pushout_node_ref["properties"]["element_id_property"]]
        # Second iteration to connect the new updt nodes with one another and with the context
        for key_pushout, pushout_node_ref in pushout_node_refs.items():
            pushout_node = pushout_node_id_to_added_node_mapping[key_pushout]
            if pushout_node_ref["relation_to"]:
                for key_relation, relation in pushout_node_ref["relation_to"].items():
                    related_node = pushout_node_id_to_added_node_mapping[key_relation]
                    pushout_node.relation_to.connect(related_node, {"rel_type": relation["properties"]["rel_type"], "list_index": relation["properties"]["list_index"]})
                    if hasattr(pushout_node, relation["properties"]["rel_type"]):
                        setattr(pushout_node, relation["properties"]["rel_type"], None)
                        print(pushout_node)
                        pushout_node.save()
            if pushout_node_ref["context_to"]:
                for key_context_to, context_to in pushout_node_ref["context_to"].items():
                    context_node = self.find_node_from_unique_path(context_to["path"], timestamp)
                    setattr(context_node, "timestamp", "mcs")
                    context_node.save()
                    pushout_node.relation_to.connect(context_node, {"rel_type": "Glue", "list_index": context_to["properties"]["list_index"]})
                    if hasattr(pushout_node, context_to["properties"]["rel_type"]):
                        setattr(pushout_node, context_to["properties"]["rel_type"], None)
                        pushout_node.save()
            if pushout_node_ref["context_from"]:
                for key_context_from, context_from in pushout_node_ref["context_from"].items():
                    context_node = self.find_node_from_unique_path(context_from["path"], timestamp)
                    setattr(context_node, "timestamp", "mcs")
                    context_node.save()
                    context_node.relation_to.connect(pushout_node, {"rel_type": "Glue", "list_index": context_from["properties"]["list_index"]})
                    if hasattr(context_node, context_from["properties"]["rel_type"]):
                        setattr(context_node, context_from["properties"]["rel_type"], None)
                        context_node.save()

    def recreate_graph_from_patch_topo_without_context(self, timestamp):
        pushout_node_refs = self.topological_patch_pattern[timestamp]
        pushout_node_id_to_added_node_mapping = {}
        added_node_id_to_pushout_id_mapping = {}
        for key, pushout_node_ref in pushout_node_refs.items():
            node_class = globals()[pushout_node_ref["node_type"]]
            node_obj = node_class(**pushout_node_ref["properties"])
            delattr(node_obj, "element_id_property")
            setattr(node_obj, "push_out", timestamp)
            setattr(node_obj, "reconstructed", True)
            print(node_obj)
            node_obj.save()
            pushout_node_id_to_added_node_mapping[pushout_node_ref["properties"]["element_id_property"]] = node_obj
            added_node_id_to_pushout_id_mapping[node_obj.element_id] = pushout_node_id_to_added_node_mapping[pushout_node_ref["properties"]["element_id_property"]]
        # Second iteration to connect the new updt nodes with one another and with the context
        for key_pushout, pushout_node_ref in pushout_node_refs.items():
            pushout_node = pushout_node_id_to_added_node_mapping[key_pushout]
            if pushout_node_ref["relation_to"]:
                for key_relation, relation in pushout_node_ref["relation_to"].items():
                    related_node = pushout_node_id_to_added_node_mapping[key_relation]
                    pushout_node.relation_to.connect(related_node, {"rel_type": relation["properties"]["rel_type"], "list_index": relation["properties"]["list_index"]})
                    if hasattr(pushout_node, relation["properties"]["rel_type"]):
                        setattr(pushout_node, relation["properties"]["rel_type"], None)
                        setattr(pushout_node, "reconstructed", True)
                        print(pushout_node)
                        pushout_node.save()
            
            
                    

    


    ######################
    ### Main Functions ###
    ######################
    
    def reconstruct_patch(self, project_id: str, timestamp_init: str, timestamp_updt: str):
        self.node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.init_side_node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.topological_patch_pattern = {timestamp_init: {}, timestamp_updt: {}}
        self.semantic_patch_pattern = {}
        self.nodes_to_delete = []

        try:
            path_topo = f"./patch_data/Patch_Topo_{project_id}_{timestamp_init}_{timestamp_updt}.json"
            path_sema = f"./patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json"
            self.load_patch_from_file(path_topo, path_sema)
        except:
            path_topo = f"./patch_data/Patch_Topo_{project_id}_{timestamp_updt}_{timestamp_init}.json"
            path_sema = f"./patch_data/Patch_Sema_{project_id}_{timestamp_updt}_{timestamp_init}.json"
            self.load_patch_from_file(path_topo, path_sema)

        self.recreate_graph_from_patch_topo(timestamp_init, init= True)
        self.recreate_graph_from_patch_topo(timestamp_updt, init= False)

    

    def reconstruct_patch_without_context(self, path_topo: str, timestamp_init: str, timestamp_updt: str):

        self.node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.init_side_node_ids_to_unique_paths_mapping = {timestamp_init: {}, timestamp_updt: {}}
        self.topological_patch_pattern = {timestamp_init: {}, timestamp_updt: {}}
        self.semantic_patch_pattern = {}
        self.nodes_to_delete = []

        self.load_patch_from_file_topo(path_topo)

        self.recreate_graph_from_patch_topo_without_context(timestamp_init)
        self.recreate_graph_from_patch_topo_without_context(timestamp_updt)


    
        