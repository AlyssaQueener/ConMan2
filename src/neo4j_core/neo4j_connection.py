from neomodel import config, db

class Neo4jConnection:

    """
    Class that handles database connection. Only needed when running direct CYPHER queries, as neomodel handles db interaction internally.
    An instance of this class can be used for CYPHER queries using <instance_name>.cypher_query("<cypher_query>").
    """

    def __init__(self, username: str="neo4j", password: str="password", hostname: str="localhost", port: int=7687):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port

        config.DATABASE_URL = f"bolt://{self.username}:{self.password}@{self.hostname}:{self.port}"

    def __getattr__(self, name):
        return getattr(db, name)