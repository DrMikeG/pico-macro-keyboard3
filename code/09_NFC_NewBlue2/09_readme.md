# Different library

I'm still trying to get the MFRC522 boards to work under circuit python.

All the repos seems to actully be built on the same port - so trying this again:

https://gitlab.com/christopher_m/circuitpython-mfrc522/-/tree/master?ref_type=heads

And with some success.

I can read a card and a fob, but not a ring, using the big blue board and the pi pico.

I hope this is a software issue.

```
▪▪ DATA ▪▪
mike

▪▪ FORMAT ▪▪
NFC Well Known (0x01)
Defined by RFC 2141, RFC 3986

▪▪ TYPE ▪▪
T

▪▪ PAYLOAD (7 bytes) ▪▪
0x02 0x65 0x6E 0x6D 0x69 0x6B 0x65

▪▪ PAYLOAD (UTF8) ▪▪
enmike

▪▪ PAYLOAD (ASCII) ▪▪
enmike
```


Need to code up mifare ultralight support.


Memory Structure and Capacity:

MIFARE Ultralight: It has a much smaller memory capacity, typically around 64 or 153 bytes. 
All the rings report 137 bytes.
The memory is organized in pages instead of sectors and blocks.


Security:

MIFARE Classic: Offers more advanced security features compared to Ultralight. It uses a proprietary encryption method known as Crypto1 for authentication and communication. 
Each sector can be protected with two different keys (Key A and Key B) along with customizable access conditions.

MIFARE Ultralight: Designed for simpler applications with less stringent security requirements. 
It does not support the Crypto1 encryption but uses a simpler locking mechanism to protect its memory pages from unauthorized writing.

(Woop, no need for authentication support?)

The UID of the MF0ICU1 comprises 7 bytes


 

- 512-bit, organized in 16 pages with 4 bytes per page
- 32-bit user definable One-Time 
- 384-bit user Read/Write area (12 pages)

User memory is page 4 to 15 (x04 - x0f) bytes 0-3 

Pages 04h to 0Fh are the user read/write area.
After production the data pages are initialized to the following values:
• Page 04h is initialized to FFh
• Pages 05h to 15h are initialized to 00h


From the ultralight manual:

- The READ command needs the page address as a parameter.
- Only addresses 00h to 0Fh are decoded.
- The MF0ICU1 returns a NAK for higher addresses. 
- The MF0ICU1 responds to the READ command by sending 16 bytes starting from the page address defined by the command argument.
- For example; if address (ADR) is 03h then pages 03h, 04h, 05h, 06h are returned.
- A roll-back is implemented for example; if address (ADR) is 0Eh, then the contents of pages 0Eh, 0Fh, 00h and 01h are returned).

I want pages 4,5,6,7  8,9,10,11  12,13,14,15, so three reads in total.

cmd 0x30
arg 0x04
CRC C0 C1

Response is 16bytes plus CRC 0 and 1

Data integrity of 16-bit CRC, parity, bit coding, bit counting




The bytes received from request() and anticoll() functions in an RFID communication context, such as with an MFRC522 RFID reader, represent specific pieces of information exchanged between the reader and the RFID tag during the anti-collision and selection process. Here's a breakdown of what these bytes typically mean:

request() Response: [4, 0]
The request() function usually sends a REQA (Request command) or WUPA (Wake-Up command) to tags in the vicinity to initiate communication. 
The response [4, 0] is the ATQA (Answer To Request) from a tag, which is a 2-byte response indicating the tag's type and capabilities.

Byte 1 (4): This byte (in hexadecimal, 0x04) provides information about the tag's RFU (Reserved for Future Use), bit frame anticollision, and technology compatibility. For instance, 0x04 often indicates a tag compatible with ISO/IEC 14443-3 Type A.
Byte 2 (0): This byte is often used for additional technology or capability indicators. A value of 0 in this context typically means there are no additional capabilities or specific technologies indicated beyond what byte 1 specifies.
anticoll() Response: [121, 28, 80, 211, 230]
The anticoll() function is part of the anti-collision process, where the RFID reader identifies tags in the field to avoid collision (i.e., overlapping responses from multiple tags). The response from anticoll() is the UID (Unique Identifier) of the tag, along with a BCC (Block Check Character) for error checking.

Bytes 1-4 (121, 28, 80, 211): These four bytes represent the UID of the tag. The UID is a unique identifier assigned to each tag, used for identifying the tag during communication. The UID can vary in length (single, double, or triple size), but in this case, it appears to be a 4-byte (or 32-bit) UID, which is common.
Byte 5 (230): This is the BCC for error detection. The BCC is calculated from the UID bytes and is used by the reader to check for transmission errors. The calculation method for the BCC is defined in the ISO/IEC 14443-3 standard and typically involves XORing all the UID bytes together.
In summary, the request() function's response [4, 0] indicates a tag type and capabilities, specifically pointing to an ISO/IEC 14443-3 Type A tag with no additional capabilities indicated. The anticoll() function's response [121, 28, 80, 211, 230] provides the unique identifier of the tag and a checksum for error checking, essential for distinguishing and communicating with a specific tag in a field of multiple tags.

``` Fob:
Request status: 0, recv: [4, 0], bytes: 2 bits: 16
Anticoll status: 0, recv: [121, 28, 80, 211, 230], bytes: 5 bits: 40
  - tag type: 0x10
  - uid     : 0x791c50d3
Command sent for authentication: [97, 0, 255, 255, 255, 255, 255, 255, 121, 28, 80, 211]
Authentication status: 0
Block 0 data: [121, 28, 80, 211, 230, 8, 4, 0, 98, 99, 100, 101, 102, 103, 104, 105]

```


``` Ring:
Request status: 0, recv: [68, 0], bytes: 2 bits: 16
Anticoll status: 0, recv: [136, 4, 142, 224, 226], bytes: 5 bits: 40
  - tag type: 0x10
  - uid     : 0x88048ee0
Command sent for authentication: [97, 0, 255, 255, 255, 255, 255, 255, 136, 4, 142, 224]
Authentication status: 2
Authentication error for block 0
```

The responses [68, 0] and [136, 4, 142, 224, 226] from the rings can be explained as follows:

[68, 0] Response:
This is the ATQA (Answer To Request) from a tag, similar to the [4, 0] response but with a different byte 1 value.

Byte 1 (68): This byte (in hexadecimal, 0x44) provides information about the tag's RFU (Reserved for Future Use), bit frame anticollision, and technology compatibility. The value 0x44 often indicates a tag compatible with ISO/IEC 14443-3 Type A, similar to 0x04 but may represent a different set of capabilities or configurations specific to the tag's design.
Byte 2 (0): This byte is used for additional technology or capability indicators. A value of 0 in this context typically means there are no additional capabilities or specific technologies indicated beyond what byte 1 specifies.
[136, 4, 142, 224, 226] Response:
This is the response from the anticoll() function, indicating the UID (Unique Identifier) of the tag and a BCC (Block Check Character) for error checking.

Bytes 1-4 (136, 4, 142, 224): These four bytes represent the UID of the tag. The UID is a unique identifier assigned to each tag, used for identifying the tag during communication. This sequence of bytes is specific to the tag in question and is used to distinguish it from other tags.
Byte 5 (226): This is the BCC for error detection, calculated from the UID bytes. The BCC is used by the reader to check for transmission errors. The calculation method typically involves XORing all the UID bytes together, as defined in the ISO/IEC 14443-3 standard.
In summary, the [68, 0] response indicates a tag type and capabilities, pointing to an ISO/IEC 14443-3 Type A tag with specific capabilities or configurations indicated by the value 0x44. The [136, 4, 142, 224, 226] response provides the unique identifier of the tag and a checksum for error checking, crucial for distinguishing and communicating with a specific tag in a field of multiple tags.


Ok - so rings are tag type 0x44 and fobs are 0x04 - first byte returned by request()



Ok, so I've figured out how to get the bytes out of the pages on the rings.

I've written and unit tested a parser class for ndef records - although I've only tried it with Short Record (SR) form of the NDEF.

We have to search within the page bytes for the  NDEF record header, which typically starts with a byte where:
- the TNF (Type Name Format) is between 0x00 and 0x07
- the MB (Message Begin) flag is set (which is the first bit in the byte).
I am only supporting TNF 1-7 for now as 0 - Empty Record which isn't useful and makes it much harder to spot the correct starting point.

Then once I've identified I have a text NDEF record with a short record and simple payload length of less than 255bytes (has to be to fit on a ring)

I can parse the payload, which includes:
Status Byte 0x02: UTF-8 encoding: 0 (second least significant bit is 0)
Language Code Length: 2 (remaining bits, which is 2 in this case)
Language Code en: Next 2 bytes: 0x65 0x6e ('en' for English)
Text mike:

