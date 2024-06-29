import board
import busio
import digitalio
from os import uname

# Moved out of \lib folder to allow autocomplete

class MFRC522:

    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    # AUTHENT1A = 0x60 which is the command for MIFARE Authenticate with key A
    AUTHENT1A = 0x60
    # Authent1B = 0x61 which is the command for MIFARE Authenticate with key B
    AUTHENT1B = 0x61

    MIFARE_CLASSIC = 0x04
    MIFARE_ULTRALIGHT = 0x44

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
            # Added by Mike
            print("Recongnized RP2040 and confingured SPI")
        else:
            raise RuntimeError("Unsupported platform")

        self.rst.value = True

        self.init()

    def _wreg(self, reg, val):
        # Write a byte to the register
        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value = True

    def _rreg(self, reg):
        # Read a byte from the register
        self.cs.value = False
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = bytearray(1)
        self.spi.readinto(val)
        self.cs.value = True

        return val[0]

    def _sflags(self, reg, mask):
        # Adds mask to value already in register
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        # _cflags is different from _sflags in that it clears the bits in the register
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):
        """
        Sends a command to the tag and receives the response.

        Args:
            cmd (int): The command to send to the tag.
            send (list): The data to send to the tag.

        Returns:
            tuple: A tuple containing the status, received data, and number of bits.
                - status (int): The status of the command execution.
                - recv (list): The received data from the tag.
                - bits (int): The number of bits received.

        Raises:
            None

        """
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR

        # cmd = 0x0C is the command for MIFARE Read
        # cmd = 0x0E is the command for MIFARE Write
        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30
        else:
            print("Unknown command")
            return self.ERR, recv, bits
            
        # Enable the interrupts
        self._wreg(0x02, irq_en | 0x80)
        # Clear the interrupt request bits
        self._cflags(0x04, 0x80)
        # Flush the FIFO buffer
        self._sflags(0x0A, 0x80)
        # Send 0x00 to the CommandReg to put the MFRC522 in idle mode
        self._wreg(0x01, 0x00)

        # Send the data to the FIFO buffer
        for c in send:
            self._wreg(0x09, c)
        # Send the command to the tag
        self._wreg(0x01, cmd)

        # If reading then set the BitFramingReg register (0x0D) to 0x80 which means StartSend=1
        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)

        # 2000 is the timeout
        i = 2000
        while True:
            # Read the ComIrqReg register
            n = self._rreg(0x04)
            i -= 1
            # if the ComIrqReg register is 0x01 and the wait_irq is 0, then break
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        # Clear 0x80 from the BitFramingReg register
        self._cflags(0x0D, 0x80)

        # If the loop didn't timeout, check for errors
        if i:
            # Read the ErrorReg register
            # if the register is 0x1B, then there are no buffer overflow, parity or CRC errors
            if (self._rreg(0x06) & 0x1B) == 0x00:
                # Set the status to OK
                stat = self.OK

                # Check if there is a card
                if n & irq_en & 0x01:
                    # If there is no card, set the status to NOTAGERR
                    print("No card")
                    stat = self.NOTAGERR
                elif cmd == 0x0C:
                    
                    # If the command is 0x0C, then read the number of bytes in the FIFO buffer

                    # 0x0A is the FIFOLevelReg register which tells us the number of bytes stored in the FIFO buffer
                    n = self._rreg(0x0A)

                    # The last byte will be padded if the number of bits is not a multiple of 8
                    # reading 0x0C will give us the number of bits in the last byte
                    # &0x07 because we only want the last 3 bits (0-7)                    
                    lbits = self._rreg(0x0C) & 0x07
                    
                    # How many valid bits in final byte?
                    # Add to number of whole bytes (-last) * 8 bits
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
                    
                    # Read between 1 and 16 bytes from the buffer
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16
                    # Read n byte from the FIFO buffer
                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                # There was an error executing the command
                print("Error in _tocard")
                stat = self.ERR
        else:
            # The loop timed out
            stat = self.ERR
        
        # return the status, the received data and the number of bits
        # assert the number of bits is a multiple of 8
        assert bits % 8 == 0

        return stat, recv, bits

    def _crc(self, data):
        # Use the CRC coprocessor to calculate the CRC of the data

        # Clear the FIFO buffer and Set the CRCIrqReg register
        self._cflags(0x05, 0x04)
        self._sflags(0x0A, 0x80)

        for c in data:
            # Write the data to the FIFO buffer
            # 0x09 is the FIFODataReg register
            self._wreg(0x09, c)

        # Execute the command (0x03 is the command for MIFARE CRC) and wait for the result
        self._wreg(0x01, 0x03)

        i = 0xFF        
        while True:
            # Read from 0x05 (CRCResultRegM) into n
            n = self._rreg(0x05)
            i -= 1
            
            if not ((i != 0) and not (n & 0x04)):
                break

        # Return CRC calculated from
        return [self._rreg(0x22), self._rreg(0x21)]

    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)

        # Not in original library
        # Increase antenna gain from default (18db) to the maximum value (48 dB)
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
        """
        Sends a request to the MFRC522 to detect nearby cards.

        Args:
            mode: The request mode to send.

        Returns:
            A tuple containing the status and bits received from the card.

        Raises:
            None.
        """

        self._wreg(0x0D, 0x07)
        
        (stat, recv, bits) = self._tocard(0x0C, [mode])

        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR
        else:
            print(f"Request status: {stat}, recv: {recv}, bytes: {bits // 8} bits: {bits}")

        return stat, recv[0] if recv else None

    
    def anticoll(self):
        """
        Executes the anticollision procedure for the MFRC522 RFID reader.

        Returns:
            tuple: A tuple containing the status and received data.
                - The status indicates the result of the anticollision procedure.
                - The received data is a list of bytes received during the procedure.
        """
        ser_chk = 0
        # This is the command for the anticollision procedure
        ser = [0x93, 0x20]

        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)
        print(f"Anticoll status: {stat}, recv: {recv}, bytes: {bits // 8} bits: {bits}")
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
       # Ensure mode is correctly set for AUTHENT1A (0x60) or AUTHENT1B (0x61)
        # Assuming mode is passed correctly as 0x60 or 0x61
        # addr is the address of the block
        # sect is the sector key for authentication
        # ser is the UID of the card, of which only the first 4 bytes are used

        # Assemble the command
        cmd = [mode, addr] + sect + ser[:4]

        # Debug: Print the command to verify its structure
        print(f"Command sent for authentication: {cmd}")

        # Send the command to the card
        status = self._tocard(0x0E, cmd)[0]  # Note: Ensure 0x0E is the correct command for your card's authentication
        print(f"Authentication status: {status}")
        return status

    def stop_crypto1(self):
        # It is used to stop the encryption which is started by the auth method
        # Stopping the encryption is necessary because the card will not respond to any commands
        # if the encryption is not stopped
        self._cflags(0x08, 0x08)

    def read(self, addr):

        data = [0x30, addr]
        data += self._crc(data)
        (stat, recv, _) = self._tocard(0x0C, data)
        return recv if stat == self.OK else None

    def read_page(self, page_addr):
        """
        Read a single page of data from the card.
        :param page_addr: Address of the page to read.
        
        """
        data = [0x30, page_addr]
        data += self._crc(data)
        (status, back_data, back_len) = self._tocard(0x0C, data)   
        print(f"Read page status: {status}, back_data: {back_data}, back_len: {back_len}")

        # Read command on ultralight returns 16 bytes (4 pages)
        if status == self.OK and len(back_data) == 16:
            return back_data
        else:
            print(f"Failed to read page {page_addr}. Status: {status}")
            return None


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
    
    # End of origina library functions
    # These are new functions I have tried to use

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
        self._sflags(0x0D, 0x80)  # StartSend=1, transmission of data starts
        recv_data = [0x30, block_addr]  # 0x30 is the MIFARE Read command
        (status, back_data, back_len) = self._tocard(0x0C, recv_data)
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
        #print(f"Authenticating: mode: {mode}, block_addr: {block_addr}, sector_key: {sector_key}, uid: {uid}")

        auth_data = [mode, block_addr] + sector_key + uid[:4]
        status = self._tocard(0x0E, auth_data)
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