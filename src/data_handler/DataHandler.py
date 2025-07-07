import json
import hashlib



class DataHandler:

    @staticmethod
    def path_to_hash(path):
        # Just return the string representation directly
        parts = []
        for item in path:
            if isinstance(item, dict):
                dict_str = ','.join(f"{k}={v}" for k, v in sorted(item.items()))
                parts.append(f"[{dict_str}]")
            else:
                parts.append(str(item))
        
        return '|'.join(parts)