import json
class Clean_up:

    def remove_false_positive_changes(self, pushout_pattern_json):
        """
        Remove false positive additions/deletions by comparing structural signatures
        of nodes from initial (timestamp '0') and updated (timestamp '1') graphs.
        Nodes with identical structure (properties, relationships, context) except
        timestamp and element_id are considered equivalent and removed from the diff.
        
        @param pushout_pattern_json: Dict with keys "0" and "1" containing deleted and added nodes
        @return: Tuple of (cleaned_pattern, remaining_deleted_nodes, remaining_added_nodes)
        """
        
        def create_node_signature(node_data):
            """
            Create a structural signature for a node that ignores timestamp and element_id.
            """
            signature = {
                'EntityType': node_data['properties'].get('EntityType'),
                'node_type': node_data.get('node_type'),
                'p21_id': node_data['properties'].get('p21_id'),
                # Include all properties except timestamp and element_id_property
                'properties': {k: v for k, v in node_data['properties'].items() 
                            if k not in ['timestamp', 'element_id_property']},
                # Structural relationships (normalize by removing element_ids)
                'relation_to_structure': {},
                'context_to_structure': {},
                'context_from_structure': {}
            }
            
            # Add relationship structure (target node's p21_id and relationship properties)
            for target_id, rel_data in node_data.get('relation_to', {}).items():
                # We'll use a placeholder since we need to look up the target's p21_id
                rel_signature = (
                    rel_data['properties'].get('rel_type'),
                    rel_data['properties'].get('list_index')
                )
                signature['relation_to_structure'][rel_signature] = True
            
            # Add context structure
            for target_id, ctx_data in node_data.get('context_to', {}).items():
                ctx_signature = (
                    ctx_data.get('path', ''),
                    ctx_data['properties'].get('rel_type'),
                    ctx_data['properties'].get('list_index')
                )
                signature['context_to_structure'][ctx_signature] = True
                
            for target_id, ctx_data in node_data.get('context_from', {}).items():
                ctx_signature = (
                    ctx_data.get('path', ''),
                    ctx_data['properties'].get('rel_type'),
                    ctx_data['properties'].get('list_index')
                )
                signature['context_from_structure'][ctx_signature] = True
            
            return signature
        
        def signatures_match(sig1, sig2):
            """
            Check if two node signatures are equivalent.
            """
            # Compare basic properties
            if sig1['EntityType'] != sig2['EntityType']:
                return False
            if sig1['node_type'] != sig2['node_type']:
                return False
            if sig1['p21_id'] != sig2['p21_id']:
                return False
            if sig1['properties'] != sig2['properties']:
                return False
                
            # Compare structural relationships
            if sig1['relation_to_structure'] != sig2['relation_to_structure']:
                return False
            if sig1['context_to_structure'] != sig2['context_to_structure']:
                return False
            if sig1['context_from_structure'] != sig2['context_from_structure']:
                return False
                
            return True
        
        # Create signatures for all nodes in both timestamps
        deleted_nodes = pushout_pattern_json.get('0', {})
        added_nodes = pushout_pattern_json.get('1', {})
        
        deleted_signatures = {
            node_id: create_node_signature(node_data) 
            for node_id, node_data in deleted_nodes.items()
        }
        
        added_signatures = {
            node_id: create_node_signature(node_data) 
            for node_id, node_data in added_nodes.items()
        }
        
        # Find matching pairs
        nodes_to_remove_deleted = set()
        nodes_to_remove_added = set()
        
        for deleted_id, deleted_sig in deleted_signatures.items():
            for added_id, added_sig in added_signatures.items():
                if added_id in nodes_to_remove_added:
                    continue  # Already matched
                    
                if signatures_match(deleted_sig, added_sig):
                    nodes_to_remove_deleted.add(deleted_id)
                    nodes_to_remove_added.add(added_id)
                    print(f"Matched false positive: {deleted_sig['p21_id']} ({deleted_sig['EntityType']})")
                    break  # Move to next deleted node
        
        # Get remaining nodes with their complete data
        remaining_deleted_nodes = {k: v for k, v in deleted_nodes.items() if k not in nodes_to_remove_deleted}
        remaining_added_nodes = {k: v for k, v in added_nodes.items() if k not in nodes_to_remove_added}
        
        # Create cleaned output (same as remaining nodes)
        cleaned_pattern = {
            '0': remaining_deleted_nodes,
            '1': remaining_added_nodes
        }
        
        print(f"\nRemoved {len(nodes_to_remove_deleted)} false positive deletions")
        print(f"Removed {len(nodes_to_remove_added)} false positive additions")
        print(f"Remaining deletions: {len(remaining_deleted_nodes)}")
        print(f"Remaining additions: {len(remaining_added_nodes)}")
        
        return cleaned_pattern, remaining_deleted_nodes, remaining_added_nodes
    
   
        
    
    def clean_semantic(self, path, timestamp_init, timestamp_updt):
        with open(path, 'r') as f:
            data = json.load(f)
            filtered_data = {}

            for node_path, properties in data.items():
                filtered_properties = {}
                # properties is a dict like {"XDim": {"init_translation_slab": ..., "updt_translation_slab": ...}}
                for property_name, values in properties.items():
                    init_value = values[timestamp_init]
                    updt_value = values[timestamp_updt]
                    if isinstance(init_value, float) and isinstance(updt_value, float):
                        rounded_init = round(init_value,3)
                        rounded_updt = round(updt_value, 3)
                        if rounded_init != rounded_updt:
                            filtered_properties[property_name] = values
                    else:
                        filtered_properties[property_name] = values
                if filtered_properties:
                    filtered_data[node_path] = filtered_properties
            
            print(filtered_data)
            with open(f"patch_data/Cleaned_Patch_Sema_{timestamp_init}_{timestamp_updt}.json", "w") as f:
                json.dump(filtered_data, f, indent=4)
                path_semantic = f"patch_data/Cleaned_Patch_Sema_{timestamp_init}_{timestamp_updt}.json"
                return path_semantic




