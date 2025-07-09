class DataHandler:

    @staticmethod
    def path_to_string(path):
        # Just return the string representation directly
        parts = []
        for item in path:
            if isinstance(item, dict):
                dict_str = ','.join(f"{k}={v}" for k, v in sorted(item.items()))
                parts.append(f"[{dict_str}]")
            else:
                parts.append(str(item))
        
        return '|'.join(parts)
    
    @staticmethod
    def string_to_path(string):
        if not string:
            return []
        
        parts = string.split('|')
        path = []
        
        for part in parts:
            part = part.strip()  # Remove whitespace
            if part.startswith('[') and part.endswith(']'):
                # Dictionary
                dict_content = part[1:-1]
                if dict_content:
                    dict_obj = {}
                    # Handle comma-separated key=value pairs
                    pairs = dict_content.split(',')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Type conversion
                            if value.isdigit():
                                dict_obj[key] = int(value)
                            elif value == 'None':
                                dict_obj[key] = None
                            elif value.lower() in ['true', 'false']:
                                dict_obj[key] = value.lower() == 'true'
                            else:
                                dict_obj[key] = value
                    path.append(dict_obj)
                else:
                    path.append({})
            else:
                # Regular value
                if part.isdigit():
                    path.append(int(part))
                elif part == 'None':
                    path.append(None)
                else:
                    path.append(part)
        
        return path
