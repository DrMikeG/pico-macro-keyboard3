import time
import board
import digitalio
import busio

#0
#1
#GND
#2
#3
miso = board.GP4  # Grey - This seems provable correct - behaviour changes on disconect 
#cs = board.GP5 # Orange
#GND
sck = board.GP6 # Yellow
mosi = board.GP7 # Purple - This seems provable correct - behaviour changes on disconect
rst = board.GP8 # Brown
#9
#GND

# Initialize SPI bus
#spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
spi = busio.SPI(clock=sck, MOSI=mosi, MISO=miso)

# Chip select (CS) pin setup
cs = digitalio.DigitalInOut(board.GP5)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

# Wait for the SPI bus to be ready
while not spi.try_lock():
    pass


try:
    # Configure SPI for your device (adjust frequency, polarity, and phase as needed)
    spi.configure(baudrate=1000000, phase=0, polarity=0)

    # Test data to send
    test_data = bytearray([0x9F])  # Example command, often used for reading device ID

    # Create a buffer to hold the response data
    response = bytearray(len(test_data))

    # Start SPI communication
    cs.value = False  # Select the SPI device
    time.sleep(0.1)   # Small delay to allow the device to select properly

    # Write data to the SPI device and read response
    spi.write_readinto(test_data, response)

    # End SPI communication
    cs.value = True  # Deselect the SPI device

    # Print the response data
    print("Sent:", [hex(x) for x in test_data])
    print("Response:", [hex(x) for x in response])

finally:
    # Release the SPI bus
    spi.unlock()

    # Clean up
    cs.deinit()