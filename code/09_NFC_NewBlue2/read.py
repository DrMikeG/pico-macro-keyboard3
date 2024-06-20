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
					print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))

	except KeyboardInterrupt:
		print("Bye")

do_read()