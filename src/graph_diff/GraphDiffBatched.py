from neomodel import db

class GraphDiffBatched:
    
    def run_diff(self, timestamp_init:str, timestamp_updt:str, batch_size:int):
        # Create indices, .
        db.cypher_query("CREATE INDEX primary_globalid_ts IF NOT EXISTS FOR (n:PrimaryNode) ON (n.GlobalId, n.timestamp)")
        db.cypher_query("CREATE INDEX connection_globalid_ts IF NOT EXISTS FOR (n:ConnectionNode) ON (n.GlobalId, n.timestamp)")
        db.cypher_query("CREATE INDEX generic_p21_ts_et IF NOT EXISTS FOR (n:GenericNode) ON (n.p21_id, n.timestamp, n.EntityType)")
        db.cypher_query("CREATE INDEX conn_p21_ts IF NOT EXISTS FOR (n:ConnectionNode) ON (n.p21_id, n.timestamp)")
        # Wait for indices to go online.
        db.cypher_query("CALL db.awaitIndexes()")

        # Find equivalences of PrimaryNodes.
        print("Linking equivalent PrimaryNodes.")
        query_primary_equivalence = """
        CALL apoc.periodic.iterate(
            "MATCH (a:PrimaryNode {timestamp: $ts_init})
            WHERE a.GlobalId IS NOT NULL RETURN a, a.GlobalId AS globalid",
            "MATCH (b:PrimaryNode {timestamp: $ts_updt, GlobalId: globalid})
            MERGE (a)-[:EQUIVALENT_TO]-(b)",
            {batchSize: $batch_size, parallel: false, params: {ts_init: $ts_init, ts_updt: $ts_updt, batch_size: $batch_size}}
        )
        """
        db.cypher_query(query_primary_equivalence, {"ts_init": timestamp_init, "ts_updt": timestamp_updt, "batch_size": batch_size})

        # Find SecondaryNode equivalences.
        print("Linking equivalent SecondaryNodes recursively from PrimaryNodes.")
        
        # Loop until no new nodes have been processed in a full pass.
        # This pattern is memory-safe because it processes nodes in batches without collecting all possible nodes into memory at once.
        while True:
            query_secondary_equivalence = """
            CALL () {
                MATCH (parent_a {timestamp: $ts_init})-[:EQUIVALENT_TO]-(parent_b {timestamp: $ts_updt})
                MATCH (parent_a)-[relation_a:RELATION_TO]->(child_a)
                WHERE child_a._visited IS NULL
                
                OPTIONAL MATCH (parent_b)-[relation_b:RELATION_TO {rel_type: relation_a.rel_type, list_index: relation_a.list_index}]->(child_b {EntityType: child_a.EntityType})
                WHERE child_b IS NULL OR child_b._visited IS NULL
                
                // Limit the number of rows to be processed in this transaction batch
                WITH child_a, child_b
                LIMIT $batch_size
                
                // Mark child_a as visited to exclude it from the next pass
                SET child_a._visited = true
                
                // If a partner child_b was found, create the link and mark it as visited.
                FOREACH (_ IN CASE WHEN child_b IS NOT NULL THEN [1] ELSE [] END |
                    MERGE (child_a)-[:EQUIVALENT_TO]-(child_b)
                    SET child_b._visited = true
                )
                RETURN count(child_a) as processed
            }
            RETURN sum(processed) as total_processed
            """
            results, _ = db.cypher_query(query_secondary_equivalence, {"ts_init": timestamp_init, "ts_updt": timestamp_updt, "batch_size": batch_size})
            
            # Escape while true loop if no new SecondaryNodes have been processed in last iteration.
            processed_count = results[0][0] if results and results[0] else 0
            if processed_count == 0:
                break
        
        # Remove visited property in memory-safe batches.
        query_remove_visited = """
        CALL apoc.periodic.iterate(
            "MATCH (n) WHERE n._visited IS NOT NULL RETURN n",
            "REMOVE n._visited",
            {batchSize: $batch_size, parallel: false}
        )
        """
        db.cypher_query(query_remove_visited, {"batch_size": batch_size})
        
        # Find ConnectionNode equivalences by GlobalId first.
        print("Linking equivalent ConnectionNodes based on GlobalId.")
        query_connection_equivalence_globalid = """
        CALL apoc.periodic.iterate(
            "MATCH (a:ConnectionNode {timestamp: $ts_init})
            WHERE a.GlobalId IS NOT NULL RETURN a, a.GlobalId AS globalid",
            "MATCH (b:ConnectionNode {timestamp: $ts_updt, GlobalId: globalid})
            MERGE (a)-[:EQUIVALENT_TO]-(b)",
            {batchSize: $batch_size, parallel: false, params: {ts_init: $ts_init, ts_updt: $ts_updt, batch_size: $batch_size}}
        )
        """
        db.cypher_query(query_connection_equivalence_globalid, {"ts_init": timestamp_init, "ts_updt": timestamp_updt, "batch_size": batch_size})
        
        print("Linking equivalent ConnectionNodes based on IoU of children.")
        # Phase 1: Pre-compute child counts for all relevant ConnectionNodes.
        print("  - Pre-computing child counts...")
        # Compute child counts in a memory-safe batched way.
        # Outer query MUST end with RETURN (not WITH). Return ids (scalars) to avoid shipping full nodes.
        query_connection_child_count = """
        CALL apoc.periodic.iterate(
            "MATCH (c:ConnectionNode)
             WHERE c.timestamp = $ts_init OR c.timestamp = $ts_updt
             WITH id(c) AS cid, size([(c)-[:RELATION_TO]->() | 1]) AS childCount
             RETURN cid, childCount",
            "MATCH (c) WHERE id(c) = cid SET c._childCount = childCount",
            {batchSize: $batch_size, parallel: false, params: {ts_init: $ts_init, ts_updt: $ts_updt}}
        )
        """
        db.cypher_query(query_connection_child_count, {"ts_init": timestamp_init, "ts_updt": timestamp_updt, "batch_size": batch_size})
        db.cypher_query("CREATE INDEX conn_childcount_ts IF NOT EXISTS FOR (n:ConnectionNode) ON (n._childCount, n.timestamp)")
        db.cypher_query("CALL db.awaitIndexes()")

        # Phase 2: Batched IoU matching using the pre-computed counts.
        print("  - Running batched IoU matching...")
        query_connection_equivalence_iou = """
        CALL apoc.periodic.iterate(
            // Outer query: Find all unpaired 'a' nodes with children.
            "MATCH (a:ConnectionNode {timestamp: $ts_init})
             WHERE NOT (a)-[:EQUIVALENT_TO]-() AND a._childCount > 0
             RETURN a",
            
            // Inner query: For each 'a', find candidate 'b's and check IoU.
            "// Use the pre-computed count for an efficient lookup.
             MATCH (b:ConnectionNode {timestamp: $ts_updt, _childCount: a._childCount})
             WHERE NOT (b)-[:EQUIVALENT_TO]-()

             // Now, for the small set of candidates, do the expensive IoU check.
             WITH a, b, a._childCount as count_a
             // Count common children
             MATCH (a)-[:RELATION_TO]->(ca)-[:EQUIVALENT_TO]->(cb)
             WHERE (b)-[:RELATION_TO]->(cb)
             WITH a, b, count_a, count(DISTINCT ca) as common
             
             // An IoU of 1.0 means the union equals the intersection.
             // For sets of the same size, this simplifies to common == count_a.
             WHERE common = count_a
             
             // Since multiple 'b' nodes could match, take the first one and stop.
             WITH a, b LIMIT 1
             MERGE (a)-[:EQUIVALENT_TO]-(b)",
            {batchSize: $batch_size, parallel: false, params: {ts_init: $ts_init, ts_updt: $ts_updt}}
        )
        """
        db.cypher_query(query_connection_equivalence_iou, {"ts_init": timestamp_init, "ts_updt": timestamp_updt, "batch_size": int(batch_size/10)})

        # Phase 3: Cleanup temporary properties and index.
        print("  - Cleaning up temporary properties...")
        query_remove_childcount = """
        CALL apoc.periodic.iterate(
            "MATCH (n) WHERE n._childCount IS NOT NULL RETURN n",
            "REMOVE n._childCount",
            {batchSize: $batch_size, parallel: false}
        )
        """
        db.cypher_query(query_remove_childcount, {"batch_size": batch_size})

        print("Diff completed.")