from neo4j_core.neo4j_connection import Neo4jConnection
from neo4j_core.neo4j_model import *
from operator import add

import json

change_library = ["tc", "rotation", "translation", "size", "rotation-2","size-2","room-size","translation-2"]
test_versions = ["v1-v2-test", "v2-v3-test", "v3-v4-test"]

all_results = []

for version in test_versions:
    modified = PrimaryNode.nodes.filter(encoded_modified=1.0, graph_type=version)
    
    for m in modified:
        modified_node = {
            "Entity": m.EntityType,
            "change_type": m.change_type,
            "graph_version": m.graph_type,
            "GlobalId": m.GlobalId,
            "top_k": []
        }
        
        for s in m.similar_to.all():
            if s.graph_type in change_library:
                rel = m.similar_to.relationship(s)
                
                if hasattr(s, "label"):
                    s_info = {
                    "EntityType": s.EntityType,
                    "change_type": s.change_type,
                    "label": s.label,
                    "graph_type": s.graph_type,
                    "score": rel.score
                }
                    if hasattr(s, "label_info"):
                        s_info["label_info"] = s.label_info
                    if hasattr(s, "label_info_material"):
                        s_info["label_info_material"] = s.label_info_material
                    modified_node["top_k"].append(s_info)
                
        
        modified_node["top_k"].sort(key=lambda x: x["score"], reverse=True)
        
        if modified_node["top_k"]:
            labels = [n["label"] for n in modified_node["top_k"]]
            modified_node["predicted"] = max(set(labels), key=labels.count)
        else:
            modified_node["predicted"] = "no_library_match"
        
        all_results.append(modified_node)

with open("knn_classification_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print(f"Wrote {len(all_results)} results to knn_classification_results.json")
        
