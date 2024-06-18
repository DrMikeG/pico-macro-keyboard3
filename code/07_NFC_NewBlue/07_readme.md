## New boards.

I've just received 3x new boards. Let's see if I can figure out what they are.

```RFID Kit - Mifare RC522 RF IC Card Sensor Module + S50 Blank Card + Key Ring for Arduino Raspberry Pi 3PCS Brand: DUTTY```

The MF522-AN module design the circuit of card read by using the original Philips MFRC522 chip.

The module use a voltage of 3.3V, it can connected communication with user's any CPU mainboard through several lines of SPI interface, it can ensure stable and reliable work, and reader distance.




![Wiring for HC-05](/readme_img/RFID-RC522.jpg)

The RC522 RFID reader module is designed to create a 13.56MHz electromagnetic field and communicate with RFID tags (ISO 14443A standard tags).

The reader can communicate with a microcontroller over a 4-pin SPI with a maximum data rate of 10 Mbps. It also supports communication over I2C and UART protocols.

The RC522 RFID module can be programmed to generate an interrupt, allowing the module to alert us when a tag approaches it, instead of constantly asking the module “Is there a card nearby?”.

The module’s operating voltage ranges from 2.5 to 3.3V, but the good news is that the logic pins are 5-volt tolerant, so we can easily connect it to an Arduino or any 5V logic microcontroller without using a logic level converter.

Technical Specifications
Here are the specifications:

Frequency Range	13.56 MHz ISM Band
Host Interface	SPI / I2C / UART
Operating Supply Voltage	2.5 V to 3.3 V
Max. Operating Current	13-26mA
Min. Current(Power down)	10µA
Logic Inputs	5V Tolerant
Read Range	5 cm
For more details, please refer below datasheet.

MFRC522 Datasheet
RC522 RFID Module Pinout
The RC522 module has a total of 8 pins that connect it to the outside world. The connections are as follows:

https://lastminuteengineers.com/how-rfid-works-rc522-arduino-tutorial/

Communicating with an RC522 RFID module is a lot of work, but luckily for us there is a library called the MFRC522 library that makes reading and writing RFID tags simple.

https://github.com/domdfcoding/circuitpython-mfrc522


 RST/Reset       RST              9                 

  SPI SS          SDA(SS)          10   GP17   
  SPI MOSI        MOSI             11   GP16
  SPI MISO        MISO             12   GP19
  SPI SCK         SCK              13   GP18


Pico has two SPI controllers, each of which can use several different pin configurations. For example, SPI0 can use any pin labelled on the pinout diagram as 'SPI0 SCK' as a clock or any 'SPI0 RX' as MISO, you just have to tell it which pins exactly you want to use.

The default pins for SPI0 are:
SCK - GP18
RX - GP16
TX - GP19



![Wiring for HC-05](/readme_img/rc522d.png)

- VCC supplies power to the module. This can be anywhere from 2.5 to 3.3 volts. You can connect it to the 3.3V output from your Arduino. But remember that connecting it to the 5V pin will probably destroy your module!

- RST is an input for reset and power-down. When this pin goes low the module enters power-down mode. In which the oscillator is turned off and the input pins are disconnected from the outside world. Whereas the module is reset on the rising edge of the signal.

- GND is the ground pin and needs to be connected to the GND pin on the Arduino.

- IRQ is an interrupt pin that alerts the microcontroller when an RFID tag is in the vicinity.

- MISO / SCL / Tx pin acts as master-in-slave-out when SPI interface is enabled, as serial clock when I2C interface is enabled and as serial data output when the UART interface is enabled.

- MOSI (Master Out Slave In) is the SPI input to the RC522 module.

- SCK (Serial Clock) accepts the clock pulses provided by the SPI bus master i.e. Arduino.

- SS / SDA / Rx pin acts as a signal input when the SPI interface is enabled, as serial data when the I2C interface is enabled and as a serial data input when the UART interface is enabled. This pin is usually marked by encasing the pin in a square so that it can be used as a reference to identify other pins.

![Wiring for HC-05](/readme_img/wired_rc522d.png)



Had to flash adafruit-circuitpython-raspberry_pi_pico-en_US-9.0.5.uf2 onto the next pi pico.
