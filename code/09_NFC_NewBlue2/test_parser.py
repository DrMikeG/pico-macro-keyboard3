import unittest
from ndef_parser import find_ndef_record_start, parse_ndef_record, has_text_ndef, get_text_ndef_string, parse_ndef_text_payload

class TestParseUID(unittest.TestCase):
    """
    Serial Number=(88:04:8e:e0)
    Page 0x04 data: [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105]
    Page 0x08 data: [107, 101, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    Serial Number=(88:04:e7:c2)
    Page 0x04 data: [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105]
    Page 0x08 data: [107, 101, 254, 0, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    Serial Number=(88:04:89:d7)
    Page 0x04 data: [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105]
    Page 0x08 data: [107, 101, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    """
    test_bytes_01 = [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105, 107, 101, 254, 0, 254]
    #                01 03  a0  0c  34 03  0b   d1 01 07  54 02   65   6e   6d   69   6b   65   fe 00   fe
    test_bytes_02 = [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105, 107, 101, 254]
    #                01 03  a0  0c  34 03  0b   d1 01 07  54 02   65   6e   6d   69   6b   65   fe

    def int_array_to_bytes(self, int_array):
        return bytes(int_array)

    def convert_to_hex(self, bytes_as_ints):
        return ''.join(format(byte, '02x') for byte in bytes_as_ints)

    def test_is_do_this(self):
        in_hex = self.convert_to_hex(self.test_bytes_01)
        print(f"Page 4-11 data (hex): {in_hex}")
        self.assertEqual(in_hex.find("d1"), 14)

    def test_is_starting_byte_findableA(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        foundStartingPosition = find_ndef_record_start(bytes)
        self.assertEqual(bytes[foundStartingPosition],209)
        self.assertEqual(foundStartingPosition, 7)

    def test_is_starting_byte_findableB(self):
        bytes = self.int_array_to_bytes(self.test_bytes_02)
        foundStartingPosition = find_ndef_record_start(bytes)
        self.assertEqual(bytes[foundStartingPosition],209)
        self.assertEqual(foundStartingPosition, 7)
    
    def test_is_record_header_found(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        foundStartingPosition = find_ndef_record_start(bytes)
        record = parse_ndef_record(bytes[foundStartingPosition:])

        self.assertEqual(record["tnf"], 1)  # TNF is 1 - Well Known Type
        self.assertEqual(record["type_length"], 1) # Type Length is 1
        self.assertEqual(record["sr_flag"], True) # Short Record Flag is set when PAYLOAD LENGTH field is 1 byte (8 bits/0-255) or less
        self.assertEqual(record["payload_length"], 7) # Payload Length is 7
        self.assertEqual(record["type"], b'T') # byte literal for 'T' character
        print(f"Payload: {record['payload']}")
        print(f"Payload (ASCII): {record['payload'].decode(errors='ignore')}")

    def test_bytes_01_has_text_ndef(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        self.assertTrue(has_text_ndef(bytes))

    def test_bytes_02_has_text_ndef(self):
        bytes = self.int_array_to_bytes(self.test_bytes_02)
        self.assertTrue(has_text_ndef(bytes))


    def test_decode_payload(self):
        payload = b'\x02enmike'
        decoded = parse_ndef_text_payload(payload)
        self.assertTrue(decoded['understood'])
        
    def test_get_raw_payload(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        foundStartingPosition = find_ndef_record_start(bytes)
        record = parse_ndef_record(bytes[foundStartingPosition:])
        self.assertEqual(record['payload'], b'\x02enmike')
    
    def test_bytes_01_get_text(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        foundStartingPosition = find_ndef_record_start(bytes)
        record = parse_ndef_record(bytes[foundStartingPosition:])
        #print(f"Payload: {record['payload']}")
        self.assertEqual(record['payload'], b'\x02enmike')
        decoded = parse_ndef_text_payload(record['payload'])
        self.assertTrue(decoded['understood'])
        decoded_text = decoded['text']
        self.assertEqual(decoded_text,"mike")
    
    def test_bytes_01_in_get_text_ndef_string(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        self.assertEqual(get_text_ndef_string(bytes), "mike")
    
    def test_bytes_02_get_text(self):
        bytes = self.int_array_to_bytes(self.test_bytes_02)
        self.assertEqual(get_text_ndef_string(bytes), "mike")
