# smbus2 is (yet another) pure Python implementation of
# the python-smbus package used to interface with I2C devices
from smbus2 import SMBus


class PiSugar3:
	"""
	Python API for the PiSugar3
	"""

	def __init__(self):

		# addresses
		self.I2C_BUS = 1
		self.I2C_ADDRESS  = 0x57
		self.I2C_CMD_VH   = 0x22  # voltage high byte
		self.I2C_CMD_VL   = 0x23  # voltage low byte
		self.I2C_CMD_IH   = 0x26  # current high byte
		self.I2C_CMD_IL   = 0x27  # current low byte
		self.I2C_CMD_TEMP = 0x04  # temperature
		self.I2C_CMD_CTR1 = 0x02  # global ctrl 1
		self.I2C_CMD_CTR2 = 0x03  # global ctrl 2

		# with SMBus(I2C_BUS) as bus: remember to close it
		self._bus = SMBus(self.I2C_BUS)

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

	def _read_voltage(self):
		vh = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_VH) # stored as int (32 bit)
		vl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_VL)
		v = (vh << 8) | vl # no worries shifting
		return v

	def _read_current(self):
		ih = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_IH) # stored as int (32 bit)
		il = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_IL)
		i = (ih << 8) | il # no worries shifting
		return i

	def _read_temperature(self):
		return self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_TEMP)

	def get_voltage(self):
		"""
		Returns the battery voltage.
		This is an instantaneous measurement, so it won't be precise.
		"""
		return self._read_voltage() / 1000.0
	
	def get_current(self):
		"""
		Returns the battery current.
		This is an instantaneous measurement, so it won't be precise.
		"""
		return self._read_current() / 1000.0

	def get_temperature(self):
		"""
		Returns the chip temperature in Celsius (range -40 to 85).
		This is an instantaneous measurement, so it won't be precise.
		"""

		# As the doc states:
		# 'The temperature measurement is in the range of -40
		# to 85 degrees Celsius. This temperature is only the
		# temperature of the chip itself, it does not represent
		# the temperature of the Raspberry Pi, nor does it represent
		# the temperature of the battery.'
		# 0 means -40 degrees Celsius
		t = self._read_temperature()
		return t - 40

	def get_percent(self):
		"""
		Returns the battery percentage for the PiSugar.
		This is an instantaneous measurement, so it won't be precise.
		"""
		battery_voltage = self._read_voltage()

		for i in range(len(self._battery_curve)):
			voltage_low = self._battery_curve[i][0]
			level_low = self._battery_curve[i][1]
			if battery_voltage > voltage_low:
				if i == 0:
					return level_low
				else:
					voltage_high = self._battery_curve[i - 1][0]
					level_high = self._battery_curve[i - 1][1]
					percent = (battery_voltage - voltage_low) / (voltage_high - voltage_low)
					return level_low + percent * (level_high - level_low)
		return 0.0

	def is_power_plugged(self):
		"""
		Self-explanatory.
		"""
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		return (ctrl & (1 << 7)) != 0

	def is_charging_allowed(self):
		"""
		Self-explanatory.
		"""
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		return (ctrl & (1 << 6)) != 0

	def toggle_allow_charging(self, enable: bool):
		"""
		Enable/Disable charging.
		"""
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1011_1111
		if enable:
			ctrl |= 0b0100_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)

	def is_charging(self):
		"""
		Duh
		"""
		return self.is_power_plugged and self.is_charging_allowed

	def toggle_power_restore(self, auto_restore: bool):
		"""
		Power restore: turn on when the external power supply is restored.
		"""
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1110_1111
		if auto_restore:
			ctrl |= 0b0001_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)

	def toggle_soft_poweroff(self, enable: bool):
		"""
		Power restore: turn on when the external power supply is restored.
		"""
		ctrl = self._bus.read_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1)
		ctrl &= 0b1110_0000
		if enable:
			ctrl |= 0b0001_0000
		# write_byte_data(i2c_addr, register, value)
		self._bus.write_byte_data(self.I2C_ADDRESS, self.I2C_CMD_CTR1, ctrl)

	def close(self):
		"""
		Closes the connection with the I2C bus.
		"""
		self._bus.close()

	def __enter__(self):
		return self

	def __del__(self):
		self.close()

	def __exit__(self, exc_type, exc_value, tb):

		if exc_type is not None:
			return False

		self.close()

		return True


if __name__ == '__main__':

	pisugar = PiSugar3()
	v = pisugar.get_voltage()
	p = pisugar.get_percent()
	print(f'Battery percentage :{p}%')
	print(f'Battery voltage [V]:{v}')
