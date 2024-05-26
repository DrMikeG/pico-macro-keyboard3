from pmk import PMK
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base
import time
import board
import busio
import board
import digitalio


# Initialize UART for HC-05 communication at 38400 baud
hc05 = busio.UART(board.GP0, board.GP1, baudrate=38400)

# Define GPIO pin connected to HC-05 EN pin
en_pin = digitalio.DigitalInOut(board.GP28) 
en_pin.direction = digitalio.Direction.OUTPUT
en_pin.value = True

# Initialize the PMK hardware and set up keys
keybow = PMK(Hardware())
keys = keybow.keys

keybow.set_all(64, 64, 64)


# Function to enter AT command mode
def enter_at_command_mode():
    en_pin.value = True  # Set EN pin high to enter AT command mode
    time.sleep(1)  # Wait for the module to enter AT command mode

# Function to exit AT command mode and enter data mode
def exit_at_command_mode():
    en_pin.value = False  # Set EN pin low to exit AT command mode
    time.sleep(1)  # Wait for the module to exit AT command mode

def send_command(command, delay=1.0):
    #enter_at_command_mode()
    hc05.write(bytes(command + "\r\n", "ascii"))
    time.sleep(delay)
    response = hc05.read(hc05.in_waiting)
    #exit_at_command_mode()
    return response.decode("utf-8") if response else ""

def handle_key_00():
    print("Sending request....")
    response = send_command("AT+VERSION")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

def handle_key_01():
    print("Checking module address")
    response = send_command("AT+ADDR")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

def handle_key_02():
    print("Checking module name")
    response = send_command("AT+NAME")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

def handle_key_03():
    print("Checking module role")
    response = send_command("AT+ROLE")
    if response:
        print("Response:", response)
        if "0" in response:
            print("Current mode: Slave")
        elif "1" in response:
            print("Current mode: Master")
        else:
            print("Unknown mode")
    else:
        print("No response or failed to read response")

def handle_key_04():
    print("Checking pairing password")
    response = send_command("AT+PSWD")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

def handle_key_05():
    print("Checking UART configuration")
    response = send_command("AT+UART")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

    print("Changing UART configuration")
    response = send_command("AT+UART=38400,0,0")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

    print("Checking UART configuration")
    response = send_command("AT+UART")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")


def handle_key_06():
    print("Clearing paired devices")
    response = send_command("AT+RMAAD")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

def handle_key_07():
    
    print("Mode")
    response = send_command("AT+CMODE")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

    response = send_command("AT+CMODE=0")
    if response:
        print("Response:", response)
    else:
        print("No response or failed to read response")

    #print("Requesting ORLG")
    #response = send_command("AT+ORGL")
    #if response:
    #    print("Response:", response)

    print("Requesting RESET")
    response = send_command("AT+RESET")
    if response:
        print("Response:", response)

    print("Requesting INIT")
    response = send_command("AT+INIT")
    if response:
        print("Response:", response)

    print("Setting INQM Params")
    response = send_command("AT+INQM=0,9,48") # max of 9 devices, timeout of 61 seconds
    if response:
        print("Response:", response)

    print("Starting inquiry")
    response = send_command("AT+INQ")
    if response:
        print("Response:", response)
        if "OK" in response:
            print("Inquiry started, waiting for devices to respond...")
            time.sleep(10)  # Wait for devices to respond

            print("Ending inquiry")
            response = send_command("AT+INQC")
            if response:
                print("Response:", response)
            else:
                print("No response or failed to read response")

            print("Reading inquiry responses...")
            response = hc05.read(hc05.in_waiting)
            if response:
                response_str = response.decode("utf-8")
                print("Inquiry response:", response_str)
            else:
                print("No devices found or failed to read response")
        else:
            print("Inquiry failed with response:", response)
    else:
        print("No response or failed to read response")

for key in keys:
    @keybow.on_press(key)
    def press_handler(key):
        print(f"Key {key.number} pressed")
        key.set_led(0, 0, 255)

        if key.number == 0:
            handle_key_00()
        elif key.number == 1:
            handle_key_01()
        elif key.number == 2:
            handle_key_02()
        elif key.number == 3:
            handle_key_03()
        elif key.number == 4:
            handle_key_04()
        elif key.number == 5:
            handle_key_05()
        elif key.number == 6:
            handle_key_06()
        elif key.number == 7:
            handle_key_07()

    @keybow.on_release(key)
    def release_handler(key):
        print(f"Key {key.number} released")
        if key.rgb == [255, 0, 0]:
            key.set_led(0, 255, 0)
        else:
            key.set_led(64, 64, 64)

    @keybow.on_hold(key)
    def hold_handler(key):
        print(f"Key {key.number} held")
        key.set_led(255, 0, 0)

while True:
    keybow.update()
    time.sleep(1.0 / 60)
