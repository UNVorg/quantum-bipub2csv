import os
import json

def get_configs():
    script_dir = os.path.dirname(__file__)
    try:
        with open(os.path.join(script_dir, 'configs.json')) as json_file:
            data = json.load(json_file)
            return data
    except:
        return {}

def get_storage_connection_string():
    cfg = get_configs()
    return cfg['storage_connection_string']

def get_oracle_auth():
    cfg = get_configs()
    return cfg['oracle_auth']
