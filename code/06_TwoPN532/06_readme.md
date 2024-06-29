# Connecting multiple PN532

I have two PN532 breakouts, and a third on the way.

Looking at if I can connect more than one to a pi pico.

The two I have currently are connected via I2C.
On the pico, you can use the multiple pairs of SPI0 pins, but you need the devices to have different addresses on the bus.
The adafruit board has a fixed address ``0x48`` and there is no practical way of changing it.

The generic v3 board reports an address of ``I2C device addresses found: 0x24``

so there is potential for connecting both of them to one pico.`1

I tried connecting them both up and as far as I can tell, they are both reporting as address 0x24.


Pi Pico can have two independent I2C buses, which works around the problem that both boards have the same Bus ID.

Because pn532_1.read_passive_target(timeout=0.1) is a blocking call, we have to reduce the timeout to that the two boards interleave their checks.

So now I have both I2C boards connected and reading at the same time on one Pico.

I can potentially add a third on SPI now.

Obviously this is only useful for testing, but it shows there is nothing sus in the setup.

The big blue board is connected to GP1+0 and needs pullups from 3v3.
The v3 red board is connected to GP3+2 and does not need pullups.

I did get a single read from a ring (smallest of 3 currently delivered) from the red board.



The key discovery today was that my phone is writing tags using:
 key_number=adafruit_pn532.adafruit_pn532.MIFARE_CMD_AUTH_B
 Which is not the default used by the examples.

 Once I discoevered this, I can authenticate and then dump the blocks on my writen cards and fobs.

 Using  key_number=adafruit_pn532.adafruit_pn532.MIFARE_CMD_AUTH_A I could only read the blank 'from the factory' cards.

 However, the rings (apart from the large cermaic) don't use mifare classic, they use mifare ultralight, which I don't think isn't yet supported in the adafruit library.

 It's only 137 bytes though, so I might stand a chance at writing my own parser if I can dump the bytes.
 I think these pages: https://learn.adafruit.com/adafruit-pn532-rfid-nfc/mifare probably have information on the commands I would need to send to the rings to read the chips.

 It's nothing secret, my phone can do it.
 https://learn.adafruit.com/adafruit-pn532-rfid-nfc/mifare#mifare-ultralight-cards-99493

 The data is writen into NDEF records: https://learn.adafruit.com/adafruit-pn532-rfid-nfc/ndef

 I'm going to switch back to trying to smaller blue reader with the mfrc522 library to see if I can get authentication working with that, now I've done it using adafruit.