from neomodel import (
    StructuredRel,
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty
)
from neomodel.contrib import SemiStructuredNode


class RelProperties(StructuredRel):
    rel_type = StringProperty(required=True)
    list_index = IntegerProperty()

class GeoRelProperties(StructuredRel):
    rel_type = StringProperty(required=True)

class Node(SemiStructuredNode):
    EntityType = StringProperty(required=True)
    relation_to = RelationshipTo('Node', 'RELATION_TO', model=RelProperties)
    relation_from = RelationshipFrom('Node', 'RELATION_TO', model=RelProperties)
    relation_to_geo = RelationshipTo('GenericGeoNode', 'GEO_RELATION_TO', model=GeoRelProperties)
    relation_from_geo = RelationshipFrom('GenericGeoNode', 'GEO_RELATION_TO', model=GeoRelProperties)
    equivalent_to = Relationship('Node', 'EQUIVALENT_TO')
    graph_type = StringProperty()
    timestamp = StringProperty()

class GenericGeoNode(SemiStructuredNode):
    p21_id = StringProperty(required=True)
    EntityType = StringProperty(required=True)
    relation_from = RelationshipFrom('Node', 'GEO_RELATION_TO', model=GeoRelProperties)  # same type as Node.relation_to_geo
    relation_to = RelationshipTo('Node', 'GEO_RELATION_TO', model=GeoRelProperties)  # same type as Node.relation_to_geo
    equivalent_to = Relationship('GenericGeoNode', 'EQUIVALENT_TO')
    graph_type = StringProperty()
    timestamp = StringProperty()

class GenericNode(Node):
    p21_id = StringProperty(required=True)


class PrimaryNode(GenericNode):
    GlobalId = StringProperty(unique_index=True, required=True)
    
    def __repr__(self):
        return f"PrimaryNode(GlobalId='{self.GlobalId}', EntityType='{self.EntityType}', timestamp='{self.timestamp}')"


class SecondaryNode(GenericNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
class GeoNode(GenericGeoNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"


class ConnectionNode(GenericNode):
    GlobalId = StringProperty(unique_index=True, required=True)

    def __repr__(self):
        return f"ConnectionNode(GlobalId='{self.GlobalId}', EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    

class InlineNode(Node):
    '''
    InlineNode class for Inline Entities in IFC like in:

    #92=IFCINDEXEDPOLYCURVE(#91,(IFCLINEINDEX((1,2)),IFCARCINDEX((2,3,4)),IFCLINEINDEX((4,5)),IFCARCINDEX((5,6,1))),.F.);
    '''

    def __repr__(self):
        return f"InlineNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"