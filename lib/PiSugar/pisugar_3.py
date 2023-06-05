# smbus2 is (yet another) pure Python implementation
# of the python-smbus package used to interface with
# I2C devices
from smbus2 import SMBus


class PiSugar3:
	'''
	PiSugar3 implementation
	'''

	def __init__ (self):

		super().__init__()

		# I2C info
		self.I2C_BUS = 1
		self.I2C_ADDRESS  = 0x57
		self.I2C_CMD_VH   = 0x22 # voltage high byte
		self.I2C_CMD_VL   = 0x23 # voltage low byte
		self.I2C_CMD_IH   = 0x26 # current high byte
		self.I2C_CMD_IL   = 0x27 # current low byte
		self.I2C_CMD_TEMP = 0x04 # temperature
		self.I2C_CMD_CTR1 = 0x02 # global ctrl 1
		self.I2C_CMD_CTR2 = 0x03 # global ctrl 2

		# with SMBus(I2C_BUS) as bus: remember to close it
		self._bus = SMBus(self.I2C_BUS)

		self._model = "PiSugar3"

		self._battery_curve = [
			[4.10, 100.0],
			[4.05, 95.0],
			[3.90, 88.0],
			[3.80, 77.0],
			[3.70, 65.0],
			[3.62, 55.0],
			[3.58, 49.0],
			[3.49, 25.6],
			[3.32, 4.5],
			[3.1, 0.0],
		]


	# All these methods will work over registers and are hence
	# device specific

	def _read_voltage (self):
		vh = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_VH) # stored as int (32 bit)
		vl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_VL)
		v = (vh << 8) | vl # no worries shifting
		return v


	def _read_output_current (self):
		ih = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_IH) # stored as int (32 bit)
		il = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_IL)
		i = (ih << 8) | il # no worries shifting
		return i


	def _read_temperature (self):
		return self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_TEMP)


	def temperature (self):
		'''
		Returns the chip temperature in celsius (range -40 to 85)
		'''

		# As the doc states:
		# 'The temperature measurement is in the range of -40
		# to 85 degrees Celsius. This temperature is only the
		# temperature of the chip itself, it does not represent
		# the temperature of the Raspberry Pi, nor does it represent
		# the temperature of the battery.'
		# 0 means -40 degrees Celsius
		t = self._read_temperature()
		return t - 40


	def is_power_plugged (self):
		'''
		Self explanatory
		'''
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		return (ctrl & (1 << 7)) != 0


	def is_charging_allowed (self):
		'''
		Self explanatory
		'''
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		return (ctrl & (1 << 6)) != 0

	def toggle_allow_charging (self, enable: bool):
		'''
		Enable/Disable charging
		'''
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1011_1111
		if enable:
			ctrl |= 0b0100_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)


	def is_charging (self):
		'''
		Duh
		'''
		return self.is_power_plugged and self.is_charging_allowed


	def toggle_power_restore (self, auto_restore: bool):
		'''
		Power restore: turn on when the external power supply is restored
		'''
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1110_1111
		if auto_restore:
			ctrl |= 0b0001_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)


	def toggle_soft_poweroff (self, enable: bool):
		'''
		Power restore: turn on when the external power supply is restored
		'''
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1110_0000
		if enable:
			ctrl |= 0b0001_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)


if __name__ == '__main__':

	pisugar = PiSugar3()

	# check if this class correctly implements the interface
	# print(isinstance(pisugar, PiSugarInterface))

	# why did I structured this code if I know I'm not gonna use it?

	v = pisugar.voltage_avg()
	p = pisugar.percent_avg()

	# as expected the reading should give 0.0 in both cases
	print('battery voltage [V]:\t\t', v)
	print('battery percent [%]:\t\t', p)

	# now run the background thread for a bit and repeat the polling
	pisugar.start()
	pisugar.UPDATE_INTERVAL = 1 # set update interval to 1s
	import time
	time.sleep(10) # sleep for 10 seconds

	v = pisugar.voltage_avg()
	p = pisugar.percent_avg()

	print('battery voltage [V]:\t\t', v)
	print('battery percent [%]:\t\t', p)

	# stop the thread when finished
	pisugar.stop()

	# this code is crap
