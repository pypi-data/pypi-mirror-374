import unittest
from mojangson import normalize
from test_data import stringify_test_data


class TestMojangsonStringify(unittest.TestCase):
    def test_normalize(self):
        for original, expected in stringify_test_data:
            with self.subTest(original=original):
                result = normalize(original)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
