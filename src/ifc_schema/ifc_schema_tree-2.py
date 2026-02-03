"""
IFC4 Schema Inheritance Tree — rooted at IfcRoot
-------------------------------------------------
Uses declaration_by_name() + .subtypes() recursion,
matching the API surface that actually works in ifcopenshell.

Usage:
    pip install ifcopenshell
    python ifc_schema_tree.py

Output:
    ifc_schema_tree.json
"""

import json
import ifcopenshell


def build_ifc4_tree() -> dict:
    schema = ifcopenshell.schema_by_name("IFC4")

    # Sequential ID counter shared across the entire DFS
    counter = {"n": 0}

    def _node(entity_name: str) -> int | dict:
        """
        Recursively build the tree starting from entity_name.
        Uses declaration_by_name() to get the declaration object,
        then .subtypes() to get its direct children.

        • leaf  (no subtypes) → bare int  (the id)
        • branch             → { "id": <int>, "children": { … } }
        """
        current_id = counter["n"]
        counter["n"] += 1

        # Resolve the declaration and ask for direct subtypes
        decl   = schema.declaration_by_name(entity_name)
        kids   = sorted(decl.subtypes(), key=lambda d: d.name())

        if not kids:
            return current_id               # leaf — just the id

        return {
            "id": current_id,
            "children": {child.name(): _node(child.name()) for child in kids},
        }

    # Single entry point — IfcRoot
    tree = {"IfcRoot": _node("IfcRoot")}
    return tree


# ---------------------------------------------------------------
if __name__ == "__main__":
    print("[*] Introspecting IFC4 schema …")
    tree = build_ifc4_tree()

    output_path = "ifc_schema_tree.json"
    with open(output_path, "w") as f:
        json.dump(tree, f, indent="\t")

    root_children = list(tree["IfcRoot"]["children"].keys())
    print(f"[+] Written to {output_path}")
    print(f"    IfcRoot direct children: {root_children}")
