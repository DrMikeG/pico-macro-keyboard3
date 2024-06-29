import mfrc522
import board

from os import uname

def do_read():

    rdr = mfrc522.MFRC522(sck=board.GP18, mosi=board.GP19, miso=board.GP16, cs=board.GP17, rst=board.GP22)

    print("")
    print("Place card before reader to read from address 0x08")
    print("")

    try:
        while True:

            (stat, tag_type) = rdr.request(rdr.REQIDL)

            if stat == rdr.OK:

                # Anti-collision, return the 4 bytes Serial number of the card
                # the final byte is the check byte
                (stat, raw_uid) = rdr.anticoll()

                if stat == rdr.OK:

                    if (tag_type == rdr.MIFARE_CLASSIC):
                        print("\nCard or Fob (MIFARE Classic detected)")
                        # print out the 4 byte UID of the card in the format
                        print("Serial Number=({:02x}:{:02x}:{:02x}:{:02x})".format(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))

                        if rdr.select_tag(raw_uid) == rdr.OK:
                            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                            block = 0
                            if rdr.auth(rdr.AUTHENT1B, block, key, raw_uid) == rdr.OK:
                                data = rdr.read(block)
                            if data:
                                print(f"Block {block} data: {data}")
                            rdr.stop_crypto1()
                        else:
                            print(f"Authentication error for block {block}")

                    elif (tag_type == rdr.MIFARE_ULTRALIGHT):
                        print("\nRing (MIFARE Ultralight detected)")
                        # print out the 4 byte UID of the card in the format
                        print("UDI=({:02x}:{:02x}:{:02x}:{:02x})".format(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))

                        if rdr.select_tag(raw_uid) == rdr.OK:

                            page_0 = rdr.read_page(0x00) # returns 16 bytes
                            print("Page 0x00 data: %s" % page_0)
                            
                            if len(page_0) > 7:
                                # byte 0,1,2 are serial number
                                # byte 3 is check byte 0
                                # byte 4,5,6,7 are serial number
                                # byte 8 is check byte 1
                                # byte 9 is internal
                                print("Serial Number=({:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x})".format(page_0[0],page_0[1],page_0[2],page_0[4],page_0[5],page_0[6],page_0[7]))
                                #Pages 0x04 to 0x0F are the user read/write area.
                            
                            pages_to_read = [0x04, 0x08, 0x0C]
                            for page_num in pages_to_read:
                                data = rdr.read_page(page_num)
                                if data is not None:
                                    print(f"Page 0x{page_num:02x} data: {data}")

                    else:
                        print("Unsupported tag type 0x%02x" % tag_type)   
                        print("  - uid     : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    

                

    except KeyboardInterrupt:
        print("Bye")
        
do_read()