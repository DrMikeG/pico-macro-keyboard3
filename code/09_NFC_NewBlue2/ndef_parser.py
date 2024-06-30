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
def parse_ndef_record(bytes):
    header = bytes[0]
    tnf = header & 0x07
    type_length = bytes[1]
    
    index = 2
    sr_flag = header & 0x10 > 0x00
    if sr_flag:  # Short Record (SR flag is set)
        payload_length = bytes[index]
        index += 1
        id_length = 0
    else:  # Normal Record (SR flag is not set)
        payload_length = (bytes[index] << 24) | (bytes[index+1] << 16) | (bytes[index+2] << 8) | bytes[index+3]
        index += 4
        id_length = bytes[index] if header & 0x08 else 0
        index += 1 if header & 0x08 else 0
    
    type_ = bytes[index:index + type_length]
    index += type_length

    if id_length > 0:
        id_ = bytes[index:index + id_length]
        index += id_length
    else:
        id_ = b''

    payload = bytes[index:index + payload_length]

    return {
        "tnf": tnf,
        "type_length": type_length,
        "payload_length": payload_length,
        "id_length": id_length,
        "type": type_,
        "id": id_,
        "payload": payload,
        "sr_flag": sr_flag
    }

"""
Given the variability in memory layouts, it is common practice to search for the start of the NDEF message rather than assuming it starts at the very beginning. 
The NDEF message is usually identified by looking for specific header bytes that conform to the NDEF record format.

The NDEF record header typically starts with a byte where:
- the TNF (Type Name Format) is between 0x00 and 0x07
- the MB (Message Begin) flag is set (which is the first bit in the byte).

I am only supporting TNF 1 for now.

"""
def find_ndef_record_start(byteArray):
    
    for i in range(len(byteArray)):
        # TNF should be 0x01 and MB should be set
        if byteArray[i] & 0x07 == 0x01 and (byteArray[i] & 0x80):
            type_length = byteArray[i + 1]
            if type_length <= 255:  # Ensure type length is reasonable
                return i
        
    raise ValueError("NDEF record start not found")