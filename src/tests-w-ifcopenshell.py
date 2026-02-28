
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
ifc_path = "src/01_sampleData/basic-geometric-changes/base-w-wall-2x3.ifc"
ifc_path_2 = "src/01_sampleData/basic-geometric-changes/translated-wall.ifc"
ifc_4="src/02_sampleData/test.ifc"
model = ifcopenshell.open(ifc_4)
# Retrieve IFC entities that will be PrimaryNodes, same for ConnectionNodes.
primary_entities_object_definitions = model.by_type("IfcObjectDefinition") 
primary_ent_product_definitions = model.by_type("IfcProduct")
primar_entities_property_def = model.by_type("IfcPropertyDefinition")
connection_entities = model.by_type("IfcRelationship")
#geo_repr = model.by_type("IfcProfilDef")



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

def get_coordinates_poly_line(poly_line):
    points = poly_line.Points
    points_coordinates = []
    for p in points:
        points_coordinates.append(p.Coordinates)
    return points_coordinates

def get_coordinates_polygon(polygon):
    points_coordinates = []
    for p in polygon:
        points_coordinates.append(p.Coordinates)
    return points_coordinates

def get_geometry_IfcExtruded_Area_Solid(item):
    geometry_info = {
        "direction": item.ExtrudedDirection.DirectionRatios,
        "depth": item.Depth
    }
    sweptArea = item.SweptArea
    if sweptArea.is_a("IfcRectangleProfileDef"):
        geometry_info["swept_area"] = "IfcRectangleProfileDef"
        geometry_info["x_dim"] = sweptArea.XDim
        geometry_info["y_dim"] = sweptArea.YDim
    elif sweptArea.is_a("IfcArbitraryClosedProfileDef"):
        geometry_info["swept_area"] = "IfcArbitraryClosedProfileDef"
        outer_curve = sweptArea.OuterCurve ### IfcPolyline
        coordinates = get_coordinates_poly_line(outer_curve)
        geometry_info["outer_curve_coordinates"] = coordinates
    else:
        ## TO BE IMPLEMENTED
        return None
def get_geometry_Ifc_Boolean_Clipping_Result(item):
    geometry_info = {}
    operator = item.Operator
    first_operand = item.FirstOperand ## either IfcSweptAreaSolid OR IfcBooleanClippingResult
    second_operand = item.SecondOperand ## IfcHalfSpaceSolid

    
                   
geo_repis = []
for entity in primary_entities_object_definitions:
    if hasattr(entity, "Representation") and entity.Representation is not None:
        #print(f"IfcEntity: {entity}")
        #print(ifcopenshell.util.element.get_material(entity))
        
        ## IFC Product Representation (-> IfcTopologyRepresentation/ IfcShapeRepresentation)
        rep = entity.Representation
        
        ## IfcShapeRepresentation
        representation = entity.Representation.Representations
        
        for i,rep in enumerate(representation):
        ## IfcShapeRepresentaion - Type
            #print(f"   {i+1}. IfcShapeRepresentaion:")
            repType = rep.RepresentationType
            #print(f"   IfcShapeRepresentaion - Type: {repType}")
        
        ## IfcShapeRepresentaion - Identifier
            repIdnetifier = rep.RepresentationIdentifier
            #print(f"   IfcShapeRepresentaion - Identifier: {repIdnetifier}")
        
        
        ## IfcShapeRepresentation - IfcRepresentationItems
            repItems = rep.Items
            for item in repItems:
                
                #print(f"   IfcShapeRepresentaion - RepresentationItems: {repItems}")
                if item.is_a("IfcFacetedBrep"):
                    outer = item.Outer #IfcClosedShell
                    cfsFaces = outer.CfsFaces #CfsFaces -> set of IfcFaces
                    for face in cfsFaces:
                        bounds = face.Bounds #IfcBound -> Boundris of the face
                        for bound in bounds:
                            orientation = bound.Orientation #Orientation of bound, True or False
                            actual_bound = bound.Bound ## for facetedBrep always Polyloop (Polygon defined by Points)
                            polygon_coordinates = get_coordinates_polygon(actual_bound.Polygon)
                            #print(f"      Polygon: {polygon_coordinates}")
                            #print(f"      Orientation: {orientation}")
                        
                    
                        
                elif item.is_a("IfcBoundingBox"):
                    bbox = item
                    corner = bbox.Corner.Coordinates
                    x_dim = bbox.XDim
                    y_dim = bbox.YDim
                    z_dim = bbox.ZDim
                elif item.is_a("IfcPolyline"):
                    points_coordinates = get_coordinates_poly_line(item)
                    #print(f"      Polyline-Points: {points_coordinates}")
                elif item.is_a("IfcExtrudedAreaSolid"):
                        extrudedDirection = item.ExtrudedDirection.DirectionRatios
                        depth = item.Depth
                        sweptArea = item.SweptArea
                        if sweptArea.is_a("IfcRectangleProfileDef"):
                            x_dim = sweptArea.XDim
                            y_dim = sweptArea.YDim
                            #print(f"     extruded solid - direction: {extrudedDirection}; depth: {depth}; sweptArea: {sweptArea.XDim} ; {sweptArea.YDim}")
                        elif sweptArea.is_a("IfcArbitraryClosedProfileDef"):
                            outer_curve = sweptArea.OuterCurve ### IfcPolyline
                            coordinates = get_coordinates_poly_line(outer_curve)
                            #print(f"      swept solid-coordinates: {coordinates}")

                elif repType == "MappedRepresentation":
                    mappingsrc = repItems[0].MappingSource
                    mapped_representation = mappingsrc.MappedRepresentation
                    mapped_type = mapped_representation.RepresentationType
                    #print(f"       Mapped Representation- Type: {mapped_type}")
                    mapped_items = mapped_representation.Items
                    #print(f"       Mapped Representation- Items: {mapped_items}")
                    
                else:
                    if entity.is_a("IfcAnnotation"):
                        continue
                    elif item.is_a("IfcFacetedBrep"):
                        continue
                    print(item)
                    if item.is_a("IfcBooleanClippingResult"):
                        operator = item.Operator
                        first_operand = item.FirstOperand ## either IfcSweptAreaSolid OR IfcBooleanClippingResult
                        second_operand = item.SecondOperand
                    if item.is_a("IfcGeometricCurveSet"):
                        elements = item.Elements # Set of IfcGeometricSetSelected (Points, Curves, Surfaces)
                        for element in elements:
                            if element.is_a("IfcPolyline"):
                                coordinates = get_coordinates_poly_line(element)
                                print(f"     Coordinates: {coordinates}")
                    
                    
            
            
        
        #for i in traversed:
            #print(f"   {i}")
    

resources = model.by_type("IfcMaterialDefinition")
resources2 = model.by_type("IfcObjectPlacement")
#print(resources)


print("Placements:")
print()
print()
#print(resources2)

