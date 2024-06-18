I'm struggling to read the smart rings with the PN532 NFC RFID module V3 is built around NXP PN532.
It should work, but doesn't.

I also have a PN532 NFC/RFID controller breakout board - v1.6
Product ID: 364 in stock:

https://www.adafruit.com/product/364

So going to try with that.


```If you are using the breakout in I2C mode, you will also need to add two 1.5K pullups on the SCL/SDA lines, since the breakout and the Arduino don't include the pullups. Simply solder or add a 1.5K resistor between SCL and 3.3V, and SDA and 3.3V, and then connect the breakout as you normally would.```

https://learn.adafruit.com/adafruit-pn532-rfid-nfc/python-circuitpython


MiFare is one of the four 13.56MHz card 'protocols' (FeliCa is another well known one) All of the cards and tags sold at the Adafruit shop use the inexpensive and popular MiFare Classic chipset

NFC rings can indeed have dual frequency support, typically operating at both 13.56 MHz (which is standard for NFC communication) and 125 kHz (which is commonly used for proximity access control systems and older RFID technologies).

If you can read the NFC ring with your smartphone, it means the ring operates at 13.56 MHz. Smartphones are equipped with NFC readers that operate at this frequency, as it is the standard frequency for NFC communication.

Smartphone NFC Capability: Modern smartphones are designed to interact with NFC devices operating at 13.56 MHz.

Compatibility: If your phone can read the NFC ring, the ring must support 13.56 MHz, since this is the only frequency used by NFC in consumer devices like smartphones.

This confirms that your issue with the V3 board not reading the ring is likely related to the board's antenna design or tuning, rather than a frequency mismatch.



Understanding Dual Frequency NFC Rings
13.56 MHz Frequency:

This is the standard frequency used by NFC (Near Field Communication) technology.

NFC rings operating at 13.56 MHz are compatible with most modern NFC-enabled devices, such as smartphones, tablets, and certain access control systems.

They are capable of data transfer rates suitable for tasks like contactless payment, data exchange, and other NFC applications.

125 kHz Frequency:

This frequency is commonly used for older RFID (Radio Frequency Identification) systems and proximity access control cards.

NFC rings that support 125 kHz are often designed to work with older access control systems that use this frequency.

They are generally used for simpler tasks like unlocking doors or access to restricted areas.

The PN532 NFC module is capable of reading and interacting with NFC (Near Field Communication) tags and devices operating at the following frequencies:

13.56 MHz:

This is the primary frequency used by NFC technology worldwide.
The PN532 fully supports NFC communication at 13.56 MHz, including:
ISO/IEC 14443 Type A
ISO/IEC 14443 Type B
ISO/IEC 18092 (NFCIP-1) standards
FeliCa™ cards

125 kHz (optional through external antenna):

The PN532 can be optionally configured to support 125 kHz RFID communication.
This is typically achieved by using an external antenna tuned for 125 kHz frequencies.
The supported protocols include EM4100/4200 and other compatible RFID protocols operating at 125 kHz.

Summary of PN532 Frequency Capabilities:
Primary Frequency: 13.56 MHz for standard NFC operations.
Optional Frequency: 125 kHz with appropriate external antenna configuration.