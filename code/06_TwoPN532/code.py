import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# Initialize the first I2C bus on GP0 (SDA) and GP1 (SCL)
i2c1 = busio.I2C(scl=board.GP1, sda=board.GP0)

# Initialize the second I2C bus on GP2 (SDA) and GP3 (SCL)
i2c2 = busio.I2C(scl=board.GP3, sda=board.GP2)

# Wait for the I2C buses to be ready
while not i2c1.try_lock():
    pass
while not i2c2.try_lock():
    pass

try:
    # Scan for devices on the first I2C bus
    devices1 = i2c1.scan()
    print("I2C addresses on bus 1:", [hex(device) for device in devices1])

    # Scan for devices on the second I2C bus
    devices2 = i2c2.scan()
    print("I2C addresses on bus 2:", [hex(device) for device in devices2])
finally:
    # Release the I2C buses
    i2c1.unlock()
    i2c2.unlock()



# Initialize the first PN532 with the default address (0x24)
pn532_1 = PN532_I2C(i2c1, address=0x24, debug=False)

# Initialize the second PN532 with the modified address (0x25)
pn532_2 = PN532_I2C(i2c2, address=0x24, debug=False)

# Configure PN532s to communicate with MiFare cards
pn532_1.SAM_configuration()
pn532_2.SAM_configuration()

print("Waiting for NFC tags...")
n_read = 0
while True:
    # Check for a card on the first PN532 (with a short timeout)
    uid_1 = pn532_1.read_passive_target(timeout=0.1)
    if uid_1 is not None:
        # Found a card
        print("{} Reader 1 Found card with UID:{}".format(n_read,[hex(i) for i in uid_1]))
        n_read = n_read + 1
        

    # Check for a card on the second PN532 (with a short timeout)
    uid_2 = pn532_2.read_passive_target(timeout=0.1)
    if uid_2 is not None:
        # Found a card
        print("{} Reader 2 Found card with UID:{}".format(n_read,[hex(i) for i in uid_2]))
        n_read = n_read + 1    
        
    # Add a short delay to prevent excessive CPU usage
    time.sleep(0.1)
