from graph_diff.GraphDiff import GraphDiff
from graph_patch.GraphPatch import GraphPatch
from neo4j_core.neo4j_connection import Neo4jConnection
from version_timeline.VersionTimeline import VersionTimeline

version_timeline = VersionTimeline()

def checkout(timestamp_init: str, timestamp_updt: str):

    Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

    if version_timeline.timeline == {}:
        print("No timeline found. Please commit at least one version before checking out.")
        return None
    else:
        if version_timeline.get_project_id_from_timestamp(timestamp_init):
            project_id = version_timeline.get_project_id_from_timestamp(timestamp_init)
            start_index = version_timeline.timeline[project_id].index(timestamp_init)
            stop_index = version_timeline.timeline[project_id].index(timestamp_updt)
            if start_index > stop_index:
                step = -1
            else:
                step = 1
            for i in range(start_index, stop_index, step):
                if i == stop_index:
                    break
                ts_init = version_timeline.timeline[project_id][i]
                ts_updt = version_timeline.timeline[project_id][i + step]
                print(f"Applying patch from {ts_init} to {ts_updt}.")
                graph_patch = GraphPatch(ts_init, ts_updt)
                graph_patch.load_patch_from_file(path_sema=f"./patch_data/Patch_Sema_{ts_init}_{ts_updt}.json", path_topo=f"./patch_data/Patch_Topo_{ts_init}_{ts_updt}.json"                                       )
                graph_patch.apply_patch(ts_init, ts_updt)