from neo4j_core.neo4j_connection import Neo4jConnection

def reset():

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    # Direct CYPHER query to delete all nodes and relationships in the db.
    query = f"""
    MATCH (n)
    DETACH DELETE n
    """
    Neo4jConnection().cypher_query(query)

    print(f"Database has been emptied.")