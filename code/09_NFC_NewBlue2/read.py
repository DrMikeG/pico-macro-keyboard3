import mfrc522
import board
import time
from os import uname


def do_read():

    rfid = mfrc522.MFRC522(sck=board.GP18, mosi=board.GP19, miso=board.GP16, cs=board.GP17, rst=board.GP22)
    
    print("")
    print("Place card before reader to read from address 0x08")
    print("")

    try:
      while True:
        if rfid.is_card():
            uid = rfid.read_card_serial()
            if uid:
                print(f"Card detected! UID: {[hex(x) for x in uid]}")
                # Authenticate and read the first block of data
                if rfid.authenticate(0x60, 8, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
                    data = rfid.read_block(8)
                    if data:
                        print(f"Block 8 data: {data}")
        time.sleep(1)

    except KeyboardInterrupt:
        print("Bye")

do_read()