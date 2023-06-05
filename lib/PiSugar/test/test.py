from smbus2 import SMBus

I2C_BUS = 1
I2C_ADDRESS = 0x57
I2C_CMD_VH  = 0x22 # voltage high byte
I2C_CMD_VL  = 0x23 # voltage low byte
I2C_CMD_IH  = 0x26 # current high byte
I2C_CMD_IL  = 0x27 # current low byte

def look_for_device_address(address):
	'''
	Checks if a device with the specified address is connected
	'''
	with SMBus(I2C_BUS) as bus:
		is_device_found = False
		for device in range(128):
			try:
				bus.read_byte(device)
				if device == address:
					is_device_found = True
					return is_device_found
			except:
				pass

		return is_device_found

def read_battery_i():
	'''
	Reads the current drawn in mA
	'''
	with SMBus(I2C_BUS) as bus:
		ih = bus.read_byte_data(I2C_ADDRESS, I2C_CMD_IH) # stored as int (32 bit)
		il = bus.read_byte_data(I2C_ADDRESS, I2C_CMD_IL)
		i = (ih << 8) | il # no worries shifting
		return i
	
def current ():
	'''
	Returns the current draw in Amps
	'''
	i = read_battery_i ()
	return i / 1000.0

def read_battery_v():
	'''
	Returns the battery voltage in mA
	'''
	with SMBus(I2C_BUS) as bus:
		vh = bus.read_byte_data(I2C_ADDRESS, I2C_CMD_VH) # stored as int (32 bit)
		vl = bus.read_byte_data(I2C_ADDRESS, I2C_CMD_VL)
		v = (vh << 8) | vl # no worries shifting
		return v

def voltage ():
	'''
	Returns the voltage [V]
	'''
	v = read_battery_v ()
	return v / 1000.0

def convert_battery_voltage_to_level (battery_voltage, battery_curve):
	'''
	Returns the battery percentage given the battery voltage curve
	'''
	for i in range(len(battery_curve)):
		voltage_low = battery_curve[i][0]
		level_low 	= battery_curve[i][1]
		if battery_voltage > voltage_low:
			if i == 0:
				return level_low
			else:
				voltage_high = battery_curve[i - 1][0]
				level_high = battery_curve[i - 1][1]
				percent = (battery_voltage - voltage_low) / (voltage_high - voltage_low)
				return level_low + percent * (level_high - level_low)
	return 0.0

def battery_percent(battery_voltage):
	'''
	Returns the battery percentage for the PiSugar3/PiSugar2 Pro (?)
	'''
	battery_curve = [
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
	battery_level = 100.0
	if battery_voltage > 0.0:
		battery_level = convert_battery_voltage_to_level(battery_voltage, battery_curve)
	return battery_level

if __name__ == '__main__':

	v = voltage()
	p = battery_percent(v)

	print('battery voltage [V]:\t', v)
	print('battery percent [%]:\t', p)