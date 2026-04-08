from neo4j_core.neo4j_model import Node, GenericNode, PrimaryNode, ConnectionNode, RelProperties, GenericGeoNode, GeoRelProperties
import json
import os
from data_handler.DataHandler import DataHandler

class GraphPatchSimple:



    ########################
    ### Helper Functions ###
    ########################
    
        

                            
    def calculate_modifications_for_geo_node(self, node_init, node_updt, semantic_patch_pattern):
        geo_node_entity = node_init.EntityType

        # Delta properties per entity type
        DELTA_PROPERTIES = {
            "IfcExtrudedAreaSolid": {
                "depth":        "delta_depth",
                "length":       "delta_length",
                "width":       "delta_width",
                "area":         "delta_area",
                "volume":       "delta_volume",
                "compactness":  "delta_compactness"
            },
            "IfcIndexedPolyCurve": {
               "length":       "delta_length",
                "width":       "delta_width",
                "area":         "delta_area",
                "compactness":  "delta_compactness"
            },
            "IfcPolygonalFaceSet": {
                "max_face_area": "delta_max_face_area",
                "min_face_area": "delta_min_face_area",
                "n_faces": "delta_n_faces",
                "total_surface_area": "delta_total_surface_area",
                "width": "delta_width",
                "height": "delta_height",
                "volume": "delta_volume",
                "length":   "delta_length"
            },
            "IfcFacetedBrep": {
                "direction":    "delta_direction",
                "depth":        "delta_depth",
                "bbox_x":       "delta_bbox_x",
                "bbox_y":       "delta_bbox_y",
                "area":         "delta_area",
                "perimeter":    "delta_perimeter",
                "num_vertices": "delta_num_vertices",
                "compactness":  "delta_compactness",
            },
            "SimpleBBox": {
                "bb_min_x": "delta_bb_min_x",
                "bb_min_y": "delta_bb_min_y",
                "bb_min_z": "delta_bb_min_z",
                "bb_max_x": "delta_bb_max_x",
                "bb_max_y": "delta_bb_max_y",
                "bb_max_z": "delta_bb_max_z",
            },
        }

        EXCLUDED_KEYS = {"timestamp", "element_id_property", "p21_id"}
        change_pattern = []

        entity_delta_map = DELTA_PROPERTIES.get(geo_node_entity, {})
        has_changes = False

        for property_key, property_value in node_init.__properties__.items():
            if property_key in EXCLUDED_KEYS:
                continue
            

            property_value_updt = node_updt.__properties__.get(property_key)

            if property_value != property_value_updt:
                has_changes = True
                pattern = {
                            "EntityType" : node_init.EntityType,
                            "changed_value": property_key,
                            "old_value": property_value,
                            "new_value": property_value_updt
                        }
                semantic_patch_pattern.append(pattern)

                if property_key in entity_delta_map:
                    try:
                        delta = round((float(property_value_updt) - float(property_value)), 3)
                        setattr(node_init, entity_delta_map[property_key], delta)
                    except (TypeError, ValueError):
                        print("Delta calculation failed")

        if has_changes:
            entity_node = node_init.relation_geo.all()[0]
            if entity_node:
                setattr(entity_node, "geo_modification", 1.0)
                setattr(entity_node, "change_type", "modified")
                entity_node.save()
            setattr(node_init, "change_type", "modified")
            node_init.save()
        
                            
    def semantic_patch(self, equivalent_nodes_init, semantic_patch):
        """
        Among the nodes that are deemed equivalent during the Diff, compare the attributes and note and differences in nodes. 
        """
        for node_init in equivalent_nodes_init:
            # Find the corresponding equivalent node in the db.
            node_updt = node_init.equivalent_to.all()[0]

            for property_key, property_value in node_init.__properties__.items():
                # Exclude checking for the attributes timestamp and node id, as these are supposed to be different..
                if property_key not in ["timestamp", "element_id_property", "p21_id"]:
                    # Compare the attribute values.
                    property_value_updt = node_updt.__properties__.get(property_key)
                    if property_value != property_value_updt:
                        setattr(node_init, "change_type", "modified")
                        setattr(node_init, "old_value", property_value )
                        setattr(node_init, "new_value", property_value_updt )
                        if property_key == "materials":
                            setattr(node_init, "delta_materials", 1.0)
                        if property_key == "material_count":
                            setattr(node_init, "delta_material_count", 1.0)
                        if property_key == "Name":
                            setattr(node_init, "name_change", 1.0)
                        node_init.save()
                        pattern = {
                            "EntityType" : node_init.EntityType,
                            "changed_value": property_key,
                            "old_value": property_value,
                            "new_value": property_value_updt
                        }
                        semantic_patch.append(pattern)

       



    ######################
    ### Main Functions ###
    ######################
    
    def modify_semantic(self, project_id: str, timestamp_init:str, timestamp_updt:str):
        """
        Use the two models that have been diffed and create a semanicpatch.
        """
        semantic_patch_pattern= []
        
        equivalent_nodes_init = Node.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()
        equivalent_geo_nodes_init = GenericGeoNode.nodes.filter(timestamp=timestamp_init).has(equivalent_to=True).all()

        self.semantic_patch(equivalent_nodes_init, semantic_patch_pattern)
        for node_init in equivalent_geo_nodes_init:
            # Find the corresponding equivalent node in the db.
            node_updt = node_init.equivalent_to.all()[0]
            self.calculate_modifications_for_geo_node(node_init, node_updt, semantic_patch_pattern)
        with open(f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json", "w") as f:
            json.dump(semantic_patch_pattern, f, indent=4)
        path_semantic = f"patch_data/Patch_Sema_{project_id}_{timestamp_init}_{timestamp_updt}.json"
        return path_semantic

   
   
   
  