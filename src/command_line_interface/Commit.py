from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch
from neo4j_core.neo4j_connection import Neo4jConnection
from version_timeline.VersionTimeline import VersionTimeline

version_timeline = VersionTimeline()

def commit(timestamp_init: str, timestamp_updt: str):

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    graph_diff = GraphDiff()
    graph_diff.run_diff(timestamp_init, timestamp_updt)

    graph_patch = GraphPatch(timestamp_init, timestamp_updt)
    graph_patch.create_patch(timestamp_init, timestamp_updt)

    version_timeline = VersionTimeline()
    version_timeline.add_commit_to_timeline(timestamp_updt)
    version_timeline.save()
