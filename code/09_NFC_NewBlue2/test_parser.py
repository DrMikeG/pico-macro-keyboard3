import unittest
from ndef_parser import parse_byte_into_record_header, extract_payload

import binascii

class NDEFRecord:
    def __init__(self, tnf, type_length, payload_length, id_length, type_, id_, payload):
        self.tnf = tnf
        self.type_length = type_length
        self.payload_length = payload_length
        self.id_length = id_length
        self.type = type_
        self.id = id_
        self.payload = payload

    @classmethod
    def from_bytes(cls, data):
        header = data[0]
        tnf = header & 0x07
        type_length = data[1]
        
        index = 2
        if header & 0x10:  # Short Record
            payload_length = data[index]
            index += 1
            id_length = 0
        else:  # Normal Record
            payload_length = (data[index] << 24) | (data[index+1] << 16) | (data[index+2] << 8) | data[index+3]
            index += 4
            id_length = data[index] if header & 0x08 else 0
            index += 1 if header & 0x08 else 0
        
        type_ = data[index:index + type_length]
        index += type_length

        if id_length > 0:
            id_ = data[index:index + id_length]
            index += id_length
        else:
            id_ = b''

        payload = data[index:index + payload_length]

        return cls(tnf, type_length, payload_length, id_length, type_, id_, payload)

class NDEFMessage:
    def __init__(self, records):
        self.records = records

    @classmethod
    def from_bytes(cls, data):
        index = 0
        records = []
        while index < len(data):
            record = NDEFRecord.from_bytes(data[index:])
            records.append(record)
            index += record.type_length + record.payload_length + record.id_length + 2
            if record.payload_length > 255:
                index += 4  # Adjust for long payload length field
        return cls(records)

def main():
    # Example NDEF message in hexadecimal form
    ndef_hex = "d1010d5402656e48656c6c6f20576f726c64"
    ndef_bytes = binascii.unhexlify(ndef_hex)

    message = NDEFMessage.from_bytes(ndef_bytes)
    for record in message.records:
        print(f"TNF: {record.tnf}")
        print(f"Type: {record.type}")
        print(f"Payload: {record.payload}")

if __name__ == "__main__":
    main()

def convert_to_hex(data):
    return ''.join(format(byte, '02x') for byte in data)

# Data for pages 4-7
page_4_7_data = [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105]

# Data for pages 8-12
page_8_12_data = [107, 101, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Convert to hex
page_4_7_hex = convert_to_hex(page_4_7_data)
page_8_12_hex = convert_to_hex(page_8_12_data)

print(f"Page 4-7 data (hex): {page_4_7_hex}")
print(f"Page 8-12 data (hex): {page_8_12_hex}")

# Output the combined result for clarity
combined_hex = page_4_7_hex + page_8_12_hex
print(f"Combined data (hex): {combined_hex}")

"""
Page 4-7 data (hex): 0103a00c34030bd101075402656e6d69
Page 8-12 data (hex): 6b65fe00000000000000000000000000
Combined data (hex): 0103a00c34030bd101075402656e6d696b65fe00000000000000000000000000
"""

"""
The NDEF record header typically starts with a byte where the TNF (Type Name Format) is between 0x00 and 0x07, and the MB (Message Begin) flag is set (which is the first bit in the byte).
We can identify the start of the NDEF record by looking for a byte that matches the NDEF record header format. In the provided data, we see d1 at position 8 (0-based index), which is a likely candidate for the start of an NDEF record:

Here, d1 in binary is 11010001:

MB (Message Begin) = 1 (set)
ME (Message End) = 0 (not set)
CF (Chunk Flag) = 0 (not set)
SR (Short Record) = 1 (set, indicating the payload length is a single byte)
IL (ID Length) = 0 (not set)
TNF (Type Name Format) = 001 (1, indicating a well-known type)

"""
def parse_ndef_record(data):
    header = data[0]
    tnf = header & 0x07
    type_length = data[1]
    
    index = 2
    if header & 0x10:  # Short Record (SR flag is set)
        payload_length = data[index]
        index += 1
        id_length = 0
    else:  # Normal Record (SR flag is not set)
        payload_length = (data[index] << 24) | (data[index+1] << 16) | (data[index+2] << 8) | data[index+3]
        index += 4
        id_length = data[index] if header & 0x08 else 0
        index += 1 if header & 0x08 else 0
    
    type_ = data[index:index + type_length]
    index += type_length

    if id_length > 0:
        id_ = data[index:index + id_length]
        index += id_length
    else:
        id_ = b''

    payload = data[index:index + payload_length]

    return {
        "tnf": tnf,
        "type_length": type_length,
        "payload_length": payload_length,
        "id_length": id_length,
        "type": type_,
        "id": id_,
        "payload": payload
    }

# Convert the hex string to bytes
ndef_hex = "0103a00c34030bd101075402656e6d696b65fe00000000000000000000000000"
ndef_bytes = bytes.fromhex(ndef_hex)

# NDEF record starts at position 8 (0-based index)
ndef_record_bytes = ndef_bytes[8:]

# Parse the NDEF record
parsed_record = parse_ndef_record(ndef_record_bytes)

print(f"TNF: {parsed_record['tnf']}")
print(f"Type Length: {parsed_record['type_length']}")
print(f"Payload Length: {parsed_record['payload_length']}")
print(f"ID Length: {parsed_record['id_length']}")
print(f"Type: {parsed_record['type']}")
print(f"ID: {parsed_record['id']}")
print(f"Payload: {parsed_record['payload']}")
print(f"Payload (ASCII): {parsed_record['payload'].decode(errors='ignore')}")



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
    test_bytes_02 = [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105, 107, 101, 254]

    def int_array_to_bytes(self, int_array):
        return bytes(int_array)

    def test_is_encode(self):
        # Example NDEF message in hexadecimal form
        ndef_hex = "d1010d5402656e48656c6c6f20576f726c64"
        ndef_bytes = binascii.unhexlify(ndef_hex)

        message = NDEFMessage.from_bytes(ndef_bytes)
        for record in message.records:
            print(f"TNF: {record.tnf}")
            print(f"Type: {record.type}")
            print(f"Payload: {record.payload}")


    def test_is_record_header_found(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        record_header = parse_byte_into_record_header(bytes[0])
        self.assertEqual(record_header["tnf"], 1)    
        

    def test_is_payload_found(self):
        bytes = self.int_array_to_bytes(self.test_bytes_01)
        payload = extract_payload(bytes)
        print("Payload:", payload)

# install and use python ndeflib