
// Push-Out-Muster

MERGE 
(n219:ts20240220T112845:PrimaryNode{
    EntityType:"IfcWallStandardCase",
    ObjectType:"Basiswand:Ziegel 300",
    Description:"None",
    Tag:"2556713",
    GlobalId:"26qcSBz5P4dvcRDncj9N0t",
    Name:"Basiswand:Ziegel 300:2556713"})
-[e727:rel{
    rel_type:"Representation"}]->
(n218:SecondaryNode:ts20240220T112845{
    EntityType:"IfcProductDefinitionShape",
    Description:"None",
    Name:"None"}) 

MERGE (n218)
-[e729:rel{
    listItem:1,
    rel_type:"Representations"}]->
(n217:ts20240220T112845:SecondaryNode{
    EntityType:"IfcShapeRepresentation",
    RepresentationIdentifier:"Body",
    RepresentationType:"Clipping"}) 

MERGE (n217)
-[e731:rel{
    listItem:0,
    rel_type:"Items"}]->
(n211:SecondaryNode:ts20240220T112845{
    EntityType:"IfcBooleanClippingResult",
    Operator:"DIFFERENCE"}) 

MERGE (n211)
-[e738:rel{
    rel_type:"SecondOperand"}]->
(n210:SecondaryNode:ts20240220T112845{
    EntityType:"IfcPolygonalBoundedHalfSpace",
    AgreementFlag:True}) 

MERGE (n210)
-[e741:rel{
    rel_type:"PolygonalBoundary"}]->
(n204:SecondaryNode:ts20240220T112845{
    EntityType:"IfcPolyline"}) 

MERGE (n204)
-[e750:rel{
    listItem:3,
    rel_type:"Points"}]->
(n203:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(0.0, 0.30)"}) 

MERGE (n204)
-[e749:rel{
    listItem:2,
    rel_type:"Points"}]->
(n202:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(2.90, 0.30)"}) 

MERGE (n204)
-[e748:rel{
    listItem:1,
    rel_type:"Points"}]->
(n201:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(2.90, 0.0)"}) 

MERGE (n204)
-[e747:rel{
    listItem:4,
    rel_type:"Points"}]->
(n4:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(0.0, 0.0)"}) 

MERGE (n210)
-[e740:rel{
    rel_type:"Position"}]->
(n209:SecondaryNode:ts20240220T112845{
    EntityType:"IfcAxis2Placement3D"}) 

MERGE (n209)
-[e742:rel{
    rel_type:"Location"}]->
(n208:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(0.0, -0.15, 4.70)"}) 

MERGE (n210)
-[e739:rel{
    rel_type:"BaseSurface"}]->
(n207:SecondaryNode:ts20240220T112845{
    EntityType:"IfcPlane"}) 

MERGE (n207)
-[e743:rel{
    rel_type:"Position"}]->
(n206:SecondaryNode:ts20240220T112845{
    EntityType:"IfcAxis2Placement3D"}) 

MERGE (n206)
-[e745:rel{
    rel_type:"Axis"}]->
(n10:ts20240220T112845:SecondaryNode{
    EntityType:"IfcDirection",
    DirectionRatios:"(0.0, 0.0, -1.0)"}) 

MERGE (n206)
-[e744:rel{
    rel_type:"Location"}]->
(n205:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(0.0, -0.15, 4.70)"}) 

MERGE (n211)
-[e737:rel{
    rel_type:"FirstOperand"}]->
(n200:SecondaryNode:ts20240220T112845{
    EntityType:"IfcExtrudedAreaSolid",
    Depth:4.70}) 

MERGE (n200)
-[e752:rel{
    rel_type:"Position"}]->
(n199:SecondaryNode:ts20240220T112845{
    EntityType:"IfcAxis2Placement3D"}) 

MERGE (n200)
-[e751:rel{
    rel_type:"SweptArea"}]->
(n198:SecondaryNode:ts20240220T112845{
    EntityType:"IfcRectangleProfileDef",
    ProfileType:"AREA",
    YDim:0.30,
    XDim:2.90,
    ProfileName:"None"}) 

MERGE (n198)
-[e755:rel{
    rel_type:"Position"}]->
(n197:SecondaryNode:ts20240220T112845{
    EntityType:"IfcAxis2Placement2D"}) 

MERGE (n197)
-[e757:rel{
    rel_type:"RefDirection"}]->
(n12:ts20240220T112845:SecondaryNode{
    EntityType:"IfcDirection",
    DirectionRatios:"(-1.0, 0.0)"}) 

MERGE (n197)
-[e756:rel{
rel_type:"Location"}]->
    (n196:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(1.45, 0.0)"}) 

MERGE (n218)
-[e728:rel{
    listItem:0,
    rel_type:"Representations"}]->
(n195:ts20240220T112845:SecondaryNode{
    EntityType:"IfcShapeRepresentation",
    RepresentationIdentifier:"Axis",
    RepresentationType:"Curve2D"}) 

MERGE (n195)
-[e1056:rel{
    listItem:0,
    rel_type:"Items"}]->
(n194:SecondaryNode:ts20240220T112845{
    EntityType:"IfcPolyline"}) 

MERGE (n194)
-[e1059:rel{
    listItem:1,
    rel_type:"Points"}]->
(n193:SecondaryNode:ts20240220T112845{
    EntityType:"IfcCartesianPoint",
    Coordinates:"(2.90, -0.0)"}) 

MERGE (n194)
-[e1058:rel{
    listItem:0,
    rel_type:"Points"}]->
(n4) 

MERGE (n195)
-[e1055:rel{
    rel_type:"ContextOfItems"}]->
(n99:SecondaryNode:ts20240220T112845{
    EntityType:"IfcGeometricRepresentationSubContext",
    TargetScale:"None",
    ContextType:"Model",
    ContextIdentifier:"Axis",
    TargetView:"GRAPH_VIEW",
    Precision:"None"
    UserDefinedTargetView:"None",
    CoordinateSpaceDimension:"None"}) 

MERGE (n219)
-[e726:rel{
    rel_type:"ObjectPlacement"}]->
(n192:SecondaryNode:ts20240220T112845{
    EntityType:"IfcLocalPlacement"}) 

MERGE (n192)
-[e759:rel{
    rel_type:"RelativePlacement"}]->
(n191:SecondaryNode:ts20240220T112845{
    EntityType:"IfcAxis2Placement3D"}) 

MERGE (n191)
-[e762:rel{
    rel_type:"RefDirection"}]->
(n7:ts20240220T112845:SecondaryNode{
    EntityType:"IfcDirection",
    DirectionRatios:"(0.0, 1.0, 0.0)"}) 

MERGE (n191)
-[e760:rel{
    rel_type:"Location"}]->
(n190:SecondaryNode:ts20240220T112845{
EntityType:"IfcCartesianPoint",
    Coordinates:"(12.45, 5.54, 0.0)"}) 

MERGE (n233:ConnectionNode:ts20240220T112845{
    EntityType:"IfcRelAssociatesMaterial",
    Description:"None",
    GlobalId:"3RmbaeZXNm8qNm9HnItoy1",
    Name:"None"})
-[e697:rel{
    listItem:0,
    rel_type:"RelatedObjects"}]->
(n219) 

MERGE (n233)
-[e696:rel{
    rel_type:"RelatingMaterial"}]->
(n227:SecondaryNode:ts20240220T112845{
    EntityType:"IfcMaterialLayerSetUsage",
    LayerSetDirection:"AXIS2",
    OffsetFromReferenceLine:0.15,
    DirectionSense:"NEGATIVE"}) 

MERGE (n239:ConnectionNode:ts20240220T112845{
    EntityType:"IfcRelDefinesByType",
    Description:"None",
    GlobalId:"1RTnKtmVgl37rEnHo$VnfZ",
    Name:"None"})
-[e674:rel{
    listItem:0,
    rel_type:"RelatedObjects"}]->
(n219) 

MERGE (n239)
-[e673:rel{
    rel_type:"RelatingType"}]->
(n228:ts20240220T112845:PrimaryNode{
    EntityType:"IfcWallType",
    ElementType:"None",
    Description:"None",
    ApplicableOccurrence:"None",
    Tag:"712215",
    PredefinedType:"STANDARD",
    GlobalId:"1ZU3D9$OrB9Q3fkDK9b0SW",
    Name:"Basiswand:Ziegel 300"}) 

MERGE (n235:ConnectionNode:ts20240220T112845{
    EntityType:"IfcRelAssociatesMaterial",
    Description:"None",
    GlobalId:"0geCvqm3_awNTIu_FrDGao",
    Name:"None"})
-[e686:rel{
    listItem:0,
    rel_type:"RelatedObjects"}]->
(n228) 

MERGE  (n235)
-[e685:rel{
    rel_type:"RelatingMaterial"}]->
(n226:SecondaryNode:ts20240220T112845{
    EntityType:"IfcMaterialLayerSet",
    LayerSetName:"Basiswand:Ziegel 300"}) 

MERGE (n227)
-[e716:rel{
    rel_type:"ForLayerSet"}]->
(n226) 

MERGE (n226)
-[e717:rel{
    listItem:0,
    rel_type:"MaterialLayers"}]->
(n225:SecondaryNode:ts20240220T112845{
    EntityType:"IfcMaterialLayer",
    IsVentilated:"None",
    LayerThickness:0.30}) 

MERGE (n225)
-[e718:rel{
    rel_type:"Material"}]->
(n220:SecondaryNode:ts20240220T112845{
    EntityType:"IfcMaterial",
    Name:"Mauerwerk - Ziegel"}) 

MERGE (n224:SecondaryNode:ts20240220T112845{
    EntityType:"IfcMaterialDefinitionRepresentation",
    Description:"None",
    Name:"None"})
-[e719:rel{
    rel_type:"RepresentedMaterial"}]->
(n220) 

MERGE (n224)
-[e720:rel{
    listItem:0,
    rel_type:"Representations"}]->
(n223:SecondaryNode:ts20240220T112845{
    EntityType:"IfcStyledRepresentation",
    RepresentationIdentifier:"Style",
    RepresentationType:"Material"}) 

MERGE (n223)
-[e722:rel{
    listItem:0,
    rel_type:"Items"}]->
(n222:SecondaryNode:ts20240220T112845{
    EntityType:"IfcStyledItem",
    Name:"None"}) 


