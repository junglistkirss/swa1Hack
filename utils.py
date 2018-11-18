# config keys :
#   - essid
#   - password
import esp
import ujson


def get_machine_guid():
    return esp.flash_id()


def read_json(filename):
    with open(filename, 'r') as file:
        conf = ujson.loads(file.read())
    return conf


def write_json(datas, filename):
    with open(filename, 'w') as file:
        file.write(ujson.dumps(datas))
