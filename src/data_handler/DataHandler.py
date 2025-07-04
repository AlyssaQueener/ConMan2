import json
import hashlib



class DataHandler:

    def path_to_hash(path):
        path_string = json.dumps(path)
        path_hash = hashlib.sha1(path_string.encode('utf-8')).hexdigest()
        return path_hash