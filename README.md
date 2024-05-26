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