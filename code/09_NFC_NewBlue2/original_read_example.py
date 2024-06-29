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

                (stat, raw_uid) = rdr.anticoll()

                if stat == rdr.OK:
                    print("New card detected")
                    print("  - tag type: 0x%02x" % tag_type)
                    print("  - uid     : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    print("")

                #▪▪ DATA ▪▪
                #▪ FORMAT ▪▪
                #NFC Well Known (0x01)
                #Defined by RFC 2141, RFC 3986
                #▪▪ TYPE ▪▪
                #T
                #▪▪ PAYLOAD (7 bytes) ▪▪
                

                # Iterate through all the blocks except for sector trailers
                for block in range(1, 64):  # Adjust the range as necessary
                    # Skip sector trailers (typically every 4th block starting from 0)
                    if block % 4 == 3:
                        continue
                    try:
                        data = rdr.read_text_record(block)
                        if data:
                            print(f"Block {block} data: {data}")
                    except Exception as e:
                        print(f"Error reading block {block}: {e}")

                # I know there is data writen on the card
                # let's read it
                # The steps in reading the text data are:
                # 1. Select the tag
                # 2. Authenticate the tag
                # 3. Read the data
                # 4. Print the data

                # In systems where tags might have different levels of access or permissions, selecting a tag can be the first step
                # in the process of authenticating and determining the level of access or operations permitted with that tag.
                # Assuming the rest of your code remains the same
                if rdr.select_tag(raw_uid) == rdr.OK:
                    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    # Start from block 4, the first block of sector 1
                    for block in range(4, 64, 4):  # Adjust the range as necessary
                        if rdr.auth(rdr.AUTHENT1A, block, key, raw_uid) == rdr.OK:
                            data = rdr.read_text_record(block)
                            if data:
                                print(f"Block {block} data: {data}")
                                break  # Exit the loop if data is found
                            rdr.stop_crypto1()
                        else:
                            print(f"Authentication error for block {block}")

    except KeyboardInterrupt:
        print("Bye")
        
do_read()