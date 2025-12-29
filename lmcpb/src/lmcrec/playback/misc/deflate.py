"""Provide inflate decompress for deflate(d) stream/file"""

import zlib
from typing import BinaryIO, Optional, Union

CHUNK_SIZE = 65536


class Inflate:
    def __init__(self, file_or_stream: Union[str, BinaryIO]):
        self._f = None
        if isinstance(file_or_stream, str):
            self._f = open(file_or_stream, "rb")
            self._must_close = True
        else:
            self._f = file_or_stream
            self._must_close = False

        self._at_f_eof = False
        self._do = zlib.decompressobj()

    def read(self, n: Optional[int] = None) -> bytes:
        toread = None if n is None or n < 0 else n
        data = b""
        while toread is None or toread > 0:
            unconsumed = self._do.unconsumed_tail
            if not self._at_f_eof:
                need_n = CHUNK_SIZE - len(unconsumed)
                if need_n > 0:
                    b = self._f.read(need_n)
                    self._at_f_eof = not b
                    unconsumed += b
            chunk = self._do.decompress(unconsumed, 0 if toread is None else toread)
            if not chunk and self._at_f_eof:
                break
            if toread is not None:
                toread -= len(chunk)
            data += chunk
        return data

    def close(self):
        if self._must_close:
            self._f.close()
            self._must_close = False

    def __del__(self):
        self.close()
