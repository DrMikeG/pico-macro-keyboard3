import unittest
from ndef_parser import parse_uid

class TestParseUID(unittest.TestCase):

    def test_parse_valid_uid(self):
        raw_uid = [0xAB, 0xCD, 0xEF, 0x01, 0x78]  # Example UID with checksum
        expected = "ab:cd:ef:01"
        self.assertEqual(parse_uid(raw_uid), expected)

    def test_parse_empty_uid(self):
        raw_uid = []
        expected = ""
        self.assertEqual(parse_uid(raw_uid), expected)

    # Add more tests as needed

if __name__ == '__main__':
    unittest.main()