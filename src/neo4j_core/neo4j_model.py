from neomodel import (
    StructuredRel,
    StringProperty,
    RelationshipTo,
    IntegerProperty
)
from neomodel.contrib import SemiStructuredNode


class RelProperties(StructuredRel):
    '''
    Relationship class for defining properties of relationships between nodes.
    '''
    rel_type = StringProperty(required=True)
    listItem = IntegerProperty()


class Node(SemiStructuredNode):
    EntityType = StringProperty(required=True)
    relation = RelationshipTo('Node', 'rel', model=RelProperties)


class GenericNode(Node):
    p21_id = StringProperty(required=True)
    timestamp = StringProperty(required=True)


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