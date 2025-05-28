MERGE (n219)-[e725:rel{rel_type:"OwnerHistory"}]->(n18) 
MERGE (n233)-[e695:rel{rel_type:"OwnerHistory"}]->(n18) 
MERGE (n239)-[e672:rel{rel_type:"OwnerHistory"}]->(n18) 
MERGE (n228)-[e715:rel{rel_type:"OwnerHistory"}]->(n18) 
MERGE (n235)-[e684:rel{rel_type:"OwnerHistory"}]->(n18) 

MERGE (n229)-[e21:rel{rel_type:"RelatedElements", listItem:23}]->(n219)

MERGE (n192)-[e758:rel{rel_type:"PlacementRelTo"}]->(n110) 
MERGE (n217)-[e730:rel{rel_type:"ContextOfItems"}]->(n100) 
MERGE (n206)-[e746:rel{rel_type:"RefDirection"}]->(n6) 
MERGE (n199)-[e754:rel{rel_type:"Location"}]->(n3) 

MERGE (n200)-[e753:rel{rel_type:"ExtrudedDirection"}]->(n9) 
MERGE (n191)-[e761:rel{rel_type:"Axis"}]->(n9) 

MERGE (n99)-[e894:rel{rel_type:"ParentContext"}]->(n98) 
MERGE (n223)-[e721:rel{rel_type:"ContextOfItems"}]->(n98) 
