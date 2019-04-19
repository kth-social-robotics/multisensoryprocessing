import unittest
from io import BytesIO

import numpy as np

from farmi.serialization import deserialize, deserialize_file, serialize


class TestSerialization(unittest.TestCase):
    def test_serializer(self):
        data = ["some strange stuff!", {"okay": ["coolio", "woho"]}, 4.44]

        serialized_data = serialize(data)

        deserialized_data = deserialize(serialized_data)

        self.assertEqual(data, deserialized_data)

    def test_serialization_of_numpy(self):
        data = np.random.random((10, 15, 20))

        serialized_data = serialize(data)
        deserialized_data = deserialize(serialized_data)

        self.assertTrue((data == deserialized_data).all())

    def test_serialization_of_numpy_in_file_serializer(self):
        data = np.random.random((10, 15, 20))

        outfile = BytesIO()
        outfile.write(serialize(("t", 1.2, data)))
        outfile.seek(0)

        deserialized_data = list(deserialize_file(outfile))

        self.assertTrue((data == deserialized_data[0][2]).all())

    def test_file_serializer(self):
        data = ["topic1", 4.231, ["some strange stuff!", {"okay": "coolio"}, 4.44]]
        data2 = ["topic2", 1.231, 2.312]
        data3 = ["topic3", 9.23, {2.0: ["list of things"]}]

        outfile = BytesIO()

        outfile.write(serialize(data))
        outfile.write(serialize(data2))
        outfile.write(serialize(data3))

        outfile.seek(0)

        deserialized_data = list(deserialize_file(outfile))

        self.assertEqual(data, deserialized_data[0])
        self.assertEqual(data2, deserialized_data[1])
        self.assertEqual(data3, deserialized_data[2])


if __name__ == "__main__":
    unittest.main()
