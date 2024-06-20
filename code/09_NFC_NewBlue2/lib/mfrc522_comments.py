import board
import busio
import digitalio
from os import uname

class MFRC522:

    # Status codes
    OK = 0
    NOTAGERR = 1
    ERR = 2

    # Commands for requesting tags
    REQIDL = 0x26
    REQALL = 0x52
    # Authentication commands
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, sck, mosi, miso, cs, rst):
        """
        Initializes the MFRC522 instance with the given pins.
        :param sck: SPI clock pin
        :param mosi: SPI MOSI pin
        :param miso: SPI MISO pin
        :param cs: Chip select pin
        :param rst: Reset pin
        """
        self.cs = digitalio.DigitalInOut(cs)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.rst = digitalio.DigitalInOut(rst)
        self.rst.direction = digitalio.Direction.OUTPUT

        self.rst.value = False
        self.cs.value = True

        # Determine the board type (only RP2040 is supported in this script)
        board = uname()[0]

        if board == 'rp2040':
            # Initialize SPI bus
            self.spi = busio.SPI(sck, mosi, miso)
            while not self.spi.try_lock():
                pass
            self.spi.configure(baudrate=100000, phase=0, polarity=0)
        else:
            raise RuntimeError("Unsupported platform")

        self.rst.value = True

        # Initialize the MFRC522
        self.init()

    def _wreg(self, reg, val):
        """
        Writes a value to a specific register.
        :param reg: Register to write to
        :param val: Value to write
        """
        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value = True

    def _rreg(self, reg):
        """
        Reads a value from a specific register.
        :param reg: Register to read from
        :return: Value read from the register
        """
        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & ((reg << 1) | 0x80)))
        val = self.spi.read(1)
        self.cs.value = True
        return val[0]

    def _set_bit_mask(self, reg, mask):
        """
        Sets specific bits of a register.
        :param reg: Register to modify
        :param mask: Bitmask to set
        """
        current = self._rreg(reg)
        self._wreg(reg, current | mask)

    def _clear_bit_mask(self, reg, mask):
        """
        Clears specific bits of a register.
        :param reg: Register to modify
        :param mask: Bitmask to clear
        """
        current = self._rreg(reg)
        self._wreg(reg, current & (~mask))

    def init(self):
        """
        Initializes the MFRC522 module.
        """
        self.reset()
        self._wreg(0x2A, 0x8D)  # Timer: TPrescaler*TreloadVal = 25ms
        self._wreg(0x2B, 0x3E)  # Reload value
        self._wreg(0x2D, 30)    # 30
        self._wreg(0x2C, 0)     # 0
        self._wreg(0x15, 0x40)  # 100%ASK
        self._wreg(0x11, 0x3D)  # CRC initial value 0x6363

    def reset(self):
        """
        Resets the MFRC522 module.
        """
        self._wreg(0x01, 0x0F)

    # Additional methods for the MFRC522 would be added here, such as methods
    # for reading from and writing to NFC tags, authenticating, etc.