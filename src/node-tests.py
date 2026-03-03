
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape

class GeometricHelper:
    
    def get_coordinates_Ifc_poly_line(self, poly_line):
        points = poly_line.Points
        points_coordinates = []
        for p in points:
            points_coordinates.append(p.Coordinates)
        return points
    
    
    def get_geometry_Ifc_Boolean_Clipping_Result(self, item):
        #### NOT DONE YET!
        geometry_info = {}
        operator = item.Operator
        first_operand = item.FirstOperand ## either IfcSweptAreaSolid OR IfcBooleanClippingResult
        ### NEEDS TO BE RECURSIVE
        second_operand = item.SecondOperand ## IfcHalfSpaceSolid

    def get_coordinates_Ifc_polygon(self, polygon):
        points_coordinates = []
        for p in polygon:
            points_coordinates.append(p.Coordinates)
        return points_coordinates
    
    def get_IfcBBox(self, item):
        bbox = item
        geo_representation = {
            "corner_coordinates": bbox.Corner.Coordinates,
            "x_dim": bbox.XDim,
            "y_dim": bbox.YDim,
            "z_dim": bbox.ZDim
        }
        return geo_representation
    
    def get_IfcGeometric_Curve_Set(self, item):
        elements = item.Elements # Set of IfcGeometricSetSelected (Points, Curves, Surfaces)
        geometric_info = {}
        for i,element in enumerate(elements):
            if element.is_a("IfcPolyline"):
                coordinates = self.get_coordinates_Ifc_poly_line(element)
                geometric_info[str(i)] = coordinates
            else:
                ## TO DO: implement differentt cases
                return None
        return geometric_info
        
    def get_geometry_Ifc_Polygonal_Face_Set(self, item):
        geometry_info = {
            "closed": item.Closed
        }
        faces = item.Faces
        face_coord_list = []
        for f in faces:
            face_coord_list.append(f.CoordIndex)
        geometry_info["faces"] = face_coord_list
        geometry_info["pn_index"] = item.PnIndex
        return geometry_info
            
    def get_geometry_IfcExtruded_Area_Solid(self, item):
        ### -> RepresentationType = Extruded Area -> [1,0]
        geometry_info = {
            "geometricRepresentation": [1,0],
            "direction": item.ExtrudedDirection.DirectionRatios,
            "depth": round(item.Depth,3)
        }
        sweptArea = item.SweptArea
        if sweptArea.is_a("IfcRectangleProfileDef"):
            geometry_info["swept_area"] = "IfcRectangleProfileDef"
            geometry_info.update(self.compute_profile_features_rectangle(sweptArea.XDim,sweptArea.YDim ))
            return geometry_info
        elif sweptArea.is_a("IfcArbitraryClosedProfileDef"):
            geometry_info["swept_area"] = "IfcArbitraryClosedProfileDef"
            outer_curve = sweptArea.OuterCurve ### IfcPolyline
            if outer_curve.is_a("IfcPolyline"):
                coordinates = self.get_coordinates_Ifc_poly_line(outer_curve)
            elif outer_curve.is_a("IfcIndexedPolyCurve"):
                coordinates = self.get_coordinates_Ifc_Indexed_Poly_Curve(outer_curve)
            else:
                print(f"not yet handled curve: {outer_curve}")
                return None
            geometry_info.update(self.compute_profile_features(coordinates))
            return geometry_info
        else:
         ## TO BE IMPLEMENTED
            return None
        
    def get_geometry_IfcFacetedBrep(self, item):
        geometry_info = {}
        outer = item.Outer #IfcClosedShell
        cfsFaces = outer.CfsFaces #CfsFaces -> set of IfcFaces
        for i,face in enumerate(cfsFaces):
            bounds = face.Bounds #IfcBound -> Boundris of the face
            face_bounds = []
            for bound in bounds:
                orientation = bound.Orientation #Orientation of bound, True or False
                actual_bound = bound.Bound ## for facetedBrep always Polyloop (Polygon defined by Points)
                polygon_coordinates = self.get_coordinates_Ifc_polygon(actual_bound.Polygon)
                face_bound = {
                    "orientation": orientation,
                    "polygon_coordinates": polygon_coordinates
                }
                face_bounds.append(face_bound)
                            #print(f"      Polygon: {polygon_coordinates}")
                            #print(f"      Orientation: {orientation}")
            geometry_info[str(i)]=face_bounds
        return geometry_info
    
    def get_coordinates_Ifc_Indexed_Poly_Curve(self, outer_curve):
         ### not done yet
        points = outer_curve.Points.CoordList
        ### if segments == None -> the poly curve is a line
        segments = outer_curve.Segments
        if segments == None: 
            coords = [(round(p[0], 3), round(p[1], 3)) for p in points]
            if coords[0] == coords[-1]:
                coords = coords[:-1]  # remove closing duplicate
            return coords
        else:
            return None
                
    def compute_profile_features_rectangle(self, x_dim, y_dim):
        area = x_dim * y_dim
        perimeter = 2 * (x_dim + y_dim)
        return {
            "bbox_x": x_dim,
            "bbox_y": y_dim,
            "area": area,
            "perimeter": perimeter,
            "num_vertices": 4,
            "compactness": (4 * 3.14159265 * area) / perimeter**2,
        }
        

    def compute_profile_features(self, coords: list[tuple]) -> dict:
        n = len(coords)
    
        # Bounding box — works with negative coords naturally
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        bbox_x = max(xs) - min(xs)
        bbox_y = max(ys) - min(ys)
    
        # Area — Shoelace formula, sign-independent
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        area = abs(area) / 2.0
    
        # Perimeter
        perimeter = 0.0
        for i in range(n):
            j = (i + 1) % n
            dx = coords[j][0] - coords[i][0]
            dy = coords[j][1] - coords[i][1]
            perimeter += (dx**2 + dy**2) ** 0.5
    
        # Compactness (isoperimetric quotient, 1.0 = perfect circle)
        compactness = (4 * 3.14159265 * area / perimeter**2) if perimeter > 0 else 0.0
    
        return {
            "bbox_x": bbox_x,
            "bbox_y": bbox_y,
            "area": area,
            "perimeter": perimeter,
            "num_vertices": n,
            "compactness": compactness,
        }
    

#geo_repr = model.by_type("IfcProfilDef")


def process_body_representations(item):
    helper = GeometricHelper()
    geometric_rep = {}
    if item.is_a("IfcFacetedBrep"):
        geometric_rep = helper.get_geometry_IfcFacetedBrep(item)
    elif item.is_a("IfcExtrudedAreaSolid"):
        geometric_rep = helper.get_geometry_IfcExtruded_Area_Solid(item)
        print(geometric_rep)
    elif item.is_a("IfcPolygonalFaceSet"):
        geometric_rep = helper.get_geometry_Ifc_Polygonal_Face_Set(item)
    else:
        print(f"Body representation Not yet implemented: {item}")
        return None
    return geometric_rep

def process_footprint_representation(item):
    helper = GeometricHelper()
    info = {}
    if item.is_a("IfcPolyline"):
        info = helper.get_coordinates_poly_line(item)
    elif item.is_a("IfcIndexedPolyCurve"):
        info = helper.get_coordinates_Ifc_Indexed_Poly_Curve(item)   
    elif item.is_a("IfcGeometricCurveSet"):
        info = helper.get_IfcGeometric_Curve_Set(item)
    else: 
        print(f"footprint representation not yet implement: {item} ") 
        return None
    return info
    
def process_ifc_entity_for_geometries(entity):
    helper = GeometricHelper()
    if hasattr(entity, "Representation") and entity.Representation is not None:
        entity_geo = {}
        ## IFC Product Representation (-> IfcTopologyRepresentation/ IfcShapeRepresentation)
        rep = entity.Representation
        
        ## IfcShapeRepresentation
        representation = entity.Representation.Representations
        
        geo_infos = []
        for i,rep in enumerate(representation):
        ## IfcShapeRepresentaion - Type
            repType = rep.RepresentationType
        
        ## IfcShapeRepresentaion - Identifier
            repIdentifier = rep.RepresentationIdentifier ### Body, Footprint
        
        ## IfcShapeRepresentation - IfcRepresentationItems
            repItems = rep.Items
            
            for item in repItems:
                
                if repIdentifier == "Body":
                    if repType == "MappedRepresentation":
                        mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                        for i in mapped_representation_items:
                            geo_info = process_body_representations(i)
                            geo_infos.append(geo_info)
                    else:
                        geo_info = process_body_representations(item)
                        p21_id = item.id()
                        geo_infos.append(geo_info)  
                elif repIdentifier == "FootPrint":            
                    if repType == "MappedRepresentation":
                        mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                        for i in mapped_representation_items:
                            geo_info = process_footprint_representation(i)
                            geo_infos.append(geo_info)
                    else:
                        geo_info = process_footprint_representation(item)
                        geo_infos.append(geo_info)  
                else:
                    print(f"    not recoginzed Items:   {item}")
        entity_geo[repIdentifier] = geo_infos         
        
        
        
        
from neomodel import db
import ifcopenshell
import ifcopenshell.api.project
from ifc_graph_interface.neo4j_helper import Neo4J_Helper
import json
import ast

from neo4j_core.neo4j_model import GenericNode, GenericGeoNode, PrimaryNode, ConnectionNode,GeoNode

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
        prim_conn_entities = primary_entities 

        prim_conn_ids = {e.id() for e in prim_conn_entities}
        ## get all material/ placement related resources
        secondary_entities = model.by_type("IfcMaterialDefinition") + model.by_type("IfcObjectPlacement")
        ## with localization: + model.by_type("IfcObjectPlacement")
        #secondary_entities = [e for e in model if e.id() != 0 and e.id() not in prim_conn_ids]
        with open("src/ifc_schema/ifc_entity_index.json") as f:
            entity_encodings = json.load(f)


        # Create a list of node dicts that can be used for batch creation with UNWIND.
        geo_nodes = []
        primary_nodes = []
        geo_relationships = []
        geo_count = 0
        for e in primary_entities:
            
            node = {
                "GlobalId": e.GlobalId,
                "EntityType": e.is_a(),
                "p21_id": f"#{e.id()}",
                "timestamp": timestamp,
                "entity_type_index": entity_encodings.get(e.is_a(), -1)
            }
            geo_count+=1
            self.createGeoNodes(e, geo_nodes, geo_relationships, geo_count, timestamp)
            primary_nodes.append(node)

      


        # Bulk creation queries.
        query_primary_nodes = """
        UNWIND $batch AS props
        CREATE (n:PrimaryNode:GenericNode:Node)
        SET n = props
        """

        
        query_geo_nodes = """
        UNWIND $batch AS props
        CREATE (n:GeoNode:GenericGeoNode)
        SET n = props
        """

        # Bulk creation.
        print(f"Creating {len(primary_nodes)} PrimaryNodes.")
        neo4j_helper.bulk_cypher_query(query_primary_nodes, primary_nodes, batch_size)
        
        print(f"Creating {len(geo_nodes)} GeoNodes")
        neo4j_helper.bulk_cypher_query(query_geo_nodes, geo_nodes, batch_size)

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
        print(f"Creating {len(relationships)} relationships.")
        query_geo_relationships = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.source_p21_id, timestamp: r.timestamp})
        MATCH (b:GenericGeoNode {p21_id: r.target_p21_id, timestamp: r.timestamp})
        CREATE (a)-[:GEO_RELATION_TO {rel_type: r.rel_type}]->(b)   
        """
        neo4j_helper.bulk_cypher_query(query_geo_relationships, geo_relationships, batch_size)


        print("Finished IFC parsing.")
        
        

   
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
                "bb_min_y": round(float(bb_min[1]),3),
                "bb_min_z": round(float(bb_min[2]),3),
                "bb_max_x": round(float(bb_max[0]),3),
                "bb_max_y": round(float(bb_max[1]),3),
                "bb_max_z": round(float(bb_max[2]),3)
            }
    
            return bbox
        except:
            print(f"Shape failed for {entity.is_a()} #{entity.id()}")
            return None
        
    def sanitize_for_neo4j(self, d: dict) -> dict:
        result = {}
        for k, v in d.items():
            str_key = str(k)
            if isinstance(v, (list, tuple)):
                result[str_key] = str(v)  # or json.dumps(v)
            elif isinstance(v, dict):
                result[str_key] = str(v)
            elif v is None:
                result[str_key] = "$"
            else:
                result[str_key] = v
        return result
    
    def sanitize_for_neo4j_test(self, d: dict) -> dict:
        result = {}
        for k, v in d.items():
            str_key = str(k)
            if isinstance(v, (list, tuple)):
                print() # or json.dumps(v)
            elif isinstance(v, dict):
                print()
            elif v is None:
                result[str_key] = "$"
            else:
                result[str_key] = v
        return result
        
    def process_body_representations(self, item):
        helper = GeometricHelper()
        geometric_rep = {}
        if item.is_a("IfcFacetedBrep"):
            geometric_rep = helper.get_geometry_IfcFacetedBrep(item)
        elif item.is_a("IfcExtrudedAreaSolid"):
            geometric_rep = helper.get_geometry_IfcExtruded_Area_Solid(item)
        elif item.is_a("IfcPolygonalFaceSet"):
            geometric_rep = helper.get_geometry_Ifc_Polygonal_Face_Set(item)
        else:
            print(f"Body representation Not yet implemented: {item}")
            return None
        return geometric_rep

    def process_footprint_representation(self, item):
        helper = GeometricHelper()
        info = {}
        if item.is_a("IfcPolyline"):
            coords = helper.get_coordinates_poly_line(item)
            info = {"coordinates": str(coords)}
        elif item.is_a("IfcIndexedPolyCurve"):
            coords = helper.get_coordinates_Ifc_Indexed_Poly_Curve(item)
            info = {"coordinates": str(coords)}  
        elif item.is_a("IfcGeometricCurveSet"):
            info = helper.get_IfcGeometric_Curve_Set(item)
        else: 
            print(f"footprint representation not yet implement: {item} ") 
            return None
        return info
    
    def create_node_and_relationship(self, entity, item, geo_info, repIdentifier, timestamp, body):
        ## EntityType -> IfcEntity of GeometryRepresentation
        ## Representation Identifier -> rel_type
        if body:
            encoded_rep_type = [0,1,0]
        else:
            encoded_rep_type = [0,0,1]
        geo_node = {
                    "EntityType": item.is_a(),
                    "p21_id": f"#{item.id()}",
                    "timestamp": timestamp,
                    "encoded_representation_type" : encoded_rep_type
                }
        geo_node.update(self.sanitize_for_neo4j_test(geo_info))
        
        geo_relationship = {
                "source_p21_id": f"#{entity.id()}",
                "target_p21_id": f"#{item.id()}",
                "timestamp": timestamp,
                "rel_type": repIdentifier,
             }
        return geo_node, geo_relationship
    
        
    def process_ifc_entity_for_geometries(self,entity, geo_nodes, geo_relationships, timestamp):
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
            
                for item in repItems:
                
                    if repIdentifier == "Body":
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info = self.process_body_representations(i)
                                geo_node, geo_rel = self.create_node_and_relationship(entity,i, geo_info, repIdentifier, timestamp, True)
                                geo_nodes.append(geo_node)
                                geo_relationships.append(geo_rel)
                        else:
                            geo_info = self.process_body_representations(item)
                            geo_node, geo_rel = self.create_node_and_relationship(entity,item, geo_info, repIdentifier, timestamp, True)
                            geo_nodes.append(geo_node)
                            geo_relationships.append(geo_rel)
                    elif repIdentifier == "FootPrint":            
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info = self.process_footprint_representation(i)
                                geo_node, geo_rel = self.create_node_and_relationship(entity,i, geo_info, repIdentifier, timestamp, False)
                                geo_nodes.append(geo_node)
                                geo_relationships.append(geo_rel)
                        else:
                            geo_info = self.process_footprint_representation(item)
                            geo_node, geo_rel = self.create_node_and_relationship(entity,item, geo_info, repIdentifier, timestamp, False)
                            geo_nodes.append(geo_node)
                            geo_relationships.append(geo_rel)
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
                    "encoded_representation_type": [1,0,0] 
                }
                geo_node.update(geo)
                geo_nodes.append(geo_node)
                geo_relationships.append({
                        "source_p21_id": f"#{entity.id()}",
                        "target_p21_id": fake_p21_id,
                        "timestamp": timestamp,
                        "rel_type": "simple_geo_representation",
                    })
        self.process_ifc_entity_for_geometries(entity, geo_nodes, geo_relationships, timestamp)
        
        
from neo4j_core.neo4j_connection import Neo4jConnection
        
path_init = "src/01_sample_data/base-example-wall-ifc4.ifc"
timestamp_init = "init_moved_wall"
timestamp_updt = "updt_moved_wall"

graph_type = "moved_wall"

db = Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)
db.cypher_query("MATCH (n) DETACH DELETE n")

# Parse IFC to Graph
creation_neo4j_ifc_interface = IfcEncodedGraphInterface()
print(f"Parsing {path_init} with timestamp {timestamp_init}.")
creation_neo4j_ifc_interface.ifc_2_graph(path_init, timestamp=timestamp_init)
                      
        
        


