MATCH (n189:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn",
 GlobalId:"0h0LzMJt93cez1WHNgxod6"}) 
SET n189.Name = "STB Stütze - rechteckig:STB 400 x 400:2521492"

MATCH (n189:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn",
 GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e27:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e31:rel{listItem:0, rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e33:rel{listItem:0, rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e34:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e39:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e42:rel{listItem:0, rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode:EntityType:"IfcExtrudedAreaSolid"}) 
-[e46:rel{rel_type:"Position"}]->
(n177:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement3D"}) 
-[e48:rel{rel_type:"Location"}]->
(n176:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 
SET n176.Coordinates = "(18.253083841520386, 20.439499669173433, 0.0)"

MATCH (n189:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn",
 GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e27:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e31:rel{listItem:0,
 rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e33:rel{listItem:0,
 rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e34:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e39:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e42:rel{listItem:0,
 rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e45:rel{rel_type:"SweptArea"}]->
(n175:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n175.YDim = 0.4

MATCH (n189:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e27:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e31:rel{listItem:0,
 rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e33:rel{listItem:0,
 rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e34:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e39:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e42:rel{listItem:0,
 rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e45:rel{rel_type:"SweptArea"}]->
(n175:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n175.XDim = 0.4

MATCH (n189:ts20240220T112536:PrimaryNode{EntityType:"IfcColumn",
 GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e27:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e31:rel{listItem:0,
 rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e33:rel{listItem:0,
 rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e34:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e39:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e42:rel{listItem:0,
 rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e45:rel{rel_type:"SweptArea"}]->
(n175:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n175.ProfileName = "STB 400 x 400"

MATCH (n189:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxod6"})
-[e27:rel{rel_type:"Representation"}]->
(n186:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e31:rel{listItem:0,
 rel_type:"Representations"}]->
(n185:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e33:rel{listItem:0,
 rel_type:"Items"}]->
(n184:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e34:rel{rel_type:"MappingSource"}]->
(n182:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e39:rel{rel_type:"MappedRepresentation"}]->
(n180:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e42:rel{listItem:0,
 rel_type:"Items"}]->
(n178:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e45:rel{rel_type:"SweptArea"}]->
(n175:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
-[e51:rel{rel_type:"Position"}]->
(n174:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[e52:rel{rel_type:"Location"}]->
(n173:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 
SET n173.Coordinates = "(0.0, 2.1649348980190553e-15)"


MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"}) 
SET n170.ObjectType = "STB Stütze - rechteckig:STB 400 x 400"

MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"}) 
SET n170.Name = "STB Stütze - rechteckig:STB 400 x 400:2521453"

MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"})
-[e57:rel{rel_type:"Representation"}]->
(n167:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e61:rel{listItem:0, rel_type:"Representations"}]->
(n166:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e63:rel{listItem:0, rel_type:"Items"}]->
(n165:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e64:rel{rel_type:"MappingSource"}]->
(n163:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e69:rel{rel_type:"MappedRepresentation"}]->
(n161:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e72:rel{listItem:0, rel_type:"Items"}]->
(n159:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e75:rel{rel_type:"SweptArea"}]->
(n156:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n156.YDim = 0.4


MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"})
-[e57:rel{rel_type:"Representation"}]->
(n167:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e61:rel{listItem:0, rel_type:"Representations"}]->
(n166:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e63:rel{listItem:0, rel_type:"Items"}]->
(n165:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e64:rel{rel_type:"MappingSource"}]->
(n163:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e69:rel{rel_type:"MappedRepresentation"}]->
(n161:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e72:rel{listItem:0, rel_type:"Items"}]->
(n159:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e75:rel{rel_type:"SweptArea"}]->
(n156:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n156.XDim = 0.4



MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"})
-[e57:rel{rel_type:"Representation"}]->
(n167:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e61:rel{listItem:0, rel_type:"Representations"}]->
(n166:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e63:rel{listItem:0, rel_type:"Items"}]->
(n165:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e64:rel{rel_type:"MappingSource"}]->
(n163:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e69:rel{rel_type:"MappedRepresentation"}]->
(n161:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e72:rel{listItem:0, rel_type:"Items"}]->
(n159:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e75:rel{rel_type:"SweptArea"}]->
(n156:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n156.ProfileName = "STB 400 x 400"

MATCH (n170:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"0h0LzMJt93cez1WHNgxoa$"})
-[e57:rel{rel_type:"Representation"}]->
(n167:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e61:rel{listItem:0, rel_type:"Representations"}]->
(n166:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e63:rel{listItem:0, rel_type:"Items"}]->
(n165:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e64:rel{rel_type:"MappingSource"}]->
(n163:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e69:rel{rel_type:"MappedRepresentation"}]->
(n161:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e72:rel{listItem:0, rel_type:"Items"}]->
(n159:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e75:rel{rel_type:"SweptArea"}]->
(n156:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
-[e81:rel{rel_type:"Position"}]->
(n155:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[e82:rel{rel_type:"Location"}]->
(n154:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 
SET n154.Coordinates = "(0.0, 0.0)"

MATCH (n151:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"}) 
SET n151.ObjectType = "STB Stütze - rechteckig:STB 400 x 400"

MATCH (n151:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"}) 
SET n151.Name = "STB Stütze - rechteckig:STB 400 x 400:2520640"

MATCH (n151:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"})
-[e87:rel{rel_type:"Representation"}]->
(n148:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e91:rel{listItem:0, rel_type:"Representations"}]->
(n147:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e93:rel{listItem:0, rel_type:"Items"}]->
(n146:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e94:rel{rel_type:"MappingSource"}]->
(n138:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e106:rel{rel_type:"MappedRepresentation"}]->
(n136:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e109:rel{listItem:0, rel_type:"Items"}]->
(n130:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e115:rel{rel_type:"SweptArea"}]->
(n127:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n127.YDim = 0.4

MATCH (n151:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"})
-[e87:rel{rel_type:"Representation"}]->
(n148:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e91:rel{listItem:0, rel_type:"Representations"}]->
(n147:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e93:rel{listItem:0, rel_type:"Items"}]->
(n146:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e94:rel{rel_type:"MappingSource"}]->
(n138:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e106:rel{rel_type:"MappedRepresentation"}]->
(n136:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e109:rel{listItem:0, rel_type:"Items"}]->
(n130:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e115:rel{rel_type:"SweptArea"}]->
(n127:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n127.XDim = 0.4

MATCH (n151:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"})
-[e87:rel{rel_type:"Representation"}]->
(n148:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e91:rel{listItem:0,
 rel_type:"Representations"}]->
(n147:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e93:rel{listItem:0, rel_type:"Items"}]->
(n146:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e94:rel{rel_type:"MappingSource"}]->
(n138:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e106:rel{rel_type:"MappedRepresentation"}]->
(n136:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e109:rel{listItem:0, rel_type:"Items"}]->
(n130:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e115:rel{rel_type:"SweptArea"}]->
(n127:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
SET n127.ProfileName = "STB 400 x 400"

MATCH (n151:ts20240220T112536:PrimaryNode:IfcColumn{
    EntityType:"IfcColumn",
    GlobalId:"2A$LC1Lgn0qvSYKm11Vune"})
-[e87:rel{rel_type:"Representation"}]->
(n148:ts20240220T112536:SecondaryNode{EntityType:"IfcProductDefinitionShape"}) 
-[e91:rel{listItem:0, rel_type:"Representations"}]->
(n147:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e93:rel{listItem:0, rel_type:"Items"}]->
(n146:ts20240220T112536:SecondaryNode{EntityType:"IfcMappedItem"}) 
-[e94:rel{rel_type:"MappingSource"}]->
(n138:ts20240220T112536:SecondaryNode{EntityType:"IfcRepresentationMap"}) 
-[e106:rel{rel_type:"MappedRepresentation"}]->
(n136:ts20240220T112536:SecondaryNode{EntityType:"IfcShapeRepresentation"}) 
-[e109:rel{listItem:0, rel_type:"Items"}]->
(n130:ts20240220T112536:SecondaryNode{EntityType:"IfcExtrudedAreaSolid"}) 
-[e115:rel{rel_type:"SweptArea"}]->
(n127:ts20240220T112536:SecondaryNode{EntityType:"IfcRectangleProfileDef"}) 
-[e121:rel{rel_type:"Position"}]->
(n126:ts20240220T112536:SecondaryNode{EntityType:"IfcAxis2Placement2D"}) 
-[e122:rel{rel_type:"Location"}]->
(n125:ts20240220T112536:SecondaryNode{EntityType:"IfcCartesianPoint"}) 
SET n125.Coordinates = "(0.0, 0.0)"


MATCH (n183:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"0h0LzMJt93cez1YHNgxod6"}) 
SET n183.Tag = "2077224"

MATCH (n183:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"0h0LzMJt93cez1YHNgxod6"}) 
SET n183.Name = "STB Stütze - rechteckig:STB 400 x 400"


MATCH (n164:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"0h0LzMJt93cez1YHNgxoa$"}) 
SET n164.Tag = "2077224"

MATCH (n164:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"0h0LzMJt93cez1YHNgxoa$"}) 
SET n164.Name = "STB Stütze - rechteckig:STB 400 x 400"


MATCH (n139:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"2A$LC1Lgn0qvSYMm11Vune"}) 
SET n139.Tag = "2077224"

MATCH (n139:ts20240220T112536:PrimaryNode{
    EntityType:"IfcColumnType",
    GlobalId:"2A$LC1Lgn0qvSYMm11Vune"}) 
SET n139.Name = "STB Stütze - rechteckig:STB 400 x 400"

