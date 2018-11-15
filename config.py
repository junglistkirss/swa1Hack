# config keys :
#   - essid
#   - password
import esp
import ujson

GUID = esp.flash_id()

CONF_FILE = 'conf.json'


def read_config():
    with open(CONF_FILE, 'r') as file:
        conf = ujson.loads(file.read())
    return conf


def write_config(conf_dict):
    with open(CONF_FILE, 'w') as file:
        file.write(ujson.dumps(conf_dict))
