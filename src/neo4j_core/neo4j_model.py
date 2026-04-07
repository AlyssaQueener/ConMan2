from neomodel import (
    StructuredRel,
    StringProperty,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    IntegerProperty,
    FloatProperty
)
from neomodel.contrib import SemiStructuredNode


class RelProperties(StructuredRel):
    rel_type = StringProperty(required=True)
    list_index = IntegerProperty()

class GeoRelProperties(StructuredRel):
    rel_type = StringProperty(required=True)
    list_index = IntegerProperty()

class Node(SemiStructuredNode):
    EntityType = StringProperty(required=True)
    
    relation_to = RelationshipTo('Node', 'RELATION_TO', model=RelProperties)
    relation_from = RelationshipFrom('Node', 'RELATION_TO', model=RelProperties)
    
    relation_geo = Relationship('GenericGeoNode', 'GEO_RELATION_TO', model=GeoRelProperties)
    equivalent_to = Relationship('Node', 'EQUIVALENT_TO')
    similar_to = RelationshipTo('Node', 'SIMILAR')
    
    graph_type = StringProperty()
    timestamp = StringProperty()

class GenericGeoNode(SemiStructuredNode):
    p21_id = StringProperty(required=True)
    EntityType = StringProperty(required=True)
    
    relation_geo = Relationship('Node', 'GEO_RELATION_TO', model=GeoRelProperties)  # same type as Node.relation_to_geo
    equivalent_to = Relationship('GenericGeoNode', 'EQUIVALENT_TO')
    
    
    graph_type = StringProperty()
    timestamp = StringProperty()

class GenericNode(Node):
    p21_id = StringProperty(required=True)


class PrimaryNode(GenericNode):
    GlobalId = StringProperty(unique_index=True, required=True)
    geo_modification = FloatProperty()

    encoded_modified = FloatProperty()
    
    def __repr__(self):
        return f"PrimaryNode(GlobalId='{self.GlobalId}', EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
    
class SolidNode(GenericGeoNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
class BrepNode(GenericGeoNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
class SurfaceNode(GenericGeoNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
class LocationNode(GenericGeoNode):
    
    def __repr__(self):
        return f"SecondaryNode(EntityType='{self.EntityType}', timestamp='{self.timestamp}')"


class ConnectionNode(GenericNode):
    GlobalId = StringProperty(unique_index=True, required=True)

    def __repr__(self):
        return f"ConnectionNode(GlobalId='{self.GlobalId}', EntityType='{self.EntityType}', timestamp='{self.timestamp}')"
    
