from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from version_timeline.VersionTimeline import VersionTimeline
from neo4j_core.neo4j_connection import Neo4jConnection

def add(model_path: str):

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    timestamp = VersionTimeline.create_timestamp()

    if model_path.endswith(".ifc"):
        ifc_graph_interface = IfcGraphInterface()
        ifc_graph_interface.ifc_2_graph(model_path, timestamp)