"""
Example of reading from a card using the ``mfrc522`` module.
"""

# 3rd party
import board
from digitalio import DigitalInOut, Direction

# this package
import mfrc522

#sck
#mosi
#miso
#rst
#cs

#0
#1
#GND
#2
#3
miso = board.GP4  # Grey - This seems provable correct - behaviour changes on disconect 
cs = board.GP5 # Orange
#GND
sck = board.GP6 # Yellow
mosi = board.GP7 # Purple - This seems provable correct - behaviour changes on disconect
rst = board.GP8 # Brown
#9
#GND

def do_read():

    #def __init__(self, sck: Pin, mosi: Pin, miso: Pin, rst: Pin, cs: Pin):
	rdr = mfrc522.MFRC522(sck, mosi, miso, rst, cs)
	#rdr.set_antenna_gain(0x07 << 4)

	print('')
	print("Place card before reader to read from address 0x08")
	
	try:
		while True:
			(stat, tag_type) = rdr.request(rdr.REQIDL)
			
			if stat == rdr.OK:

				(stat, raw_uid) = rdr.anticoll()

				if stat == rdr.OK:
					print("New card detected")
					print("  - tag type: 0x%02x" % tag_type)
					print("  - uid\t : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
					print('')

					if rdr.select_tag(raw_uid) == rdr.OK:

						key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

						if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
							print("Address 8 data: %s" % rdr.read(8))
							rdr.stop_crypto1()
						else:
							print("Authentication error")
					else:
						print("Failed to select tag")

	except KeyboardInterrupt:
		print("Bye")
	print("Exiting do_read()")

do_read()
