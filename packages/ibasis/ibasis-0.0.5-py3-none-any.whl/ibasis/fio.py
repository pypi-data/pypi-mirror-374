import json
import pickle
import msgpack
import traceback


def read(fpath, ftype):
    pass


def write(fpath, obj, ftype):
    pass


def write_pkl(fpath, var_lis):
    with open(fpath, 'wb') as f:
        pickle.dump(var_lis, f)


def read_pkl(fpath):
    with open(fpath, 'rb') as f:
        return pickle.load(f)


def write_msgpack(path, data):
    with open(path, "wb") as f:
        f.write(msgpack.packb(data))


def read_msgpack(path):
    with open(path, "rb") as f:
        data = msgpack.unpackb(f.read())
        return data


def read_json(fpath):
    try:
        f = open(fpath, 'r')
        data_dic = json.load(f)
    except Exception:
        print(f"读取文件失败: {fpath}")
        traceback.print_exc()
        data_dic = dict()
    return data_dic


def write_json(fpath, data, CustomEncoder=None):
    with open(fpath, 'w') as f:
        json.dump(data, f, cls=CustomEncoder)