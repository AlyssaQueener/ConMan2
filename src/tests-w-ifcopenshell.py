
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
ifc_path = "src/01_sampleData/basic-geometric-changes/base-w-wall-2x3.ifc"
ifc_path_2 = "src/01_sampleData/basic-geometric-changes/translated-wall.ifc"
model = ifcopenshell.open(ifc_path)
# Retrieve IFC entities that will be PrimaryNodes, same for ConnectionNodes.
primary_entities = model.by_type("IfcObjectDefinition") + model.by_type("IfcPropertyDefinition")
connection_entities = model.by_type("IfcRelationship")


def get_combined_geo_representation(entity):
    simple_geo_rep = simple_geo_representation(entity)
    geo_rep_ifc = getGeometricRepresentation(entity)
    if geo_rep_ifc is None or simple_geo_rep == None:
        return None
    combined_geo_rep = {
        "GeometryRepIfc": geo_rep_ifc,
        "BrepGeometry": simple_geo_rep
    }
    return combined_geo_rep
def simple_geo_representation(entity):
    if not hasattr(entity, "Representation") or entity.Representation is None:
        return None
    settings = ifcopenshell.geom.settings()
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
        "bb_min_x": float(bb_min[0]),
        "bb_min_y": float(bb_min[1]),
        "bb_min_z": float(bb_min[2]),
        "bb_max_x": float(bb_max[0]),
        "bb_max_y": float(bb_max[1]),
        "bb_max_z": float(bb_max[2]),
        "centroid_x": float(centroid[0]),
        "centroid_y": float(centroid[1]),
        "centroid_z": float(centroid[2]),
        "geometry_id": shape.geometry.id
    }
    
    return rep


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
                    geometric_type = item.is_a()
                    # Now you can access geometry-specific attributes depending on type
                    if item.is_a("IfcMappedItem"):
                        representation_type_mapped_item = item.MappingSource.MappedRepresentation.RepresentationType
                        geometric_type = f"Mapped Item - {representation_type_mapped_item}"
        return geometric_type
    return None
                   
geo_repis = []
for entity in primary_entities:
    if hasattr(entity, "Representation") and entity.Representation is not None:
        traversed = model.traverse(entity, 10)
        print("")
        print(traversed)
        print("")
    geo_repo = get_combined_geo_representation(entity)
    if geo_repo is None:
        continue
    geo_repis.append(geo_repo)

