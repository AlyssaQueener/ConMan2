from neomodel import db
import ifcopenshell

class IfcGraphInterfaceBatched:

    ########################
    ### Helper Functions ###
    ########################


    def batch_cypher_query(self, query:str, rows:list, batch_size:int):
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            db.cypher_query(query, {"batch": batch})


    def process_ifc_attributes(self, entity:ifcopenshell.entity_instance, timestamp:str, props_map:dict, relationships:list, related_nodes:set, inline_patterns:list):
        p21_id = f"#{entity.id()}"

        # Recursively handle IFC attributes to catch primitives to nested lists.
        def traverse(key, val, list_index=0):
            if isinstance(val, ifcopenshell.entity_instance):
                # Case where attribute is single relation to other entity.
                if val.id() == 0:
                    inline_patterns.append({
                        "props": {
                            "EntityType": val.is_a(),
                            "wrappedValue": str(val.wrappedValue),
                            "timestamp": timestamp
                        },
                        "relation": {
                            "rel_type": key,
                            "list_index": list_index,
                            "source_p21_id": p21_id
                        }
                    })
                else:
                    related_p21_id = f"#{val.id()}"
                    relationships.append({
                        "source_p21_id": p21_id,
                        "target_p21_id": related_p21_id,
                        "timestamp": timestamp,
                        "rel_type": key,
                        "list_index": list_index
                    })
                    related_nodes.add(related_p21_id)
            elif isinstance(val, (tuple, list)):
                # Case where attribute is a list.
                if any(isinstance(x, ifcopenshell.entity_instance) for x in val):
                    # Case where list of IFC entities.
                    for i, x in enumerate(val):
                        traverse(key, x, list_index=i)
                else:
                    # Case where list of primtitves.
                    props_map.setdefault(p21_id, {})[key] = str(val)
            elif val is None:
                # Case where attribute is not assigned.
                props_map.setdefault(p21_id, {})[key] = "$"
            else:
                # Case where value is primitive.
                props_map.setdefault(p21_id, {})[key] = val
        
        info = entity.get_info()
        for key, val in info.items():
            # Ignore any IDs or types as they are already saved in the node and must not be changed
            if key in ("GlobalId", "EntityType", "type", "p21_id", "id", "inline_id", "timestamp"):
                continue
            else:
                traverse(key, val)


    ######################
    ### Main Functions ###
    ######################


    def ifc_2_graph(self, ifc_path:str, timestamp:str, batch_size:int):

        # Create index for p21_id and timestamp for faster lookup.
        db.cypher_query("CREATE INDEX generic_p21_ts IF NOT EXISTS FOR (n:GenericNode) ON (n.p21_id, n.timestamp)")
        # Wait until the index is online.
        db.cypher_query("CALL db.awaitIndexes()")

        # Load IFC model.
        print("Loading IFC model.")
        model = ifcopenshell.open(ifc_path)

        # Retrieve IFC entities that will be PrimaryNodes, same for ConnectionNodes.
        primary_entities = model.by_type("IfcObjectDefinition") + model.by_type("IfcPropertyDefinition")
        connection_entities = model.by_type("IfcRelationship")
        prim_conn_entities = primary_entities + connection_entities

        prim_conn_ids = {e.id() for e in prim_conn_entities}
        secondary_entities = [e for e in model if e.id() != 0 and e.id() not in prim_conn_ids]

        # Create a list of node dicts that can be used for batch creation with UNWIND.
        primary_nodes = [{
            "GlobalId": e.GlobalId,
            "EntityType": e.is_a(),
            "p21_id": f"#{e.id()}",
            "timestamp": timestamp
        } for e in primary_entities]

        connection_nodes = [{
            "GlobalId": e.GlobalId,
            "EntityType": e.is_a(),
            "p21_id": f"#{e.id()}",
            "timestamp": timestamp
        } for e in connection_entities]

        secondary_nodes = [{
            "EntityType": e.is_a(),
            "p21_id": f"#{e.id()}",
            "timestamp": timestamp
        } for e in secondary_entities]

        inline_patterns = []

        # Bulk creation queries.
        query_primary_nodes = """
        UNWIND $batch AS props
        CREATE (n:PrimaryNode:GenericNode:Node)
        SET n = props
        """

        query_connection_nodes = """
        UNWIND $batch AS props
        CREATE (n:ConnectionNode:GenericNode:Node)
        SET n = props
        """

        query_secondary_nodes = """
        UNWIND $batch AS props
        CREATE (n:SecondaryNode:GenericNode:Node)
        SET n = props
        """

        # Bulk creation.
        print(f"Creating {len(primary_nodes)} PrimaryNodes.")
        self.batch_cypher_query(query_primary_nodes, primary_nodes, batch_size)

        print(f"Creating {len(connection_nodes)} ConnectionNodes.")
        self.batch_cypher_query(query_connection_nodes, connection_nodes, batch_size)

        print(f"Creating {len(secondary_nodes)} SecondaryNodes")
        self.batch_cypher_query(query_secondary_nodes, secondary_nodes, batch_size)

        # Process IFC attributes into collections for node attributes and relationships.
        print("Collecting attributes and relationships.")
        props_map = {}
        relationships = []
        related_nodes = set()

        for entity in model:
            self.process_ifc_attributes(entity, timestamp, props_map, relationships, related_nodes, inline_patterns)

        # Bulk update primitive attributes on nodes.
        print(f"Updating attributes on {len(props_map)} nodes.")
        attributes_list = [{"p21_id": p21_id, "timestamp": timestamp, "properties": properties} for p21_id, properties in props_map.items()]
        query_properties = """
        UNWIND $batch AS row
        MATCH (n:GenericNode {p21_id: row.p21_id, timestamp: row.timestamp})
        SET n += row.properties
        """
        self.batch_cypher_query(query_properties, attributes_list, batch_size)

        # Bulk create relationships from IFC attributes.
        print(f"Creating {len(relationships)} relationships.")
        query_relationships = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.source_p21_id, timestamp: r.timestamp})
        MATCH (b:GenericNode {p21_id: r.target_p21_id, timestamp: r.timestamp})
        CREATE (a)-[:rel {rel_type: r.rel_type, list_index: r.list_index}]->(b)   
        """
        self.batch_cypher_query(query_relationships, relationships, batch_size)

        # Bulk create InlinePatterns
        print(f"Creating {len(inline_patterns)} InlineNode patterns.")
        query_inline_patterns = """
        UNWIND $batch AS r
        MATCH (a:GenericNode {p21_id: r.relation.source_p21_id, timestamp: r.props.timestamp})
        CREATE (b:InlineNode:Node)
        SET b = r.props
        CREATE (a)-[:rel {rel_type: r.relation.rel_type, list_index: r.relation.list_index}]->(b)
        """
        self.batch_cypher_query(query_inline_patterns, inline_patterns, batch_size)

        print("Finished IFC parsing.")