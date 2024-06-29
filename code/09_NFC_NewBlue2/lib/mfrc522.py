import board
import busio
import digitalio
from os import uname


class MFRC522:

    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    def __init__(self, sck, mosi, miso, cs, rst):

        self.cs = digitalio.DigitalInOut(cs)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.rst = digitalio.DigitalInOut(rst)
        self.rst.direction = digitalio.Direction.OUTPUT

        self.rst.value = False
        self.cs.value = True

        board = uname()[0]

        if board == 'rp2040':
            self.spi = busio.SPI(sck, mosi, miso)
            while not self.spi.try_lock():
                pass
            self.spi.configure(baudrate=100000, phase=0, polarity=0)
        else:
            raise RuntimeError("Unsupported platform")

        self.rst.value = True

        self.init()

    def _wreg(self, reg, val):

        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value = True

    def _rreg(self, reg):

        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = bytearray(1)
        self.spi.readinto(val)
        self.cs.value = True

        return val[0]

    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):

        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._cflags(0x04, 0x80)
        self._sflags(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for c in send:
            self._wreg(0x09, c)
        self._wreg(0x01, cmd)

        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        self._cflags(0x0D, 0x80)

        if i:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                stat = self.OK

                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == 0x0C:
                    n = self._rreg(0x0A)
                    lbits = self._rreg(0x0C) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8

                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16

                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                stat = self.ERR

        return stat, recv, bits

    def _crc(self, data):

        self._cflags(0x05, 0x04)
        self._sflags(0x0A, 0x80)

        for c in data:
            self._wreg(0x09, c)

        self._wreg(0x01, 0x03)

        i = 0xFF
        while True:
            n = self._rreg(0x05)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        return [self._rreg(0x22), self._rreg(0x21)]

    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        # Initialize and set the antenna gain to the maximum value (48 dB)
        current_gain = self._rreg(0x26) & 0x07
        gain_dict = {
            0x00: 18,
            0x01: 23,
            0x02: 18,
            0x03: 23,
            0x04: 33,
            0x05: 38,
            0x06: 43,
            0x07: 48
        }
        print(f"Current antenna gain: {gain_dict.get(current_gain, 'Unknown')} dB")
        self._wreg(0x26, (self._rreg(0x26) & 0xF8) | 0x07)  # Set gain to maximum (48 dB)
        new_gain = self._rreg(0x26) & 0x07
        print(f"New antenna gain: {gain_dict.get(new_gain, 'Unknown')} dB")

        self._wreg(0x26, (self._rreg(0x26) & 0xF8) | 0x07)  # Set gain to maximum (48 dB)
        self.antenna_on()

    def reset(self):
        self._wreg(0x01, 0x0F)

    def antenna_on(self, on=True):

        if on and ~(self._rreg(0x14) & 0x03):
            self._sflags(0x14, 0x03)
        else:
            self._cflags(0x14, 0x03)

    def request(self, mode):

        self._wreg(0x0D, 0x07)
        (stat, recv, bits) = self._tocard(0x0C, [mode])

        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR

        return stat, bits

    def anticoll(self):

        ser_chk = 0
        ser = [0x93, 0x20]

        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)

        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR

        return stat, recv

    def select_tag(self, ser):

        buf = [0x93, 0x70] + ser[:5]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(0x0C, buf)
        return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

    def auth(self, mode, addr, sect, ser):
        return self._tocard(0x0E, [mode, addr] + sect + ser[:4])[0]

    def stop_crypto1(self):
        self._cflags(0x08, 0x08)

    def read(self, addr):

        data = [0x30, addr]
        data += self._crc(data)
        (stat, recv, _) = self._tocard(0x0C, data)
        return recv if stat == self.OK else None

    def write(self, addr, data):

        buf = [0xA0, addr]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(0x0C, buf)

        if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
            stat = self.ERR
        else:
            buf = []
            for i in range(16):
                buf.append(data[i])
            buf += self._crc(buf)
            (stat, recv, bits) = self._tocard(0x0C, buf)
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR

        return stat
    
    def _set_bit_mask(self, reg, mask):
        current = self._rreg(reg)
        self._wreg(reg, current | mask)

    def _clear_bit_mask(self, reg, mask):
        current = self._rreg(reg)
        self._wreg(reg, current & (~mask))
        
    def _to_card(self, command, send_data):
        recv_data = []
        bits = irq_en = wait_irq = n = 0
        status = 0

        if command == 0x0C:
            irq_en = 0x77  # Enable all interrupts for Transceive
            wait_irq = 0x30  # RxIRq and IdleIRq

        self._wreg(0x02, irq_en | 0x80)  # CommIEnReg, Enable interrupt request
        self._clear_bit_mask(0x04, 0x80)  # CommIrqReg, Clear all interrupt requests
        self._set_bit_mask(0x0A, 0x80)  # FIFOLevelReg, FlushBuffer=1, FIFO initialization
        self._wreg(0x01, 0x00)  # CommandReg, Idle command

        print(f"Sending data: {send_data}")
        for byte in send_data:
            self._wreg(0x09, byte)  # FIFODataReg, Write data to FIFO
        self._wreg(0x01, command)  # CommandReg, Execute command

        if command == 0x0C:
            self._set_bit_mask(0x0D, 0x80)  # BitFramingReg, StartSend=1, transmission of data starts

        i = 2000
        while True:
            n = self._rreg(0x04)  # ComIrqReg register
            print(f"ComIrqReg: {hex(n)}")
            i -= 1
            if not ((i != 0) and (n & 0x01 == 0) and (n & wait_irq == 0)):
                break

        self._clear_bit_mask(0x0D, 0x80)  # BitFramingReg, StopSend=0

        if i != 0:
            error_reg = self._rreg(0x06)  # ErrorReg register
            if (error_reg & 0x1B) == 0x00:  # Check for buffer overflow, parity or CRC errors
                status = 1

                if n & irq_en & 0x01:
                    status = 0  # No card

                if command == 0x0C:
                    n = self._rreg(0x0A)  # FIFOLevelReg, number of bytes stored in the FIFO buffer
                    last_bits = self._rreg(0x0C) & 0x07  # ControlReg, Last bits received
                    if last_bits != 0:
                        bits = (n - 1) * 8 + last_bits
                    else:
                        bits = n * 8

                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16

                    recv_data = []
                    for _ in range(n):
                        recv_data.append(self._rreg(0x09))  # FIFO buffer

                    print(f"Received data: {recv_data}")
            else:
                status = 0  # Error
                print(f"ErrorReg: {hex(error_reg)}")
        else:
            print("Timeout: No response from the card")

        return (status, recv_data, bits)


    def _request(self, mode):
        self._wreg(0x0D, 0x07)  # BitFramingReg
        (status, back_data, back_bits) = self._to_card(0x0C, [mode])  # Transceive command
        if status != 0 or back_bits != 0x10:
            return (status, back_data, back_bits)
        return (status, None, None)

    def is_card(self):
        (status, back_data, back_bits) = self._request(0x26)  # REQA command
        return True if status == 1 else False

    def read_card_serial(self):
        (status, uid, back_bits) = self._request(0x93)  # Anti-collision command
        if status == 1 and len(uid) == 5:
            return uid
        return None

    def read_block(self, block_addr):
        """
        Read a single block of data from the card.
        :param block_addr: Address of the block to read.
        :return: A list of 16 bytes read from the block.
        """
        self._set_bit_mask(0x0D, 0x80)  # StartSend=1, transmission of data starts
        recv_data = [0x30, block_addr]  # 0x30 is the MIFARE Read command
        (status, back_data, back_len) = self._to_card(0x0C, recv_data)
        if status == 1 and len(back_data) == 16:
            return back_data
        else:
            print(f"Failed to read block {block_addr}. Status: {status}")
            return None

    def authenticate(self, mode, block_addr, sector_key, uid):
        """
        Authenticate a block for reading or writing.
        :param mode: Authentication mode (0x60 for Key A, 0x61 for Key B).
        :param block_addr: Address of the block to authenticate.
        :param sector_key: 6 bytes key for the sector.
        :param uid: 4 bytes card UID.
        :return: True if authentication is successful, False otherwise.
        """
        auth_data = [mode, block_addr] + sector_key + uid[:4]
        (status, back_data, back_len) = self._to_card(0x0E, auth_data)
        if status != 1:
            print(f"Authentication failed for block {block_addr}. Status: {status}")
            return False
        return True

    def read_text_record(self, block_addr):
        """
        Read a text record from a block.
        :param block_addr: Address of the block to read.
        :return: The text record as a string.
        """
        data = self.read_block(block_addr)
        if not data:
            return None

        # Assuming the text record starts after the first few bytes
        nfc_header = data[:4]
        tnf = nfc_header[0] & 0x07
        type_length = nfc_header[1]
        payload_length = nfc_header[2]

        if tnf != 0x01:  # TNF_WELL_KNOWN
            print(f"Unexpected TNF: {tnf}")
            return None

        if type_length != 1 or data[4] != ord('T'):  # 'T' for text record
            print(f"Unexpected type: {data[4]}")
            return None

        payload = data[5:5+payload_length]
        text = ''.join(chr(x) for x in payload)
        return text