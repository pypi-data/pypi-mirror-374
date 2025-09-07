import unittest
from mojangson import stringify, parse
from test_data import stringify_test_data


class TestMojangsonStringify(unittest.TestCase):
    def test_stringify(self):
        for original, expected in stringify_test_data:
            with self.subTest(original=original):
                result = stringify(parse(original))
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
