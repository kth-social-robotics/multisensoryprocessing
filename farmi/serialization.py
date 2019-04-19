import msgpack
import msgpack_numpy as m

m.patch()


def deserialize_file(f, legacy=False):
    return msgpack.Unpacker(f, raw=legacy, use_list=True)


def deserialize(data):
    return msgpack.unpackb(data, raw=False)


def serialize(data):
    return msgpack.packb(data, use_bin_type=True)
