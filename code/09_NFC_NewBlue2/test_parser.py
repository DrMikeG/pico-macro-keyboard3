import unittest
from ndef_parser import parse_byte_into_record_header, parse_uid, parse_byte_array_into_records

class TestParseUID(unittest.TestCase):

    ''' test data
        Ring (MIFARE Ultralight detected)
        Serial Number=(88:04:e7:c2)
        Page 0x04 data: [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105]
        Page 0x08 data: [107, 101, 254, 0, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Page 0x0c data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    '''

    def int_array_to_bytes(self, int_array):
        return bytes(int_array)
    
    def test_parse_pages_into_records(self):
        bytes = self.int_array_to_bytes([1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105, 107, 101, 254, 0, 254])
        record_header = parse_byte_into_record_header(bytes[0])
        self.assertEqual(record_header["tnf"], 1)    
        
        

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