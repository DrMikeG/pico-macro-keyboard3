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

while True:
    # Main loop can be used to read NFC tags, etc.
    pass
