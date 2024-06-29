import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import adafruit_pn532

def read_block(pn532, block_number, key, uid):
    
    ''' Before you can do access the sector's memory, you first need to "authenticate" according to the security settings stored in the Sector Trailer.
        By default, any new card will generally be configured to allow full access to every block in the sector using Key A and a value of 
        0xFF 0xFF 0xFF 0xFF 0xFF 0xFF.
    '''
    
    # Authenticate the block
    #key_a = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    authenticated = pn532.mifare_classic_authenticate_block(uid, block_number=block_number, key_number=adafruit_pn532.adafruit_pn532.MIFARE_CMD_AUTH_A, key=key_a)
    if not authenticated:
        print("Failed to authenticate block", block_number)
        return None

    # Read the block
    block_data = pn532.mifare_classic_read_block(block_number)
    if block_data is None:
        print("Failed to read block", block_number)
        return None

    return block_data

def dump_blocks(pn532, uid):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    # Now we try to go through all 16 sectors (each having 4 blocks)
    for i in range(64):
        try:
            pn532.mifare_classic_authenticate_block(uid, block_number=i, key_number=adafruit_pn532.adafruit_pn532.MIFARE_CMD_AUTH_A, key=key_a)
            print("Authenticated block", i)
            block_data = pn532.mifare_classic_read_block(i)
            if block_data is None:
                print("Failed to read block", i)
            else:
                print(i, ':', ' '.join(['%02X' % x for x in block_data]))
            #print(i, ':', ' '.join(['%02X' % x for x in pn532.mifare_classic_read_block(i)]))
        
        except AttributeError as e:
            print("Attribute error:", e)
        except OSError as e:
            print("I/O error occurred:", e)
        except ValueError as e:
            print("Invalid parameter:", e)
        except TimeoutError as e:
            print("Operation timed out:", e)
        except NotImplementedError as e:
            print("Operation not supported:", e)
        except MemoryError as e:
            print("Memory error:", e)
        except TypeError as e:
            print("Type error:", e)
        except Exception as e:  # Cach-all for any other exceptions not explicitly caught above
            # print i and exception message
            # q: why isn't the following statement printing the value of i?
            # a: the value of i is not being passed to the print statement as an argument  
            print(i, e )

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

# Example key, typically you need the correct key for the block you're trying to read
key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
block_number = 4  # Example block


print("Waiting for NFC tags...")
n_read = 0
while True:
    # Check for a card on the first PN532 (with a short timeout)
    uid_1 = pn532_1.read_passive_target(timeout=0.1)
    if uid_1 is not None:
        # Found a card
        print("{} Reader 1 Found card with UID:{}".format(n_read,[hex(i) for i in uid_1]))
        n_read = n_read + 1
        #read_block(pn532_1,4,key,uid_1)
        dump_blocks(pn532_1, uid_1)
        
        

    # Check for a card on the second PN532 (with a short timeout)
    uid_2 = pn532_2.read_passive_target(timeout=0.1)
    if uid_2 is not None:
        # Found a card
        print("{} Reader 2 Found card with UID:{}".format(n_read,[hex(i) for i in uid_2]))
        n_read = n_read + 1    
        dump_blocks(pn532_2, uid_2)

    # Add a short delay to prevent excessive CPU usage
    time.sleep(0.1)
