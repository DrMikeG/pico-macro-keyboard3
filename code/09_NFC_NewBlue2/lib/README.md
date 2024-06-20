# circuitpython-mfrc522
Circuitpython class to access the MFRC522 RFID reader

This is a port from [micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522) to Circuitpython to run on [Arduino Nano RP2040 Connect](https://docs.arduino.cc/hardware/nano-rp2040-connect).

Basic class to access RFID readers of the type [MFRC522](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf). 
This is basically a re-write of [this](https://github.com/mxgxw/MFRC522-python) Python port for the MFRC522. Stefan Wendler
tried to strip things down and make them more "pythonic" so the result is small enough to run on 
[Micropython](https://github.com/micropython/micropython) boards.

I adopted this to [Circuitpython](https://circuitpython.org/downloads) boards and tried the class on [Arduino Nano RP2040 Connect](https://docs.arduino.cc/hardware/nano-rp2040-connect)

## Usage

Put the modules ``mfrc522.py``, ``examples/read.py``, ``examples/write.py`` to the root of the flash FS on your board. 
 
I used the following pins for my setup:

| Signal    | GPIO RP2040  | Note                                 |
| --------- | ------------ | ------------------------------------ |
| SCK       | SCK          |                                      |
| MOSI      | MOSI         |                                      |
| MISO      | MISO         |                                      |
| RST       | D8           |                                      |
| CS        | D9           |Labeled SDA on most RFID-RC522 boards |

See also breadbord schematics or [Fritzing](./doc/Arduino_Nano_RP2040_RFID-RC522.fzz):
![Schematics](./doc/Arduino_Nano_RP2040_RFID-RC522_Breadboard.png)

Now enter the REPL you could run one of the two exmaples: 

For detecting, authenticating and reading from a card:
 
    import read
    read.do_read()
    
This will wait for a MifareClassic 1k card. As soon the card is detected, it is authenticated, and 
16 bytes are read from address 0x08.

For detecting, authenticating and writing to a card:

    import write
    write.do_write()

This will wait for a MifareClassic 1k card. As soon the card is detected, it is authenticated, and 
16 bytes written to address 0x08.
