import networkx as nx 
import json

class networkxConnection: 

    def __init__(self):
        self.graph = nx.MultiDiGraph() 

    def save_graph(self, filename):
        """Serialize a graph to disk using JSON.

        Parameters
        ----------
        filename : str
            Path to the file where the graph will be written in JSON format.

        Notes
        -----
        Converts the NetworkX graph to a node-link format for JSON serialization.
        """
        data = nx.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_graph(self, filename):
        """
        Load a previously saved graph from the given JSON file path
        and assign it to the instance's `graph` attribute.

        Parameters
        ----------
        filename : str
            Path of the file containing the serialized graph object in JSON format.

        Raises
        ------
        OSError, IOError
            If the file cannot be opened for reading.
        json.JSONDecodeError
            If the file's contents are not valid JSON.

        Notes
        -----
        Expects the JSON file to be in NetworkX node-link format.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data, directed=True)

