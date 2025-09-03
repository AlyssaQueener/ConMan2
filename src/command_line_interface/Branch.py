from neo4j_core.neo4j_connection import Neo4jConnection
from version_timeline.VersionTimeline import VersionTimeline

version_timeline = VersionTimeline()
Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

def branch(project_id: str, branch_name: str):

    version_timeline.branch(project_id, branch_name)