from neomodel import db
import ifcopenshell
from .neo4j_helper import Neo4J_Helper
import json
from data_handler.GeometricHelper import GeometricHelper  # import the class from the module
import ifcopenshell.util.selector

from neo4j_core.neo4j_model import GenericNode, GenericGeoNode, PrimaryNode, ConnectionNode, SolidNode, LocationNode, SurfaceNode, BrepNode

class IfcEncodedGraphInterface:

    ########################
    ### Helper Functions ###
    ########################
    

    #### TO DO ###
    ### IDEA ####
    ### Process ifc attributes in a different way. only process
    ### whatever there is for geometric description /localization / 
    
    def process_ifc_attributes(self, entity:ifcopenshell.entity_instance, timestamp:str, props_map:dict, relationships:list, related_nodes:set, prim_conn_ids:list):
        p21_id = f"#{entity.id()}"


        # Recursively handle IFC attributes to catch primitives to nested lists.
        def traverse(key, val, list_index=0):
            if isinstance(val, ifcopenshell.entity_instance):
                # Instead of creating Inline Nodes i set these as attributes
                if val.id() in prim_conn_ids:
                    related_p21_id = f"#{val.id()}"
                    relationships.append({
                        "source_p21_id": p21_id,
                        "target_p21_id": related_p21_id,
                        "timestamp": timestamp,
                        "rel_type": key,
                        "list_index": list_index
                    })
                    related_nodes.add(related_p21_id)
                #if key=="RelativePlacement":
                    #if val.is_a("IfcAxis2Placement3D") or val.is_a("IfcAxis2Placement2D"):
                        #coordinates = val.Location.Coordinates if val.Location is not None else "$"
                        #direction = val.RefDirection.DirectionRatios if val.RefDirection is not None else "$"
                        #props_map.setdefault(p21_id, {})["relative placement - direction"] = direction
                        #props_map.setdefault(p21_id, {})["relative placement - coordinates"] = coordinates

                 
            elif isinstance(val, (tuple, list)):
                # Case where attribute is a list.
                if any(isinstance(x, ifcopenshell.entity_instance) for x in val):
                    # Case where list of IFC entities.
                    for i, x in enumerate(val):
                        traverse(key, x, list_index=i)
                else:
                    # Case where list of primtitves.
                    props_map.setdefault(p21_id, {})[key] = str(val)
            elif val is None:
                # Case where attribute is not assigned.
                props_map.setdefault(p21_id, {})[key] = "$"
            else:
                # Case where value is primitive.
                props_map.setdefault(p21_id, {})[key] = val
        if entity.id() in prim_conn_ids:
            info = entity.get_info()
            for key, val in info.items():
                # Ignore any IDs or types as they are already saved in the node and must not be changed
                if key in ("GlobalId", "EntityType", "type", "p21_id", "id", "inline_id", "timestamp"):
                    continue
                else:
                    traverse(key, val)

    ######################
    ### Main Functions ###
    ######################

    def ifc_2_graph(self, ifc_path:str, timestamp:str, batch_size:int = 20000):

        # Create Neo4J_Helper instance.
        neo4j_helper = Neo4J_Helper()

        # Create index for p21_id and timestamp for faster lookup.
        db.cypher_query("CREATE INDEX generic_p21_ts IF NOT EXISTS FOR (n:GenericNode) ON (n.p21_id, n.timestamp)")
        # Wait until the index is online.
        db.cypher_query("CALL db.awaitIndexes()")

        # Load IFC model.
        print("Loading IFC model.")
        model = ifcopenshell.open(ifc_path)

        # Retrieve IFC entities that will be PrimaryNodes, same for ConnectionNodes.
        #  + model.by_type("IfcPropertyDefinition")
        primary_entities = model.by_type("IfcObjectDefinition")
        connection_entities = model.by_type("IfcRelationship")
        prim_conn_entities = primary_entities + connection_entities

        prim_conn_ids = {e.id() for e in prim_conn_entities}
        ## get all material/ placement related resources
        secondary_entities = model.by_type("IfcMaterialDefinition") + model.by_type("IfcObjectPlacement")
        ## with localization: + model.by_type("IfcObjectPlacement")
        #secondary_entities = [e for e in model if e.id() != 0 and e.id() not in prim_conn_ids]
        with open("src/ifc_schema/ifc_entity_index.json") as f:
            entity_encodings = json.load(f)


        # Create a list of node dicts that can be used for batch creation with UNWIND.
        ## Location nodes
        geo_nodes = []
        geo_relationships = []
        geo_count = 0
        
        ## surface nodes
        surface_nodes = []
        surface_relationships = []
        
        ## extruded_solid nodes
        solid_nodes = []
        solid_relationships = []
        
        brep_nodes = []
        brep_relationships = []
        
        primary_nodes = []
        for e in primary_entities:
            
            node = {
                "GlobalId": e.GlobalId,
                "EntityType": e.is_a(),
                "p21_id": f"#{e.id()}",
                "timestamp": timestamp,
                "entity_type_index": float(entity_encodings.get(e.is_a(), -1)),
                "delta_materials": 0.0
            }
            material = self.getMaterial(e)
            if material:
                node.update({
                    "materials": material
                })
            geo_count+=1
            self.createGeoNodes(e, geo_nodes, geo_relationships, geo_count, timestamp)
            self.create_surface_and_solid_nodes(e, surface_nodes, solid_nodes, surface_relationships, solid_relationships, brep_nodes, brep_relationships, timestamp)
            primary_nodes.append(node)

        connection_nodes = []
        for e in connection_entities:
            if e.is_a("IfcRelDefinesByProperties"):
                continue
            else:
                node = {
                    "GlobalId": e.GlobalId,
                    "EntityType": e.is_a(),
                    "p21_id": f"#{e.id()}",
                    "timestamp": timestamp,
                    "entity_type_index": float(entity_encodings.get(e.is_a(), -1))
                }
                connection_nodes.append(node)
       

        #secondary_nodes = []
        #p21_ids_secondary_nodes = []
        #for e in secondary_entities:
            #sec_node = {
             #   "EntityType": e.is_a(),
              #  "p21_id": f"#{e.id()}",
               # "timestamp": timestamp
            #}
            #secondary_nodes.append(sec_node)
            #p21_ids_secondary_nodes.append(e.id())
      


        # Bulk creation queries.
        query_primary_nodes = """
        UNWIND $batch AS props
        CREATE (n:PrimaryNode:GenericNode:Node)
        SET n = props
        """

        query_connection_nodes = """
        UNWIND $batch AS props
        CREATE (n:ConnectionNode:GenericNode:Node)
        SET n = props
        """

        #query_secondary_nodes = """
        #UNWIND $batch AS props
        #CREATE (n:SecondaryNode:GenericNode:Node)
        #SET n = props
        #"""
        
        query_location_nodes = """
        UNWIND $batch AS props
        CREATE (n:LocationNode:GenericGeoNode)
        SET n = props
        """
        
        query_solid_nodes = """
        UNWIND $batch AS props
        CREATE (n:SolidNode:GenericGeoNode)
        SET n = props
        """
        
        query_brep_nodes = """
        UNWIND $batch AS props
        CREATE (n:BrepNode:GenericGeoNode)
        SET n = props
        """
        
        query_surface_nodes = """
        UNWIND $batch AS props
        CREATE (n:SurfaceNode:GenericGeoNode)
        SET n = props
        """

        # Bulk creation.
        print(f"Creating {len(primary_nodes)} PrimaryNodes.")
        neo4j_helper.bulk_cypher_query(query_primary_nodes, primary_nodes, batch_size)

        print(f"Creating {len(connection_nodes)} ConnectionNodes.")
        neo4j_helper.bulk_cypher_query(query_connection_nodes, connection_nodes, batch_size)

        #print(f"Creating {len(secondary_nodes)} SecondaryNodes")
        #neo4j_helper.bulk_cypher_query(query_secondary_nodes, secondary_nodes, batch_size)
        
        print(f"Creating {len(geo_nodes)} LocationNodes")
        neo4j_helper.bulk_cypher_query(query_location_nodes, geo_nodes, batch_size)
        
        print(f"Creating {len(surface_nodes)} SurfaceNodes")
        neo4j_helper.bulk_cypher_query(query_surface_nodes, surface_nodes, batch_size)
        
        print(f"Creating {len(solid_nodes)} SolidNodes")
        neo4j_helper.bulk_cypher_query(query_solid_nodes, solid_nodes, batch_size)
        
        print(f"Creating {len(solid_nodes)} BrepNodes")
        neo4j_helper.bulk_cypher_query(query_brep_nodes, brep_nodes, batch_size)

        # Process IFC attributes into collections for node attributes and relationships.
        print("Collecting attributes and relationships.")
        props_map = {}
        relationships = []
        related_nodes = set()

        for entity in model:
            #self.process_ifc_attributes(entity, timestamp, props_map, relationships, related_nodes, p21_ids_secondary_nodes, prim_conn_ids)
            self.process_ifc_attributes(entity, timestamp, props_map, relationships, related_nodes, prim_conn_ids)

        # Bulk update primitive attributes on nodes.
        print(f"Updating attributes on {len(props_map)} nodes.")
        attributes_list = [{"p21_id": p21_id, "timestamp": timestamp, "properties": properties} for p21_id, properties in props_map.items()]
        query_properties = """
        UNWIND $batch AS row
        MATCH (n:GenericNode {p21_id: row.p21_id, timestamp: row.timestamp})
        SET n += row.properties
        """
        neo4j_helper.bulk_cypher_query(query_properties, attributes_list, batch_size)

        # Bulk create relationships from IFC attributes.
        print(f"Creating {len(relationships)} relationships.")
        query_relationships = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.source_p21_id, timestamp: r.timestamp})
        MATCH (b:GenericNode {p21_id: r.target_p21_id, timestamp: r.timestamp})
        CREATE (a)-[:RELATION_TO {rel_type: r.rel_type, list_index: r.list_index}]->(b)   
        """
        neo4j_helper.bulk_cypher_query(query_relationships, relationships, batch_size)
        
        
        # Bulk create relationships from Geo relationsships
        print(f"Creating Location {len(geo_relationships)} relationships.")
        query_geo_relationships = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.source_p21_id, timestamp: r.timestamp})
        MATCH (b:GenericGeoNode {p21_id: r.target_p21_id, timestamp: r.timestamp})
        CREATE (a)-[:GEO_RELATION_TO {rel_type: r.rel_type}]->(b)   
        """
        
        print(f"Creating Location {len(geo_relationships)} relationships.")

        neo4j_helper.bulk_cypher_query(query_geo_relationships, geo_relationships, batch_size)
        
        # Bulk create relationships from Geo relationsships
        print(f"Creating solid {len(solid_relationships)} relationships.")
      
        neo4j_helper.bulk_cypher_query(query_geo_relationships, solid_relationships, batch_size)
        
        # Bulk create relationships from Geo relationsships
        print(f"Creating surface {len(surface_relationships)} relationships.")
        neo4j_helper.bulk_cypher_query(query_geo_relationships, surface_relationships, batch_size)
        
        print(f"Creating Breü {len(brep_relationships)} relationships.")
        neo4j_helper.bulk_cypher_query(query_geo_relationships, brep_relationships, batch_size)


        print("Finished IFC parsing.")
        
        

    def getMaterial(self, entity):
        try:
            material_count = ifcopenshell.util.selector.get_element_value(entity, "materials.count")
            materials = []
            if material_count == 0:
                return None
            elif material_count > 1:
                material_item_names = ifcopenshell.util.selector.get_element_value(entity, "material.item.Material.Name")
                for n in material_item_names:
                    materials.append(n)
            else:
                materials.append(ifcopenshell.util.selector.get_element_value(entity, "material.Name"))
            return materials
        except:
            return None
        
    @staticmethod
    def get_project_id_from_timestamp(timestamp: str):
        try:
            project = PrimaryNode.nodes.get(EntityType="IfcProject", timestamp=timestamp)
            return project.GlobalId
        except Exception as e:
            print(f"Error retrieving project ID for timestamp {timestamp}: {e}")
            return None
        
    @staticmethod
    def get_project_id_from_ifc_path(ifc_path: str):
        try:
            model = ifcopenshell.open(ifc_path)
            project = model.by_type("IfcProject")[0]
            return project.GlobalId
        except Exception as e:
            print(f"Error retrieving project ID from IFC file {ifc_path}: {e}")
            return None
    
    @staticmethod
    def get_timestamp_from_project_id(project_id: str):
        try:
            project = PrimaryNode.nodes.filter(GlobalId=project_id, EntityType="IfcProject").all()
            return [p.timestamp for p in project]
        except Exception as e:
            print(f"Error retrieving latest timestamp for project ID {project_id}: {e}")
            return None
        
    def simple_geo_representation(self, entity):
        if not hasattr(entity, "Representation") or entity.Representation is None:
            return None
        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)
        try: 
            shape = ifcopenshell.geom.create_shape(settings, entity)

        # 4x4 transformation matrix as numpy array
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
            location = matrix[:, 3][0:3]

        # Grouped vertices as [[x,y,z], [x,y,z], ...] — these are LOCAL coordinates
            grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

        # Derive compact geometry features
            bb_min = grouped_verts.min(axis=0)
            bb_max = grouped_verts.max(axis=0)
            #centroid = grouped_verts.mean(axis=0)
            
    
            bbox = {
                "bb_min_x": round(float(bb_min[0]),3),
                "delta_bb_min_x": 0.0,
                
                "bb_min_y": round(float(bb_min[1]),3),
                "delta_bb_min_y": 0.0,
                
                "bb_min_z": round(float(bb_min[2]),3),
                "delta_bb_min_z": 0.0,
                
                "bb_max_x": round(float(bb_max[0]),3),
                "delta_bb_max_x": 0.0,
                
                "bb_max_y": round(float(bb_max[1]),3),
                "delta_bb_max_y": 0.0,
                
                "bb_max_z": round(float(bb_max[2]),3),
                "delta_bb_max_z": 0.0
            }
    
            return bbox
        except:
            print(f"Shape failed for {entity.is_a()} #{entity.id()}")
            return None
        
    def sanitize_for_neo4j(self, d: dict) -> dict:
        if d is None:
            return None
        result = {}
        for k, v in d.items():
            str_key = str(k)
            if v is None:
                result[str_key] = "$"
            else:
                result[str_key] = v
        return result
        
    def process_body_representations(self, item):
        helper = GeometricHelper()
        geometric_rep = {}
        #if item.is_a("IfcFacetedBrep"):
            #geometric_rep = helper.get_geometry_IfcFacetedBrep(item)
        if item.is_a("IfcExtrudedAreaSolid"):
            geometric_rep = helper.get_geometry_IfcExtruded_Area_Solid(item)
            extruded = True
        elif item.is_a("IfcPolygonalFaceSet"):
            geometric_rep = helper.get_geometry_Ifc_Polygonal_Face_Set(item)
            extruded = False
        else:
            print(f"Body representation Not yet implemented: {item}")
            return None, None
        return geometric_rep, extruded

    def process_footprint_representation(self, item):
        helper = GeometricHelper()
        info = {}
        #if item.is_a("IfcPolyline"):

        if item.is_a("IfcIndexedPolyCurve"):
            coords = helper.get_coordinates_Ifc_Indexed_Poly_Curve(item)
            profile_features = helper.compute_profile_features(coords)
            info.update(profile_features)  
        #elif item.is_a("IfcGeometricCurveSet"):
            
        else: 
            print(f"footprint representation not yet implement: {item} ") 
            return None
        return info
    
    def create_node_and_relationship(self, entity, item, geo_info, repIdentifier, timestamp, item_r):
        ## EntityType -> IfcEntity of GeometryRepresentation
        ## Representation Identifier -> rel_type
        success = True
        sanitized_geo_info = self.sanitize_for_neo4j(geo_info)
        if sanitized_geo_info is None:
            return None, None, False
        geo_node = {
                    "EntityType": item.is_a(),
                    "p21_id": f"#{item.id()}",
                    "timestamp": timestamp,
                }
        geo_node.update(self.sanitize_for_neo4j(geo_info))
        
        geo_relationship = {
                "source_p21_id": f"#{entity.id()}",
                "target_p21_id": f"#{item.id()}",
                "timestamp": timestamp,
                "rel_type": repIdentifier,
                "list_index": item_r
             }
        return geo_node, geo_relationship, success
    
        
    def process_ifc_entity_for_geometries(self,entity, surface_nodes, solid_nodes, surface_relationships, solid_relationships,brep_nodes, brep_relationships, timestamp):
        if hasattr(entity, "Representation") and entity.Representation is not None:
            ## IFC Product Representation (-> IfcTopologyRepresentation/ IfcShapeRepresentation)
            rep = entity.Representation
        
            ## IfcShapeRepresentation
            representation = entity.Representation.Representations
        
            for i,rep in enumerate(representation):
            ## IfcShapeRepresentaion - Type
                repType = rep.RepresentationType
        
            ## IfcShapeRepresentaion - Identifier
                repIdentifier = rep.RepresentationIdentifier ### Body, Footprint
        
            ## IfcShapeRepresentation - IfcRepresentationItems
                repItems = rep.Items
                item_nr = 1
                for item in repItems:
                    
                
                    if repIdentifier == "Body":
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info, extruded = self.process_body_representations(i)
                                geo_node, geo_rel, success = self.create_node_and_relationship(entity,i, geo_info, repIdentifier, timestamp, item_nr)
                                if success: 
                                    geo_node.update({
                                        "rep_item_nr": item_nr
                                    })
                                    item_nr += 1
                                    solid_nodes.append(geo_node)
                                    solid_relationships.append(geo_rel)
                                else:
                                    continue
                        else:
                            geo_info, extruded = self.process_body_representations(item)
                            geo_node, geo_rel, success = self.create_node_and_relationship(entity,item, geo_info, repIdentifier, timestamp, True)
                            if success:
                                geo_node.update({
                                        "rep_item_nr": item_nr
                                    })
                                item_nr += 1
                                if extruded:
                                    solid_nodes.append(geo_node)
                                    solid_relationships.append(geo_rel)
                                else:
                                    brep_nodes.append(geo_node)
                                    brep_relationships.append(geo_rel)
                            else: continue
                    elif repIdentifier == "FootPrint":            
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info = self.process_footprint_representation(i)
                                geo_node, geo_rel,success = self.create_node_and_relationship(entity,i, geo_info, repIdentifier, timestamp, False)
                                if success:
                                    geo_node.update({
                                        "rep_item_nr": item_nr
                                    })
                                    item_nr += 1
                                    surface_nodes.append(geo_node)
                                    surface_relationships.append(geo_rel)
                                else: continue
                        else:
                            geo_info = self.process_footprint_representation(item)
                            geo_node, geo_rel, success = self.create_node_and_relationship(entity,item, geo_info, repIdentifier, timestamp, False)
                            if success:
                                geo_node.update({
                                    "rep_item_nr": item_nr
                                })
                                item_nr += 1
                                surface_nodes.append(geo_node)
                                surface_relationships.append(geo_rel)
                            else: continue
                    else:
                        print(f"    not recoginzed Items:   {item}")
        
        

    
    def createGeoNodes(self, entity, geo_nodes, geo_relationships, geo_count,timestamp):
        geo = self.simple_geo_representation(entity)
            
        if geo:
                fake_p21_id = f"geo{geo_count}" 
                geo_node = {
                    "EntityType": "SimpleBBox",
                    "p21_id": fake_p21_id,
                    "timestamp": timestamp,
                }
                geo_node.update(geo)
                geo_nodes.append(geo_node)
                geo_relationships.append({
                        "source_p21_id": f"#{entity.id()}",
                        "target_p21_id": fake_p21_id,
                        "timestamp": timestamp,
                        "rel_type": "world_location",
                        "list_index": fake_p21_id
                    })
                
    def create_surface_and_solid_nodes(self, entity, surface_nodes, solid_nodes, surface_relationships, solid_relationships, brep_nodes, brep_relationships, timestamp):
        self.process_ifc_entity_for_geometries(entity, surface_nodes, solid_nodes, surface_relationships, solid_relationships, brep_nodes, brep_relationships, timestamp)
                   