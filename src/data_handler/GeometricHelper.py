
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape

class GeometricHelper:
    
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
                coordinates = self.get_coordinates_Ifc_poly_line(outer_curve)
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
        segments = outer_curve.Segments
        self_intersect = outer_curve.SelfIntersect
        return points
    

#geo_repr = model.by_type("IfcProfilDef")


def process_body_representations(item):
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
        
        


