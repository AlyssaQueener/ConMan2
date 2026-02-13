from neomodel import db
import ifcopenshell
import ifcopenshell.api.project
from .neo4j_helper import Neo4J_Helper
import json

import ast

from neo4j_core.neo4j_model import GenericNode, PrimaryNode, SecondaryNode, ConnectionNode, InlineNode

class IfcGraphInterfaceSimple:

    ########################
    ### Helper Functions ###
    ########################

    def process_ifc_attributes(self, entity:ifcopenshell.entity_instance, timestamp:str, props_map:dict, relationships:list, related_nodes:set, inline_patterns:list):
        p21_id = f"#{entity.id()}"

        # Recursively handle IFC attributes to catch primitives to nested lists.
        def traverse(key, val, list_index=0):
            if isinstance(val, ifcopenshell.entity_instance):
                # Case where attribute is single relation to other entity.
                if val.id() == 0:
                    inline_patterns.append({
                        "props": {
                            "EntityType": val.is_a(),
                            "wrappedValue": val.wrappedValue,
                            "timestamp": timestamp
                        },
                        "relation": {
                            "rel_type": key,
                            "list_index": list_index,
                            "source_p21_id": p21_id
                        }
                    })
                else:
                    related_p21_id = f"#{val.id()}"
                    relationships.append({
                        "source_p21_id": p21_id,
                        "target_p21_id": related_p21_id,
                        "timestamp": timestamp,
                        "rel_type": key,
                        "list_index": list_index
                    })
                    related_nodes.add(related_p21_id)
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
        primary_entities = model.by_type("IfcObjectDefinition") + model.by_type("IfcPropertyDefinition")
        connection_entities = model.by_type("IfcRelationship")
        prim_conn_entities = primary_entities + connection_entities

        prim_conn_ids = {e.id() for e in prim_conn_entities}
        secondary_entities = [e for e in model if e.id() != 0 and e.id() not in prim_conn_ids]
        with open("src/ifc_schema/ifc_entity_index.json") as f:
            entity_encodings = json.load(f)


        # Create a list of node dicts that can be used for batch creation with UNWIND.
        primary_nodes = []
        for e in primary_entities:
            node = {
                "GlobalId": e.GlobalId,
                "EntityType": e.is_a(),
                "p21_id": f"#{e.id()}",
                "timestamp": timestamp,
                "entity_type_index": entity_encodings.get(e.is_a(), -1)
            }
            geo = self.simple_geo_representation(e)
            if geo:
                node.update(geo)
            geo_2 = self.getGeometricRepresentation(e)
            if geo_2:
                node.update(geo_2)
            primary_nodes.append(node)

        connection_nodes = [{
            "GlobalId": e.GlobalId,
            "EntityType": e.is_a(),
            "p21_id": f"#{e.id()}",
            "timestamp": timestamp
        } for e in connection_entities]

        secondary_nodes = [{
            "EntityType": e.is_a(),
            "p21_id": f"#{e.id()}",
            "timestamp": timestamp
        } for e in secondary_entities]

        inline_patterns = []

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

        query_secondary_nodes = """
        UNWIND $batch AS props
        CREATE (n:SecondaryNode:GenericNode:Node)
        SET n = props
        """

        # Bulk creation.
        print(f"Creating {len(primary_nodes)} PrimaryNodes.")
        neo4j_helper.bulk_cypher_query(query_primary_nodes, primary_nodes, batch_size)

        print(f"Creating {len(connection_nodes)} ConnectionNodes.")
        neo4j_helper.bulk_cypher_query(query_connection_nodes, connection_nodes, batch_size)

        print(f"Creating {len(secondary_nodes)} SecondaryNodes")
        neo4j_helper.bulk_cypher_query(query_secondary_nodes, secondary_nodes, batch_size)

        # Process IFC attributes into collections for node attributes and relationships.
        print("Collecting attributes and relationships.")
        props_map = {}
        relationships = []
        related_nodes = set()

        for entity in model:
            self.process_ifc_attributes(entity, timestamp, props_map, relationships, related_nodes, inline_patterns)

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

        # Bulk create InlinePatterns
        print(f"Creating {len(inline_patterns)} InlineNode patterns.")
        query_inline_patterns = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.relation.source_p21_id, timestamp: r.props.timestamp})
        CREATE (b:InlineNode:Node)
        SET b = r.props
        CREATE (a)-[:RELATION_TO {rel_type: r.relation.rel_type, list_index: r.relation.list_index}]->(b)
        """
        neo4j_helper.bulk_cypher_query(query_inline_patterns, inline_patterns, batch_size)

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
        
    @staticmethod
    def simple_geo_representation(entity):
        if not hasattr(entity, "Representation") or entity.Representation is None:
            return None
        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True) 
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
        centroid = grouped_verts.mean(axis=0)
    
        rep = {
            "bb_min_x": round(float(bb_min[0]),3),
            "bb_min_y": round(float(bb_min[1]),3),
            "bb_min_z": round(float(bb_min[2]),3),
            "bb_max_x": round(float(bb_max[0]),3),
            "bb_max_y": round(float(bb_max[1]),3),
            "bb_max_z": round(float(bb_max[2]),3),
            "centroid_x": round(float(centroid[0]),3),
            "centroid_y": round(float(centroid[1]),3),
            "centroid_z": round(float(centroid[2]),3),
            "geometry_id": shape.geometry.id
        }
    
        return rep

    @staticmethod
    def getGeometricRepresentation_test(entity):
        if hasattr(entity, "Representation") and entity.Representation is not None:
            product_shape = entity.Representation  # IfcProductDefinitionShape
            for shape_rep in product_shape.Representations:
                print(f"  RepresentationIdentifier: {shape_rep.RepresentationIdentifier}")  # 'Body', 'Axis', etc.
                print(f"  RepresentationType: {shape_rep.RepresentationType}")  # 'SweptSolid', 'Brep', etc.
                print(f"  Items: {shape_rep.Items}")
                for item in shape_rep.Items:
                    print(f"    Item type: {item.is_a()}")
                    # Now you can access geometry-specific attributes depending on type
                    if item.is_a("IfcExtrudedAreaSolid"):
                        print(f"    Depth: {item.Depth}")
                        print(f"    Profile: {item.SweptArea}")
                    elif item.is_a("IfcMappedItem"):
                        print(f"    MappingSource: {item.MappingSource}")
                        print(f"    Mapping Source Representation: {item.MappingSource.MappedRepresentation}")
                        print(f"    Mapping Source Representation: {item.MappingSource.MappedRepresentation.Items}")
                    elif item.is_a("IfcFacetedBrep"):
                        print(f"    Outer: {item.Outer}")
                    else:
                        print(f"     item with different geometry")
                    
    @staticmethod
    def getGeometricRepresentation(entity):
        if hasattr(entity, "Representation") and entity.Representation is not None:
            product_shape = entity.Representation  # IfcProductDefinitionShape
            for shape_rep in product_shape.Representations:
                #print(f"  RepresentationIdentifier: {shape_rep.RepresentationIdentifier}")  # 'Body', 'Axis', etc.
                #print(f"  RepresentationType: {shape_rep.RepresentationType}")  # 'SweptSolid', 'Brep', etc.
                #print(f"  Items: {shape_rep.Items}")
                if shape_rep.RepresentationIdentifier == "Body":
                    for item in shape_rep.Items:
                        print(f"    Item type: {item.is_a()}")
                        geometric_type = {
                            "IfcGeometry": item.is_a()
                        }
                        # Now you can access geometry-specific attributes depending on type
                        if item.is_a("IfcMappedItem"):
                            representation_type_mapped_item = item.MappingSource.MappedRepresentation
                            geometric_string = f"Mapped Item - {representation_type_mapped_item}"
                            geometric_type = {
                            "IfcGeometry": geometric_string
                            }
            return geometric_type
        return None
                   