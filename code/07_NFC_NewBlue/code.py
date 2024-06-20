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
		self._wreg(0x0D, 0x07)  # BitFramingReg
		(status, back_data, back_bits) = self._to_card(0x0C, [mode])  # Transceive command
		if status != 0 or back_bits != 0x10:
			return (status, back_data, back_bits)
		return (status, None, None)

	def _to_card(self, command, send_data):
		recv_data = []
		bits = irq_en = wait_irq = n = 0
		status = 0

		if command == 0x0C:
			irq_en = 0x77  # Enable all interrupts for Transceive
			wait_irq = 0x30  # RxIRq and IdleIRq

		print(f"Initializing communication: irq_en={hex(irq_en)}, wait_irq={hex(wait_irq)}")

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

		print("Waiting for command to complete...")
		i = 2000
		while True:
			n = self._rreg(0x04)  # ComIrqReg register
			#print(f"ComIrqReg: {hex(n)}")
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

	def is_card(self):
		(status, back_data, back_bits) = self._request(0x26)  # REQA command
		return True if status == 1 else False

	def read_card_serial(self):
		(status, uid, back_bits) = self._request(0x93)  # Anti-collision command
		if status == 1 and len(uid) == 5:
			return uid
		return None

# Example usage
def main():
    import board
    import time

    # Define the pins for SPI
    sck = board.GP18
    mosi = board.GP19
    miso = board.GP16
    rst = board.GP22
    cs = board.GP17

    # Create an instance of the MFRC522 class
    rfid = MFRC522(sck, mosi, miso, rst, cs)

    # Query the version
    version = rfid.get_version()
    print(f"RC522 Version: {hex(version)}")

    # Check for card and read UID
    while True:
        if rfid.is_card():
            uid = rfid.read_card_serial()
            if uid:
                print(f"Card detected! UID: {[hex(x) for x in uid]}")
        time.sleep(1)

if __name__ == "__main__":
    main()
