MATCH path0 =
(n103:ts20240220T112845:PrimaryNode{EntityType:"IfcProject", GlobalId:"1ODmFv4Jv9ZO9fO_v2Tu_8"})
-[e888:rel{rel_type:"OwnerHistory"}]->
(n18:SecondaryNode:ts20240220T112845{EntityType:"IfcOwnerHistory"}) 

MATCH path1 =
(n189:ts20240220T112845:PrimaryNode{EntityType:"IfcColumn", GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e765:rel{rel_type:"Representation"}]->
(n186:SecondaryNode:ts20240220T112845{EntityType:"IfcProductDefinitionShape"})
-[e769:rel{listItem:0, rel_type:"Representations"}]->
(n185:ts20240220T112845:SecondaryNode{EntityType:"IfcShapeRepresentation"})
-[e770:rel{rel_type:"ContextOfItems"}]->
(n100:SecondaryNode:ts20240220T112845{EntityType:"IfcGeometricRepresentationSubContext"}) 

MATCH path2 =
(n185)
-[e771:rel{listItem:0, rel_type:"Items"}]->
(n184:SecondaryNode:ts20240220T112845{EntityType:"IfcMappedItem"})
-[e772:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112845:SecondaryNode{EntityType:"IfcRepresentationMap"})
-[e777:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112845:SecondaryNode{EntityType:"IfcShapeRepresentation"})
-[e780:rel{listItem:0, rel_type:"Items"}]->
(n178:SecondaryNode:ts20240220T112845{EntityType:"IfcExtrudedAreaSolid"})
-[e784:rel{rel_type:"Position"}]->
(n177:SecondaryNode:ts20240220T112845{EntityType:"IfcAxis2Placement3D"})
-[e788:rel{rel_type:"RefDirection"}]->
(n6:ts20240220T112845:SecondaryNode{EntityType:"IfcDirection"}) 

MATCH path3 =
(n178)
-[e785:rel{rel_type:"ExtrudedDirection"}]->
(n9:ts20240220T112845:SecondaryNode{EntityType:"IfcDirection"}) 

MATCH path4 =
(n103)
-[e890:rel{listItem:0, rel_type:"RepresentationContexts"}]->
(n98:SecondaryNode:ts20240220T112845{EntityType:"IfcGeometricRepresentationContext"})
-[e895:rel{rel_type:"WorldCoordinateSystem"}]->
(n96:SecondaryNode:ts20240220T112845{EntityType:"IfcAxis2Placement3D"})
-[e897:rel{rel_type:"Location"}]->
(n3:SecondaryNode:ts20240220T112845{EntityType:"IfcCartesianPoint"}) 

MATCH path5 = 
(n229:ts20240220T112601:ConnectionNode{EntityType:"IfcRelContainedInSpatialStructure", GlobalId:"13LV5dTeP3CAox54\mbox{\textdollar}56C1Z"})
