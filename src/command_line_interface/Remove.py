from neo4j_core.neo4j_connection import Neo4jConnection

def remove(timestamp: str):

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    # Direct CYPHER query to delete all nodes and relationships with the given timestamp
    query = f"""
    MATCH (n)
    WHERE n.timestamp = '{timestamp}'
    DETACH DELETE n
    """
    Neo4jConnection().cypher_query(query)