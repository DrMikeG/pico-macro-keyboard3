# pico-macro-keyboard3

Ok, May 2024 - I'm making a new macro pad out of a pi pico (not-W) and a Pico RGB Keypad Base by Pimoroni (https://shop.pimoroni.com/products/pico-rgb-keypad-base)

I'm going to use circuit python - so interested in: https://github.com/pimoroni/pmk-circuitpython

I want to do some stuff with blue-tooth. I'm starting out with a HC-05 - although I've been warned this might not be what I want for the job.


```
https://learn.pimoroni.com/article/circuitpython-and-keybow-2040

First of all, go to this page and download the most recent .uf2 file - this is a customised version of CircuitPython built especially for Keybow 2040.
- You'll need to download and install CircuitPython for Raspberry Pi Pico instead of CircuitPython for Keybow 2040.

CircuitPython 9.0.5

Downloading and installing the libraries
The next thing you'll need to do is download and install the libraries that Keybow uses. CircuitPython libraries are installed by copying files from your computer to the lib folder in the CIRCUITPY drive - super easy!

If you already have files in your lib folder, it's a good idea to delete them before you copy across the new ones, as having older versions of the libraries lurking around can cause problems.

First up is the Adafruit IS31FL3731 library - this is a driver for Keybow's LED matrix controller. The easiest way to get it is via the CircuitPython Library Bundle, which you can download from this page. Make sure you download the library bundle that matches your CircuitPython version!

Next, you'll need to download our PMK library from Github (PMK stands for Pimoroni Mechanical/Mushy Keypad, if you're curious!). Click on the green 'Code' button at the top of the page, and select 'Download ZIP' in the dropdown - this will download the whole library, complete with examples.

PMK on Pico RGB Keypad
- RGB Keypad has APA102 LEDs (aka Dotstar), so you'll need to copy adafruit_dotstar.mpy from the library bundle into your lib folder.
- When you save your example as code.py, add a # to the beginning of the line that starts from pmk.platform.keybow2040 
- and remove the # from the line that starts from pmk.platform.rgbkeypadbase

See \code\01_rainbow for first working example with pi pico
See \code\02_single_function_keys for first example of reacting to key press.

## HC-05

https://gist.github.com/idriszmy/479befe5c3fa475d785ccd9ef080b880

```
import board
import busio

hc05 = busio.UART(board.GP4, board.GP5, baudrate=38400)

while True:
    command = input() + "\r\n"
    hc05.write(bytes(command, 'ascii'))
    while True:
        response = hc05.readline()
        if response == None:
            break
        print(str(response, 'UTF-8'))

![Wiring for HC-05](/readme_img/hc05.png)

https://howtomechatronics.com/tutorials/arduino/how-to-configure-pair-two-hc-05-bluetooth-module-master-slave-commands/

Reading this to try and understand the purpose of the enable pin and the button.

```
For this tutorial we need to configure both modules. In order to do that we need to switch to AT Command Mode and here’s how we will do that. First we need connect the Bluetooth module to the Arduino as the circuit schematics explained in the previous tutorials. What we need to do additionally is to connect the “EN” pin of the Bluetooth module to 5 volts and also switch the TX and RX pins at the Arduino Board

So the RX pin of the Arduino needs to be connected to the RX pin of the Bluetooth module, through the voltage divider, and the TX pin of the Arduino to the TX pin of the Bluetooth module. Now while holding the small button over the “EN” pin we need to power the module and that’s how we will enter the command mode. If the Bluetooth module led is flashing every 2 seconds that means that we have successfully entered in the AT command mode.

After this we need to upload an empty sketch to the Arduino but don’t forget to disconnect the RX and TX lines while uploading. Then we need to run the Serial Monitor and there select “Both NL and CR”, as well as, “38400 baud” rate which is the default baud rate of the Bluetooth module. Now we are ready to send commands and their format is as following.
```

Pin Connections
- VCC: Connect to 3.3V (or 5V, but ensure logic levels are compatible with the Pico).
- GND: Connect to GND.
- TX: Connect to RX (GP1) on the Pico (with a voltage divider if needed for 5V logic).
- RX: Connect to TX (GP0) on the Pico (with a voltage divider if needed for 5V logic).
- EN: This pin is used to enter AT command mode. It should be pulled high to enter AT command mode.
- State: This pin indicates the connection status (it can be left unconnected for basic setups).

Arduino with HC-05 (ZS-040) Bluetooth module – AT MODE

'AT\r\n' – simple feedback request. Will return “OK”
'AT+VERSION\r\n' – returns the firmware version. “+VERSION:2.0-20100601

connected up as pictured.

booted up with button held. LED flashes every 2 seconds.

able to communicate and query firmware version with code in \code\03

Moved to keypress: VERSION:3.0-20170601

