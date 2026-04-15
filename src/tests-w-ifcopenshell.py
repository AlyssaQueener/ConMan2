
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import json
from data_handler.GeometricHelper import GeometricHelper  # import the class from the module




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
                                
                                
                                
def process_body_representations(item):
        helper = GeometricHelper()
        geometric_rep = {}
        if item.is_a("IfcFacetedBrep"):
            geometric_rep = helper.get_geometry_IfcFacetedBrep(item)
            extruded = False
        elif item.is_a("IfcExtrudedAreaSolid"):
            geometric_rep = helper.get_geometry_IfcExtruded_Area_Solid(item)
            extruded = True
        elif item.is_a("IfcPolygonalFaceSet"):
            geometric_rep = helper.get_geometry_Ifc_Polygonal_Face_Set(item)
            #geometric_rep = helper.get_Polygonal_Face_Set_w_openshell(item)
            extruded = False
        else:
            print(f"Body representation Not yet implemented: {item}")
            return None, None
        return geometric_rep, extruded

def process_footprint_representation(item):
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
                    
                    
def create_surface_and_solid_nodes(entity, surface_nodes, solid_nodes, surface_relationships, solid_relationships,brep_nodes, brep_relationships, timestamp, geo_count, graph_type, printed):
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
                geometric_representation_item_json = []
                for item in repItems:
                    
                
                    if repIdentifier == "Body":
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info, extruded = process_body_representations(i)
                                geometric_representation_item_json.append(geo_info)
                        else:
                            geo_info, extruded = process_body_representations(item)
                            geometric_representation_item_json.append(geo_info)
                    elif repIdentifier == "FootPrint":            
                        if repType == "MappedRepresentation":
                            mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                            for i in mapped_representation_items:
                                geo_info = process_footprint_representation(i)
                                geometric_representation_item_json.append(geo_info)
                        else:
                            geo_info = process_footprint_representation(item)
                            geometric_representation_item_json.append(geo_info)
                    else:
                        print(f"   for {entity}, representation Identifier: {repIdentifier} not recoginzed Items:   {item}")
                print(geometric_representation_item_json)
        
        

model = ifcopenshell.open("src/06_TestData/2026-03-SampleData-ChangeInterpretation-v3.ifc")
primary_entities = model.by_type("IfcObjectDefinition")
geo_help = GeometricHelper()

for entity in primary_entities:
    if hasattr(entity, "Representation") and entity.Representation is not None:
        s = []
        a = [] 
        b= []
        c=[]
        d=[]
        e=[]
        f=[]
        g=""
        h="2"
        j=1
        k=[]
        create_surface_and_solid_nodes(entity,a,k,b,c,d,e,g,j,h,f)
                    
                
                        
                    
                        
                