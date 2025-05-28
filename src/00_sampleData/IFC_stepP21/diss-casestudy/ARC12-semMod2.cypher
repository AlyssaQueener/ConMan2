

MATCH (n189:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn", GlobalId:"0h0LzMJt93cez1WHNgxod6"}) 
-[:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[:rel{listItem:0, rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[:rel{rel_type:"SweptArea"}]->
(n175:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"})
-[:rel{rel_type:"Position"}]->
(n174:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[:rel{rel_type:"Location"}]->
(n173:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 

MATCH (n170:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn", GlobalId:"0h0LzMJt93cez1WHNgxoa"}) 
-[:rel{rel_type:"Representation"}]->
(n167:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[:rel{listItem:0, rel_type:"Representations"}]->
(n166:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n165:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[:rel{rel_type:"MappingSource"}]->
(n163:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[:rel{rel_type:"MappedRepresentation"}]->
(n161:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n159:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[:rel{rel_type:"SweptArea"}]->
(n156:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"})
-[:rel{rel_type:"Position"}]->
(n155:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[:rel{rel_type:"Location"}]->
(n154:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 

MATCH (n151:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn", GlobalId:"2A$LC1Lgn0qvSYKm11Vune"}) 
-[:rel{rel_type:"Representation"}]->
(n148:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[:rel{listItem:0, rel_type:"Representations"}]->
(n147:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n146:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[:rel{rel_type:"MappingSource"}]->
(n138:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[:rel{rel_type:"MappedRepresentation"}]->
(n136:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[:rel{listItem:0, rel_type:"Items"}]->
(n130:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[:rel{rel_type:"SweptArea"}]->
(n127:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"})
-[:rel{rel_type:"Position"}]->
(n126:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[:rel{rel_type:"Location"}]->
(n125:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 

MATCH (n183:ts20240220T112536:PrimaryNode{EntityType:"IfcColumnType", GlobalId:"0h0LzMJt93cez1YHNgxod6"}) 
MATCH (n164:ts20240220T112536:PrimaryNode{EntityType:"IfcColumnType", GlobalId:"0h0LzMJt93cez1YHNgxoa$"}) 
MATCH (n139:ts20240220T112536:PrimaryNode{EntityType:"IfcColumnType", GlobalId:"2A$LC1Lgn0qvSYMm11Vune"}) 


SET n189.ObjectType = "STB Stütze - rechteckig:STB 400 x 400"
SET n189.Name = "STB Stütze - rechteckig:STB 400 x 400:2521492"
SET n175.YDim = 0.4
SET n175.XDim = 0.4
SET n175.ProfileName = "STB 400 x 400"
SET n173.Coordinates = "(0.0, 2.1649348980190553e-15)"

SET n170.ObjectType = "STB Stütze - rechteckig:STB 400 x 400"
SET n170.Name = "STB Stütze - rechteckig:STB 400 x 400:2521453"
SET n156.YDim = 0.4
SET n156.XDim = 0.4
SET n156.ProfileName = "STB 400 x 400"
SET n154.Coordinates = "(0.0, 0.0)"

SET n151.ObjectType = "STB Stütze - rechteckig:STB 400 x 400"
SET n151.Name = "STB Stütze - rechteckig:STB 400 x 400:2520640"
SET n127.YDim = 0.4
SET n127.XDim = 0.4
SET n127.ProfileName = "STB 400 x 400"
SET n125.Coordinates = "(0.0, 0.0)"


SET n183.Tag = "2077224"
SET n183.Name = "STB Stütze - rechteckig:STB 400 x 400"

SET n164.Tag = "2077224"
SET n164.Name = "STB Stütze - rechteckig:STB 400 x 400"

SET n139.Tag = "2077224"
SET n139.Name = "STB Stütze - rechteckig:STB 400 x 400"