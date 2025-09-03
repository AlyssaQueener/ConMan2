from version_timeline.VersionTimeline import VersionTimeline
from neo4j_core.neo4j_connection import Neo4jConnection
from ifc_graph_interface.IfcGraphInterface import IfcGraphInterface

version_timeline = VersionTimeline()
Neo4jConnection(username="neo4j", password="password", hostname="localhost", port=7687)

def checkout(project_id: str, branch_init: str, branch_updt: str, timestamp_updt: str):
    
    version_timeline.checkout(project_id, branch_init, branch_updt, timestamp_updt)


    # if start_index > stop_index:
    #     step = -1
    # else:
    #     step = 1
    # for i in range(start_index, stop_index, step):
    #     if i == stop_index:
    #         break
    #     if start_index > stop_index:
    #         ts_init = self.timeline[project_id]["branches"][branch]["timestamps"][i + step]
    #         ts_updt = self.timeline[project_id]["branches"][branch]["timestamps"][i]
    #         graph_patch = GraphPatch(ts_updt, ts_init)
    #         print(f"Applying patch from {ts_updt} to {ts_init}.")
    #         graph_patch.load_patch_from_file(path_sema=f"./patch_data/Patch_Sema_{ts_init}_{ts_updt}.json", path_topo=f"./patch_data/Patch_Topo_{ts_init}_{ts_updt}.json"                                       )
    #         graph_patch.apply_patch(ts_updt, ts_init)
    #     else:
    #         ts_init = self.timeline[project_id]["branches"][branch]["timestamps"][i]
    #         ts_updt = self.timeline[project_id]["branches"][branch]["timestamps"][i + step]
    #         graph_patch = GraphPatch(ts_init, ts_updt)
    #         print(f"Applying patch from {ts_init} to {ts_updt}.")
    #         graph_patch.load_patch_from_file(path_sema=f"./patch_data/Patch_Sema_{ts_init}_{ts_updt}.json", path_topo=f"./patch_data/Patch_Topo_{ts_init}_{ts_updt}.json"                                       )
    #         graph_patch.apply_patch(ts_init, ts_updt)