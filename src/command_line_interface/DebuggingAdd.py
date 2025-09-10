from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface
from neo4j_core.neo4j_connection import Neo4jConnection
from version_timeline.VersionTimeline import VersionTimeline

def debugging_add(model_path: str, timestamp: str):

    version_timeline = VersionTimeline()
    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    if model_path.endswith(".ifc"):
        project_id = IfcGraphInterface.get_project_id_from_ifc_path(model_path)
        ifc_graph_interface = IfcGraphInterface()
        print(f"Adding files from path {model_path} with timestamp {timestamp}. Project: {project_id}")
        ifc_graph_interface.ifc_2_graph(model_path, timestamp)