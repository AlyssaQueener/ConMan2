import ifcopenshell
import ifcopenshell.api.project

import ast

from neo4j_core.neo4j_model import GenericNode, PrimaryNode, SecondaryNode, ConnectionNode, InlineNode

class IfcGraphInterface:

    ########################
    ### Helper Functions ###
    ########################

    def process_ifc_attribute(self, node, key, val, timestamp, list_index=0):
        """
        Process an IFC entity's attribute to either be handled as a connection to another node or a node attribute.

        @param node: The node that models the current IFC entity in Neo4J.
        @param key: The attibute name, will either be an attribute name or the name of the relation to another node.
        @param val: The attribute value, will either be the attribute value or the related node.
        @param timestamp: Required to only interact with nodes from the correct IFC source model.
        """

        # Check if the attribute value is an IFC entity itself.
        if isinstance(val, ifcopenshell.entity_instance):
            # If the entity id is 0, it is an inline entity like IfcArcIndex or IfcPlaneAngleMeasure.
            if val.id() == 0:
                # Create a new node of type InlineNode for inline entities
                ref = InlineNode(EntityType=val.is_a(),
                                timestamp=timestamp).save()
                # Create a connection from the node to the newly created inline node.
                node.relation_to.connect(ref, {"rel_type": key, "list_index": list_index})
                # Recursively handle the inline node's wrappedValue (holds the data like "(5,6,2)" for "IfcArcIndex(5,6,1)"). Safety in case of nested inline attributes.
                self.process_ifc_attribute(ref, "wrappedValue", val.wrappedValue, timestamp)
                # Save new inline node.
                ref.save()
            else:
                # ID is not 0, so the attribute entity already exists in neo4j.
                ref = GenericNode.nodes.get(p21_id=f"#{val.id()}", timestamp=timestamp)
                # Create a realtion from node to related node
                node.relation_to.connect(ref, {"rel_type": key, "list_index": list_index})
        # Check if attribute value is a list. This list can comprise primitives, entities, or lists of either.
        elif isinstance(val, (tuple, list)):
            # Check if any list item is itself an IFC entity.
            if any(isinstance(x, ifcopenshell.entity_instance) for x in val):
                # Recursively call function to handle list elements correctly.
                for i, x in enumerate(val):
                    self.process_ifc_attribute(node, key, x, timestamp, list_index=i)
            # If no IFC entities in list, save list as a string. An example is a n IfcCaresianPointList3D. This works because (nested) lists can be interpreted using ast package when parsing it back to IFC.     
            else:
                setattr(node, key, str(val))
        # Assign "$" to non-assigned attributes, as neo4j does not store these attributes at all otherwise.
        # By extension: setting a node attribute (e.g. node.Name = None) it will remove it from the node completely.
        elif val is None:
            setattr(node, key, "$")
        # If attribute value is a primitive, store it directly.
        else:
            setattr(node, key, val)


    def process_node_attribute(self, ifc_entity, key, val):
        """
        Process node attributes. These are the directly attached primtive node properties that are directly attached to a neo4j node.

        @param ifc_entity: An ifcopenshell model entity.
        @param key: The key of the node attribute.
        @param val: The attribute value. This can either be a primitive type, a string, or a stringified list of primitives.
        """
        # print(f"Processing {ifc_entity, key, val}")
        if val == "$":
            pass
        # Check if it is any primitive but a string. If so, leave it.
        elif not isinstance(val, str):
            # Store the processed attribute in the IFC entity.
            setattr(ifc_entity, key, val)
        # Check if it is a list of primitives that was parsed as a string. If so, leave it.
        # While neo4j allows lists, it does not allow for nested lists, so every list is stored as a string for consistency.
        elif not val.startswith("(") or not val.endswith(")"):
            # Store the processed attribute in the IFC entity.
            setattr(ifc_entity, key, val)
        # If it is a stringified list of primitives, evaluate it back into a Python list.
        else:
            val = tuple(ast.literal_eval(val))
            # Store the processed attribute in the IFC entity.
            setattr(ifc_entity, key, val)

    def process_node_relation(self, model, ifc_entity, rel_type, related_nodes, id_mapping):
        """
        From the relations in neo4j, create entity attributes and inline attributes for every STEP IFC object.

        @param model: The parsed ifcopenshell IFC model.
        @param ifc_entity: The current IFC entity.
        @param rel_type: The name of the relation in neo4j which will become the attribute key in the STEP attribute.
        @param related_nodes: The list of nodes that are all connected via a relation with the rel_type name.
        @param id_mapping: A dictionary that maps the newly created STEP ids to the node ids.
        """
        # Create list for entities to then set as the attribute value.
        ents = []
        # Iterate over all nodes that are grouped under the rel_attribute in the dict. This means that initially, all these nodes were part of the same IFC attribute.
        for node, list_index in related_nodes:
            # Check if Inline node, if so, create new entity.
            if isinstance(node, InlineNode):
                ent = model.create_entity(node.EntityType)
                # WrappedValue is the actual input data of inline entities like "(6,5,1)" in "IfcArcIndex(6,5,1)". Process this like any other non-entity attribute.
                self.process_node_attribute(ent, "wrappedValue", node.wrappedValue)
                ents.append((ent, list_index))
            # If entity is a real STEP entity, get the existing IFC entity and append that to the list.
            else:
                ent = model.by_id(id_mapping[node.element_id])
                ents.append((ent, list_index))

        # Every attribute value is a list, for some attributes this datatype is correct. Others need single values.
        if len(ents) <= 1:
            # Required try block because if a list has only 1 entry, it might have to be passed as a list with one entry, or it may have to be passed as a single entry.
            try:
                setattr(ifc_entity, rel_type, ents[0][0])
            except:
                setattr(ifc_entity, rel_type, [ents[0][0]])
        # If multiple entities in the list, set the list as attribute value.
        else:
            # Sort the entity list by the list index before setting as attribute. This rebuilds the same order.
            ents_sorted = sorted(ents, key=lambda x: x[1])
            ents_final = [ent[0] for ent in ents_sorted]
            setattr(ifc_entity, rel_type, ents_final)



    ######################
    ### Main Functions ###
    ######################

    def ifc_2_graph(self, ifc_path:str, timestamp:str):
        """
        Generate a graph from an IFC file and save it to the Neo4j database.

        @param ifc_path: Path to the IFC file.
        @param timestamp: ID to keep track of what nodes in the graph belong to the same origin IFC file.
        """
        model = ifcopenshell.open(ifc_path)

        # First iteration over all STEP entities: Create nodes and add p21_id and timestamp for unambiguous entity to node mapping.
        for entity in model:
            if entity.is_a("IfcObjectDefinition") or entity.is_a("IfcPropertyDefinition"):
                PrimaryNode(GlobalId=entity.GlobalId,
                            EntityType=entity.is_a(),
                            p21_id=f"#{entity.id()}",
                            timestamp=timestamp).save()
            elif entity.is_a("IfcRelationship"):
                ConnectionNode(GlobalId=entity.GlobalId,
                                EntityType=entity.is_a(),
                                p21_id=f"#{entity.id()}",
                                timestamp=timestamp).save()
            elif entity.id() != 0: # For security. ID 0 is used for Inline Entities, see InlineNode
                SecondaryNode(EntityType=entity.is_a(),
                                p21_id=f"#{entity.id()}",
                                timestamp=timestamp).save()
            else: # Nothing created here because Inline IFC entities (e.g. IfcArcIndex) is not in model entites, still listed for better understandability
                InlineNode(EntityType=entity.is_a(),
                                timestamp=timestamp).save()
                
        # Second iteration over all STEP entities: Go through all attributes and either append them to the node or create relationships with other nodes.
        for entity in model:
            info = entity.get_info()

            node = GenericNode.nodes.get(p21_id=f"#{entity.id()}", timestamp=timestamp)

            # Iterate over all entity attributes
            for key, val in info.items():
                # Ignore any IDs or types as they are already saved in the node and must not be changed
                if key in ("GlobalId", "EntityType", "type", "p21_id", "id", "inline_id", "timestamp"):
                    continue
                # Call method to handle attributes, no matter if they are single or tuple of primitives or entities
                self.process_ifc_attribute(node, key, val, timestamp)
            # Save node with all created attributes and realtions
            node.save()

    def graph_2_ifc(self, ifc_path:str, timestamp:str):
        """
        Generate an IFC file from a graph stored in a Neo4J database.

        @param ifc_path: Target path of the generated IFC file.
        @param timestamp: ID to keep track of what nodes in the graph belong to the same origin IFC file.
        """
        model = ifcopenshell.api.project.create_file("IFC4")

        # Dictionary to map newly created IFC entities to their source node ids.
        id_mapping = {}

        # Per method call, only one IFC file is created from the nodes. Therefore, filter all nodes with the timestamp of that IFC file.
        # First iteraton: Create IFC entities (STEP entities with p21 id) from all nodes that are not Inline Nodes
        for node in GenericNode.nodes.filter(timestamp=timestamp):
            ifc_entity = model.create_entity(node.EntityType)
            # Add node id and id of new IFC entity to mapping for later use
            id_mapping[node.element_id] = ifc_entity.id()

            # Iterate over all node attributes. These are only primitive attributes and can therefore be appended to the new IFC entity independently of what other entities already exist in the model.
            for key, val in node.__properties__.items():
                # Check if the ifc entity has an attribute with the name of the node attribute. Make sure e.g. node id or p21_id is ignored.
                if key in ["TrueNorth"]:
                    continue
                if hasattr(ifc_entity, key):
                    # Call function that handles primitives or stringified (nested) list of primitives.
                    self.process_node_attribute(ifc_entity, key, val)

        # Second iteration: Go over all node relations (either to existing Step entities in the model or to inline attributes that will be created).
        for node in GenericNode.nodes.filter(timestamp=timestamp):
            # Find ifc entity for current neo4j graph using the dictionary.
            ifc_entity = model.by_id(id_mapping[node.element_id])
            # Create a dictionary to collect all related entities. This is important, because one entity attribute may be a list of entity references. So first group all nodes by their rel_type.
            relations_dict = {}

            # Iterate over all related nodes.
            for related_node in node.relation_to.all():
                # Rel type will be used as the attribute key.
                rel_type = node.relation_to.relationship(related_node).rel_type
                list_index = node.relation_to.relationship(related_node).list_index
                # Check if IFC entity has an attribute with the name of the rel_type
                if hasattr(ifc_entity, rel_type):
                    # Rel type already exists in dict? Append node to its value that is a list.
                    if rel_type in relations_dict:
                        relations_dict[rel_type].append([related_node, list_index])
                    # Rel type appears for the first time? Create new entry for that attribtue in the dict.
                    else:
                        relations_dict[rel_type] = [[related_node, list_index]]

            # Iterate over the dictionary and process the lists of related nodes
            for rel_type, related_nodes in relations_dict.items():
                self.process_node_relation(model, ifc_entity, rel_type, related_nodes, id_mapping)
        # Save the IFC model to file.
        model.write(ifc_path)

    @staticmethod
    def get_project_id_from_timestamp(timestamp: str):
        try:
            project = PrimaryNode.nodes.get(EntityType="IfcProject", timestamp=timestamp)
            return project.GlobalId
        except Exception as e:
            print(f"Error retrieving project ID for timestamp {timestamp}: {e}")
            return None
        
    @staticmethod
    def get_project_id_from_ifc_path(ifc_path: str):
        try:
            model = ifcopenshell.open(ifc_path)
            project = model.by_type("IfcProject")[0]
            return project.GlobalId
        except Exception as e:
            print(f"Error retrieving project ID from IFC file {ifc_path}: {e}")
            return None
    
    @staticmethod
    def get_timestamp_from_project_id(project_id: str):
        try:
            project = PrimaryNode.nodes.filter(GlobalId=project_id, EntityType="IfcProject").all()
            return [p.timestamp for p in project]
        except Exception as e:
            print(f"Error retrieving latest timestamp for project ID {project_id}: {e}")
            return None