
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape



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

primary_entities_object_definitions = []
                   
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
    

#print(resources)


print("Placements:")
print()
print()
#print(resources2)

