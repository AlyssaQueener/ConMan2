"""
IFC4 One-Hot Encoding — DFS-ordered inheritance tree
-----------------------------------------------------
Reads the inheritance tree from ifc_schema_tree.py (DFS-ordered IDs)
and produces a pure one-hot encoding per entity.

Semantic proximity is already baked into the ID ordering:
  IfcWall (65), IfcWindow (68)          → close in hierarchy → close IDs
  IfcWall (65), IfcRelDefinesByType (414) → distant branches  → distant IDs

Output
------
  ifc_encodings.json    →  { "IfcWall": [0,0,...,1,...,0], ... }
  ifc_entity_index.json →  { "IfcRoot": 0, "IfcObjectDefinition": 1, ... }
"""

import json


# ---------------------------------------------------------------------------
# 1.  Flatten the nested tree into { name: id }
# ---------------------------------------------------------------------------
def _flatten(node: dict | int, name: str, index: dict):
    if isinstance(node, int):
        index[name] = node
        return
    index[name] = node["id"]
    for child_name, child_node in node["children"].items():
        _flatten(child_node, child_name, index)


def load_tree(path: str = "ifc_schema_tree.json") -> dict:
    with open(path) as f:
        tree = json.load(f)

    index = {}
    for root_name, root_node in tree.items():
        _flatten(root_node, root_name, index)
    return index


# ---------------------------------------------------------------------------
# 2.  Pure one-hot: single 1 at the entity's own DFS position
# ---------------------------------------------------------------------------
def build_one_hot(index: dict) -> dict[str, list[int]]:
    n = len(index)
    encodings = {}
    for entity, idx in index.items():
        vec = [0] * n
        vec[idx] = 1
        encodings[entity] = vec
    return encodings


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    index     = load_tree("src/ifc_schema/ifc_schema_tree.json")
    encodings = build_one_hot(index)

    # --- write outputs ---------------------------------------------------
    with open("ifc_encodings.json", "w") as f:
        json.dump(encodings, f, indent="\t")

    sorted_index = dict(sorted(index.items(), key=lambda kv: kv[1]))
    with open("ifc_entity_index.json", "w") as f:
        json.dump(sorted_index, f, indent="\t")

    print(f"[+] {len(encodings)} entities encoded  →  ifc_encodings.json")
    print(f"[+] Entity index                       →  ifc_entity_index.json")
    print(f"    Vector dimension: {len(index)}")

    # --- sanity: show a few entities and their positions -----------------
    print("\n  Sample entities and their 1-positions (DFS order):")
    print("  " + "-" * 45)
    for name in ["IfcRoot", "IfcObjectDefinition", "IfcObject",
                 "IfcWall", "IfcDoor", "IfcWindow",
                 "IfcRelationship", "IfcRelDefinesByType"]:
        if name in index:
            print(f"  {name:35s}  →  {index[name]}")