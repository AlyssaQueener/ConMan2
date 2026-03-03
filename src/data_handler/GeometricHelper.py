
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import numpy as np


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
   
 
    def polygon_area(self,vertices):
        pts = np.array(vertices)
        area = 0.0
        for i in range(1, len(pts) - 1):
            a = pts[i] - pts[0]
            b = pts[i + 1] - pts[0]
            area += np.linalg.norm(np.cross(a, b))
        return area / 2.0
    



    def get_geometry_Ifc_Polygonal_Face_Set(self, item):
        coord_list = item.Coordinates.CoordList
        pn_index = item.PnIndex

        def resolve_index(i):
            if pn_index:
                return coord_list[pn_index[i - 1] - 1]
            return coord_list[i - 1]

        # Resolve faces to actual coordinates
        resolved_faces = []
        for face in item.Faces:
            outer_loop = [resolve_index(i) for i in face.CoordIndex]
            face_data = {"outer_loop": outer_loop}
            if hasattr(face, "InnerCoordIndices") and face.InnerCoordIndices:
                face_data["inner_loops"] = [
                    [resolve_index(i) for i in loop]
                    for loop in face.InnerCoordIndices
                ]
            resolved_faces.append(face_data)

        # Compute per-face areas
        face_areas = []
        for face in resolved_faces:
            area = self.polygon_area(face["outer_loop"])
            for inner in face.get("inner_loops", []):
                area -= self.polygon_area(inner)
            face_areas.append(area)

        # Fixed-size feature vector
        pts = np.array(coord_list)
        centroid = pts.mean(axis=0)
        bbox_min = pts.min(axis=0)
        bbox_max = pts.max(axis=0)
        extents = bbox_max - bbox_min

        geometry_info = {
            "closed": int(item.Closed) if item.Closed is not None else 0,
            "centroid": centroid.tolist(),
            "bbox_min": bbox_min.tolist(),
            "bbox_max": bbox_max.tolist(),
            "extents": extents.tolist(),
            "total_surface_area": sum(face_areas),
            "max_face_area": max(face_areas),
            "min_face_area": min(face_areas),
            "n_faces": len(resolved_faces),
            "n_vertices": len(coord_list),
            # raw data in case you need it
            "faces": resolved_faces,
            "coord_list": [tuple(c) for c in coord_list]
        }
        
        geo_info = {
            "geometricRepresentation":[0,1],
            
            "total_surface_area": round(float(sum(face_areas)),3),
            "delta_total_surface_area": 0,
            
            "max_face_area": round(float(max(face_areas)),3),
            "delta_max_face_area": 0,

            "min_face_area": round(float(min(face_areas)),3),
            "delta_min_face_area": 0,

            "n_faces": len(resolved_faces),
            "delta_n_faces": 0,
            
            "n_vertices": len(coord_list),
            "delta_n_vertices": 0
            
        }

        return geo_info
            
    def get_geometry_IfcExtruded_Area_Solid(self, item):
        ### -> RepresentationType = Extruded Area -> [1,0]
        depth = round(item.Depth,3)
        geometry_info = {
            "geometricRepresentation": [1,0],
            "direction": item.ExtrudedDirection.DirectionRatios,
            "depth": depth
        }
        sweptArea = item.SweptArea
        if sweptArea.is_a("IfcRectangleProfileDef"):
            geometry_info["swept_area"] = "IfcRectangleProfileDef"
            profile_features = self.compute_profile_features_rectangle(sweptArea.XDim,sweptArea.YDim )
            volume = profile_features["area"]*depth
            geometry_info.update(profile_features)
            geometry_info.update({
                    "volume": volume,
                    "delta_volume": 0
                })
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
            profile_features = self.compute_profile_features(coordinates)
            volume = profile_features["area"]*depth
            geometry_info.update(profile_features)
            geometry_info.update({
                    "volume": volume,
                    "delta_volume": 0
                })
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
            "delta_bbox_x": 0,
            
            "bbox_y": y_dim,
            "delta_bbox_y": 0,
            
            "area": area,
            "delta_area": 0,

            "perimeter": perimeter,
            "delta_perimeter": 0,
            
            "num_vertices": 4,
            "delta_num_vertices": 0,
            
            "compactness": round(((4 * 3.14159265 * area) / perimeter**2),3),
            "delta_compactness": 0,
            
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
            "delta_bbox_x": 0,
            
            "bbox_y": bbox_y,
            "delta_bbox_y": 0,
            
            "area": area,
            "delta_area": 0,
            
            "perimeter": perimeter,
            "delta_perimeter": 0,
            
            "num_vertices": n,
            "delta_num_vertices": 0,
            
            "compactness": compactness,
            "delta_compactness": 0
        }
    

    

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
                            if geo_info:
                                geo_infos.append(geo_info)
                            else: continue
                    else:
                        geo_info = process_body_representations(item)
                        if geo_info:
                            geo_infos.append(geo_info) 
                        else: continue 
                elif repIdentifier == "FootPrint":            
                    if repType == "MappedRepresentation":
                        mapped_representation_items = item.MappingSource.MappedRepresentation.Items
                        for i in mapped_representation_items:
                            geo_info = process_footprint_representation(i)
                            if geo_info:
                                geo_infos.append(geo_info)
                            else:
                                continue
                    else:
                        geo_info = process_footprint_representation(item)
                        if geo_info:
                            geo_infos.append(geo_info)
                        else:
                            continue  
                else:
                    print(f"    not recoginzed Items:   {item}")
        entity_geo[repIdentifier] = geo_infos            
        
        


