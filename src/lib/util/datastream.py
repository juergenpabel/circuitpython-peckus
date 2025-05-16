from io import BytesIO as io_BytesIO
from msgpack import unpack as msgpack_unpack, \
                    pack as msgpack_pack
from traceback import print_exception as traceback_print_exception


class DataStream:

    def __init__(self, name: str):
        self.name = name


    def test(self, store: Any, offset: int, length: int) -> bool:
        try:
            msgpack_unpack(io_BytesIO(store[offset:offset+length]))
        except Exception as e:
            print(f"DataStream<{self.name}>.test(): {e}")
            traceback_print_exception(e)
            return False
        return True


    def load(self, store: Any, offset: int = 0, length: int = 0) -> Any:
        result = None
        if length == 0:
            length = len(store)
        try:
            result = msgpack_unpack(io_BytesIO(store[offset:offset+length]))
        except Exception as e:
            print(f"DataStream<{self.name}>.load(): {e}")
            traceback_print_exception(e)
        return result


    def save(self, data: Any, store: Any, offset: int = 0, length: int = 0) -> bool:
        if length == 0:
            length = len(store)
        try:
            bytestream = io_BytesIO()
            msgpack_pack(data, bytestream)
            data = bytestream.getvalue()
            store[offset:offset+len(data)] = data
        except Exception as e:
            print(f"DataStream<{self.name}>.save(): {e} (data is {len(bytestream.getvalue())} bytes, store is {length} bytes)")
            traceback_print_exception(e)
            return False
        return True

