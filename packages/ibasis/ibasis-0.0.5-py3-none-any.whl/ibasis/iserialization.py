from . import fio


# 旧版本有依赖，故保留


def dump_pkl(fpath, var_lis):
    fio.write_pkl(fpath, var_lis)


def load_pkl(fpath):
    return fio.read_pkl(fpath)


def dump_msgpack(path, data):
    fio.write_msgpack(path, data)


def load_msgpack(path):
    return fio.read_msgpack(path)
