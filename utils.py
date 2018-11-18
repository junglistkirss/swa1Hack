# config keys :
#   - essid
#   - password
import ujson
from machine import unique_id
from ubinascii import hexlify


def get_machine_guid():
    return hexlify(unique_id())


def read_json(filename):
    with open(filename, 'r') as file:
        conf = ujson.loads(file.read())
    return conf


def write_json(datas, filename):
    with open(filename, 'w') as file:
        file.write(ujson.dumps(datas))
