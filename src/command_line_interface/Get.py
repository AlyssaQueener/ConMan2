from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from version_timeline.VersionTimeline import VersionTimeline
from neo4j_core.neo4j_connection import Neo4jConnection

def get(model_path: str, timestamp: str):

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    if model_path.endswith(".ifc"):
        ifc_graph_interface = IfcGraphInterface()
        ifc_graph_interface.graph_2_ifc(model_path, timestamp)