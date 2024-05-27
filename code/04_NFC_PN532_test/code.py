import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# I2C setup
i2c = busio.I2C(board.GP1, board.GP0)

# Create the PN532 object
pn532 = PN532_I2C(i2c, debug=False)

# Check if the PN532 is connected
def check_pn532():
    try:
        ic, ver, rev, support = pn532.firmware_version
        print(f"Found PN532 with firmware version: {ver}.{rev}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Check the PN532 connection
if check_pn532():
    print("PN532 is connected and working!")
else:
    print("PN532 not found. Please check connections.")

# Configure the PN532 to communicate with MiFare cards
pn532.SAM_configuration()

print("Waiting for an NFC card...")

# Specific card UID to be recognized
specific_card_uid = [0x79, 0x1c, 0x50, 0xd3]

while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    
    # Try to read a tag
    if uid is not None:
        # Found a card
        print("Found card with UID:", [hex(i) for i in uid])
        
        # Check if the UID starts with 0x8 or matches the specific card UID
        if uid[0] == 0x8 or uid == specific_card_uid:
            print("Recognized device with UID:", [hex(i) for i in uid])
        else:
            print("Unknown UID detected.")
        
    time.sleep(1)
