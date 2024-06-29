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