from neomodel import db

class Neo4J_Helper:

    def truncate_db(self, batch_size:int):
        print(f"Deleting {db.cypher_query("MATCH (n) RETURN COUNT(n)")[0][0][0]} nodes.")
        query_truncate_db = """
            CALL apoc.periodic.commit("
            MATCH (n) 
            WITH n LIMIT $limit 
            DETACH DELETE n 
            RETURN count(*)
            ", {limit:$batch_size});
        """
        db.cypher_query(query_truncate_db, {"batch_size":batch_size})

    def bulk_cypher_query(self, query:str, rows:list, batch_size:int):
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            db.cypher_query(query, {"batch": batch})
            