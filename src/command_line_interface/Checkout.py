from version_timeline.VersionTimeline import VersionTimeline
from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface

version_timeline = VersionTimeline()
Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

def checkout(project_id: str, branch_updt: str, timestamp_updt: str):
    
    version_timeline.checkout(project_id, branch_updt, timestamp_updt)