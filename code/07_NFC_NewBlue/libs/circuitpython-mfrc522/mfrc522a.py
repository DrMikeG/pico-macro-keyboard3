import busio
import digitalio
from adafruit_bus_device.spi_device import SPIDevice
from microcontroller import Pin

class MFRC522:
    def __init__(self, sck: Pin, mosi: Pin, miso: Pin, rst: Pin, cs: Pin):
        self.cs = digitalio.DigitalInOut(cs)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.cs.value = True

        self.rst = digitalio.DigitalInOut(rst)
        self.rst.switch_to_output()

        self.rst.value = 0
        self.rst.value = 1

        self.spi = busio.SPI(sck, MOSI=mosi, MISO=miso)
        self.spi_device = SPIDevice(self.spi, self.cs)

        self.init()

    def _wreg(self, reg: int, val):
        with self.spi_device as bus_device:
            bus_device.write(bytes([0xff & ((reg << 1) & 0x7e)]))
            bus_device.write(bytes([0xff & val]))

    def _rreg(self, reg: int):
        with self.spi_device as bus_device:
            bus_device.write(bytes([0xff & (((reg << 1) & 0x7e) | 0x80)]))
            val = bytearray(1)
            bus_device.readinto(val)
        return val[0]

    def get_version(self):
        version_reg = 0x37
        return self._rreg(version_reg)

    def init(self):
        # Add initialization code here if needed
        pass

    def _set_bit_mask(self, reg, mask):
        current = self._rreg(reg)
        self._wreg(reg, current | mask)

    def _clear_bit_mask(self, reg, mask):
        current = self._rreg(reg)
        self._wreg(reg, current & (~mask))

    def _request(self, mode):
        self._wreg(0x0D, 0x07)
        (status, back_data, back_bits) = self._to_card(0x0C, [mode])
        if status != 0 or back_bits != 0x10:
            return (status, back_data, back_bits)
        return (status, None, None)

    def _to_card(self, command, send_data):
        recv_data = []
        bits = irq_en = wait_irq = n = 0
        status = 0

        if command == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._clear_bit_mask(0x04, 0x80)
        self._set_bit_mask(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for byte in send_data:
            self._wreg(0x09, byte)
        self._wreg(0x01, command)

        if command == 0x0C:
            self._set_bit_mask(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if not ((i != 0) and (n & 0x01 == 0) and (n & wait_irq == 0)):
                break

        self._clear_bit_mask(0x0D, 0x80)

        if i != 0:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                status = 1

                if n & irq_en & 0x01:
                    status = 0

                if command == 0x0C:
                    n = self._rreg(0x0A)
                    last_bits = self._rreg(0x0C) & 0x07
                    if last_bits != 0:
                        bits = (n - 1) * 8 + last_bits
                    else:
                        bits = n * 8

                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16

                    for _ in range(n):
                        recv_data.append(self._rreg(0x09))
            else:
                status = 0

        return (status, recv_data, bits)

    def is_card(self):
        (status, back_data, back_bits) = self._request(0x26)
        return True if status == 1 else False

    def read_card_serial(self):
        (status, uid, back_bits) = self._request(0x93)
        if status == 1 and len(uid) == 5:
            return uid
        return None