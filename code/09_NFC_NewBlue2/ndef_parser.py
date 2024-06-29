"""
The NDEF format is used to store and exchange information like URIs, plain text, etc., using a commonly understood format. 

NDEF Messages are the basic "transportation" mechanism for NDEF records, with each message containing one or more NDEF Records.

NDEF Records contain a specific payload, and have the following structure that identifies the contents and size of the record:

Bit 7     6       5       4       3       2       1       0
------  ------  ------  ------  ------  ------  ------  ------ 
[ MB ]  [ ME ]  [ CF ]  [ SR ]  [ IL ]  [        TNF         ]  
[                         TYPE LENGTH                        ]
[                       PAYLOAD LENGTH                       ]
[                          ID LENGTH                         ]
[                         RECORD TYPE                        ]
[                              ID                            ]
[                           PAYLOAD                          ]


 TNF Value    Record Type
  ---------    -----------------------------------------
  0x00         Empty Record
               Indicates no type, id, or payload is associated with this NDEF Record.
               This record type is useful on newly formatted cards since every NDEF tag
               must have at least one NDEF Record.
               
  0x01         Well-Known Record
               Indicates the type field uses the RTD type name format.  This type name is used
               to stored any record defined by a Record Type Definition (RTD), such as storing
               RTD Text, RTD URIs, etc., and is one of the mostly frequently used and useful
               record types.

TNF: Type Name Format Field
The Type Name Format or TNF Field of an NDEF record is a 3-bit value that describes the record type, and sets the expectation for the structure and content of the rest of the record. Possible record type names include:

IL: ID LENGTH Field
The IL flag indicates if the ID Length Field is present or not. If this is set to 0, then the ID Length Field is ommitted in the record.

SR: Short Record Bit
The SR flag is set to one if the PAYLOAD LENGTH field is 1 byte (8 bits/0-255) or less. This allows for more compact records.

CF: Chunk Flag
The CF flag indicates if this is the first record chunk or a middle record chunk.

ME: Message End
The ME flag indicates if this is the last record in the message.

MB: Message Begin
The MB flag indicates if this is the start of an NDEF message.               

"""
def parse_byte_into_record_header(byte):
    tnf = byte & 0x07  # TNF is the lower 3 bits
    flags = byte >> 3  # Flags are the upper 5 bits
    il = (flags & 0x01) > 0  # IL flag
    sr = (flags & 0x02) > 0  # SR flag
    me = (flags & 0x04) > 0  # ME flag
    cf = (flags & 0x08) > 0  # CF flag
    mb = (flags & 0x10) > 0  # MB flag
    return {"tnf": tnf, "il": il, "sr": sr, "me": me, "cf": cf, "mb": mb}

def extract_payload(byte_array):
    header = parse_byte_into_record_header(byte_array[0])
    # Calculate the start index of the Type Length field, which is right after the header
    index = 1
    type_length = byte_array[index]
    index += 1

    if header["sr"]:
        # If SR flag is set, payload length is 1 byte
        payload_length = byte_array[index]
        index += 1
    else:
        # If SR flag is not set, payload length could be more than 1 byte (not covered in this example)
        payload_length = 0  # Placeholder for extended logic

    if header["il"]:
        # If IL flag is set, next byte is ID Length
        id_length = byte_array[index]
        index += 1
    else:
        id_length = 0

    # Skip the Type and ID fields to reach the payload
    index += type_length + id_length

    # Extract the payload
    payload = byte_array[index:index+payload_length]
    return payload

# Example usage
bytes_data = [0xD1, 0x01, 0x07, 0x54, 0x02, 0x65, 0x6E, 0x48, 0x65, 0x6C, 0x6C, 0x6F]  # An example NDEF record
payload = extract_payload(bytes_data)
print("Payload:", payload)
# Example usage with your test data
bytes_data = [1, 3, 160, 12, 52, 3, 11, 209, 1, 7, 84, 2, 101, 110, 109, 105, 107, 101, 254, 0, 254]
find_ndef_record(bytes_data)

def parse_byte_array_into_records(byte_array):
    """
    Parse the byte array into NDEF records.

    :param byte_array: The byte array to parse.
    :return: A list of NDEF records.
    """
    header = parse_byte_into_record_header(byte_array[0])
    
    return None

def parse_byte_into_record_header(byte):
    # byte 0 is the record header
    # we need to use bit manipulation to extract the values of the flags
    # starting with the least significant bit 
    
    # prints the bits of byte 0 in byte_array
    for i in range(8):
        print(byte & (1 << i), end=" ")
    print("\n")

    # TNF: Type Name Format Field is bits 0,1 & 2
    tnf = byte & 0x07
    print(f"TNF: {tnf}")

    # IL: ID LENGTH Field is bit 3
    id_length_present = byte & 0x08
    print(f"ID Length Present: {id_length_present}")

    # SR: Short Record Bit is bit 4
    short_record = byte & 0x10
    print(f"Short Record: {short_record}")

    # CF: Chunk Flag is bit 5
    chunk_flag = byte & 0x20
    print(f"Chunk Flag: {chunk_flag}")

    # ME: Message End is bit 6
    message_end = byte & 0x40
    print(f"Message End: {message_end}")

    # MB: Message Begin is bit 7
    message_begin = byte & 0x80
    print(f"Message Begin: {message_begin}")

    # Parse the rest of the byte array
    # assign values to names members of the record
    record_header = {
        "tnf": tnf,
        "id_length_present": id_length_present,
        "short_record": short_record,
        "chunk_flag": chunk_flag,
        "message_end": message_end,
        "message_begin": message_begin
    }
    return record_header


def parse_uid(uid):
    """
    Parse the UID bytes and return a string representation.

    :param uid: The UID bytes.
    :return: The string representation of the UID.
    """
    return ":".join([hex(byte)[2:].zfill(2) for byte in uid])