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
    '''
    Relationship class for defining properties of relationships between nodes.
    '''
    rel_type = StringProperty(required=True)
    list_index = IntegerProperty()


class Node(SemiStructuredNode):
    EntityType = StringProperty(required=True)

    relation_to = RelationshipTo('Node', 'rel', model=RelProperties)
    relation_from = RelationshipFrom('Node', 'rel', model=RelProperties)
    equivalent_to = Relationship('Node', 'equivalent_to')

    pushout_id = IntegerProperty()

    timestamp = StringProperty(required=True)


class GenericNode(Node):
    p21_id = StringProperty(required=True)


class PrimaryNode(GenericNode):
    GlobalId = StringProperty(unique_index=True, required=True)
    
    def __repr__(self):
        return f"PrimaryNode(GlobalId='{self.GlobalId}', EntityType='{self.EntityType}', timestamp='{self.timestamp}')"


class SecondaryNode(GenericNode):
    
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