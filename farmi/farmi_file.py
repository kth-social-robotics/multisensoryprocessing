import os
import shutil

import lz4.frame
from farmi.serialization import deserialize_file

ONE_GB = 1_073_741_824


class FarmiFile(object):
    """handles saving to a farmi file"""

    def __init__(self, file_name):
        self.file_name = file_name
        self.file_handle = None
        self.counter = 0
        self.file_timestamp = None
        self.should_create_new_file = True
        self.ready_to_compress = []

    def check_file_size(self):
        if self.file_handle and os.path.getsize(self.file_handle.name) > ONE_GB * 5:
            self.should_create_new_file = True

            compress_files = self.ready_to_compress[:]
            self.ready_to_compress = []

            for filename in compress_files:
                new_path = filename + ".lz4"
                with open(filename, "rb") as f_in, lz4.frame.open(
                    new_path, "wb"
                ) as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(f_in.name)

    def write(self, data=None, timestamp=None):
        if self.should_create_new_file:
            self._create_new_file(timestamp)

        self.file_handle.write(data)
        # not sure if we should flush each time..
        # self.file_handle.flush()

    def _create_new_file(self, timestamp=None):
        if not self.file_timestamp:
            self.file_timestamp = timestamp

        self.counter += 1
        if self.file_handle:
            self.ready_to_compress.append(self.file_handle.name)
            self.file_handle.close()

        self.file_handle = open(
            self.file_name.format(f"{self.file_timestamp}_{self.counter}"), "wb"
        )
        self.should_create_new_file = False

    @staticmethod
    def read(filename):
        with open(filename, "rb") as f:
            for value in deserialize_file(f):
                yield value

    def close(self):
        if self.file_handle:
            self.file_handle.close()
