
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape

class GeometryHelper:
    
    def get_coordinates_Ifc_poly_line(self, poly_line):
        points = poly_line.Points
        points_coordinates = []
        for p in points:
            points_coordinates.append(p.Coordinates)
        return points_coordinates
    
    
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
                coordinates = self.get_coordinates_poly_line(element)
                geometric_info[i] = coordinates
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
        geometry_info = {
            "direction": item.ExtrudedDirection.DirectionRatios,
            "depth": item.Depth
        }
        sweptArea = item.SweptArea
        if sweptArea.is_a("IfcRectangleProfileDef"):
            geometry_info["swept_area"] = "IfcRectangleProfileDef"
            geometry_info["x_dim"] = sweptArea.XDim
            geometry_info["y_dim"] = sweptArea.YDim
            return geometry_info
        elif sweptArea.is_a("IfcArbitraryClosedProfileDef"):
            geometry_info["swept_area"] = "IfcArbitraryClosedProfileDef"
            outer_curve = sweptArea.OuterCurve ### IfcPolyline
            if outer_curve.is_a("IfcPolyline"):
                coordinates = self.get_coordinates_poly_line(outer_curve)
            elif outer_curve.is_a("IfcIndexedPolyCurve"):
                coordinates = self.get_coordinates_Ifc_Indexed_Poly_Curve(outer_curve)
            else:
                print(f"not yet handled curve: {outer_curve}")
                return None
            geometry_info["outer_curve_coordinates"] = coordinates
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
                polygon_coordinates = self.get_coordinates_polygon(actual_bound.Polygon)
                face_bound = {
                    "orientation": orientation,
                    "polygon_coordinates": polygon_coordinates
                }
                face_bounds.append(face_bound)
                            #print(f"      Polygon: {polygon_coordinates}")
                            #print(f"      Orientation: {orientation}")
            geometry_info[i]=face_bounds
        return geometry_info
    
    def get_coordinates_Ifc_Indexed_Poly_Curve(self, outer_curve):
         ### not done yet
        points = outer_curve.Points.CoordList
        segments = outer_curve.Segments
        self_intersect = outer_curve.SelfIntersect
        return points
    
ifc_path = "src/01_sampleData/basic-geometric-changes/base-w-wall-2x3.ifc"
ifc_path_2 = "src/01_sampleData/basic-geometric-changes/translated-wall.ifc"
ifc_4="src/02_sampleData/test.ifc"
ifc_4_1 = "src/01_sample_data/base-example-wall-ifc4.ifc"
model = ifcopenshell.open(ifc_4_1)
# Retrieve IFC entities that will be PrimaryNodes, same for ConnectionNodes.
primary_entities_object_definitions = model.by_type("IfcObjectDefinition") 
primary_ent_product_definitions = model.by_type("IfcProduct")
primar_entities_property_def = model.by_type("IfcPropertyDefinition")
connection_entities = model.by_type("IfcRelationship")
#geo_repr = model.by_type("IfcProfilDef")



    
helper = GeometryHelper()                   
geo_repis = []
for entity in primary_entities_object_definitions:
    if hasattr(entity, "Representation") and entity.Representation is not None:
        print(f"IfcEntity: {entity}")
        #print(ifcopenshell.util.element.get_material(entity))
        
        ## IFC Product Representation (-> IfcTopologyRepresentation/ IfcShapeRepresentation)
        rep = entity.Representation
        
        ## IfcShapeRepresentation
        representation = entity.Representation.Representations
        
        for i,rep in enumerate(representation):
        ## IfcShapeRepresentaion - Type
            print(f"   {i+1}. IfcShapeRepresentaion:")
            repType = rep.RepresentationType
            #print(f"   IfcShapeRepresentaion - Type: {repType}")
        
        ## IfcShapeRepresentaion - Identifier
            repIdnetifier = rep.RepresentationIdentifier
            print(f"   IfcShapeRepresentaion - Identifier: {repIdnetifier}")
        
        
        ## IfcShapeRepresentation - IfcRepresentationItems
            repItems = rep.Items
            for item in repItems:
                
                #print(f"   IfcShapeRepresentaion - RepresentationItems: {repItems}")
                if item.is_a("IfcFacetedBrep"):
                    geo_representation = helper.get_geometry_IfcFacetedBrep(item)
                    #print(f"              Faceted Brep: {geo_representation}")
                          
                elif item.is_a("IfcBoundingBox"):
                    continue
                elif item.is_a("IfcPolyline"):
                    points_coordinates = helper.get_coordinates_poly_line(item)
                    #print(f"      Polyline-Points: {points_coordinates}")
                elif item.is_a("IfcExtrudedAreaSolid"):
                        geo_rep = helper.get_geometry_IfcExtruded_Area_Solid(item)
                        #print(f"      Extruded Solid: {geo_rep}")  
                elif item.is_a("IfcExtrudedAreaSolid"):
                    print("")
                        
                elif item.is_a("IfcGeometricCurveSet"):
                    info = helper.get_IfcGeometric_Curve_Set(item)           
                    #print(f"              GeometricCurveSet: {info}")
                elif repType == "MappedRepresentation":
                    mappingsrc = repItems[0].MappingSource
                    mapped_representation = mappingsrc.MappedRepresentation
                    mapped_type = mapped_representation.RepresentationType
                    #print(f"       Mapped Representation- Type: {mapped_type}")
                    mapped_items = mapped_representation.Items
                    #print(f"       Mapped Representation- Items: {mapped_items}")
                elif item.is_a("IfcPolygonalFaceSet"):
                    geometric_rep = helper.get_geometry_Ifc_Polygonal_Face_Set(item)
                    print(f"       {geometric_rep}")
                elif item.is_a("IfcGeometricCurveSet"):
                    elements = item.Elements # Set of IfcGeometricSetSelected (Points, Curves, Surfaces)
                    for element in elements:
                        if element.is_a("IfcPolyline"):
                            coordinates = helper.get_coordinates_poly_line(element)
                            #print(f"     Coordinates: {coordinates}")
                    
                else:
                    print(f"    not recoginzed Items:   {item}")
                    
                  
                    
                    
                    
            
            
        
        #for i in traversed:
            #print(f"   {i}")
    

resources = model.by_type("IfcMaterialDefinition")
resources2 = model.by_type("IfcObjectPlacement")
#print(resources)


print("Placements:")
print()
print()
#print(resources2)

