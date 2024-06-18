"""
  Interface RFid RC522 Reader using Maker Pi Pico and CircuitPython
  https://tutorial.cytron.io/2022/01/11/interface-rfid-rc522-reader-using-maker-pi-pico-and-circuitpython/
  
  Items:
  - Maker Pi Pico
    https://my.cytron.io/p-maker-pi-pico
  - Mifare RC522 RFID Kit
    https://my.cytron.io/p-mifare-rc522-rfid-kit
  - Grove - Relay
    https://my.cytron.io/p-grove-relay
  - USB Micro B Cable
    https://my.cytron.io/p-usb-micro-b-cable
  
  Libraries required from bundle (https://circuitpython.org/libraries):
  - simpleio.mpy
  
  References:
  - https://github.com/domdfcoding/circuitpython-mfrc522
  
  Last update: 11 Jan 2022 (tested with CircuitPython 7.1.0)
"""

import time
import board
import digitalio
import simpleio
import busio
import mfrc522

NOTE_C5 = 523
NOTE_G5 = 784
buzzer = board.GP18

relay = digitalio.DigitalInOut(board.GP3)
relay.switch_to_output()

sck = board.GP6
mosi = board.GP7
miso = board.GP4
spi = busio.SPI(sck, MOSI=mosi, MISO=miso)

cs = digitalio.DigitalInOut(board.GP5)
rst = digitalio.DigitalInOut(board.GP8)
rfid = mfrc522.MFRC522(spi, cs, rst)
rfid.set_antenna_gain(0x07 << 4)

print("\n***** Scan your RFid tag/card *****\n")

prev_data = ""
prev_time = 0
timeout = 1

while True:
    (status, tag_type) = rfid.request(rfid.REQALL)

    if status == rfid.OK:
        (status, raw_uid) = rfid.anticoll()

        if status == rfid.OK:
            rfid_data = "{:02x}{:02x}{:02x}{:02x}".format(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])

            if rfid_data != prev_data:
                prev_data = rfid_data

                print("Card detected! UID: {}".format(rfid_data))

                if rfid_data == "cc40b773":
                    simpleio.tone(buzzer, NOTE_C5, 0.08)
                    simpleio.tone(buzzer, NOTE_G5, 0.08)

                    time.sleep(1)
                    print("Activate relay for 5 seconds")
                    relay.value = True
                    time.sleep(5)
                    relay.value = False

                else:
                    simpleio.tone(buzzer, NOTE_C5, 0.3)

            prev_time = time.monotonic()

    else:
        if time.monotonic() - prev_time > timeout:
            prev_data = ""