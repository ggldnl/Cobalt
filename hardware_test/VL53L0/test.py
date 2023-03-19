import time
import VL53L0X
import RPi.GPIO as GPIO

# GPIO shutdown pin XSHUT for ith sensor 
sensor_shutdown = [18, 26, 6]
addr = [0x2B, 0x2C, 0x2D]
# optional sensor in GPIO22

sensors = []

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on each VL53L0X
GPIO.setmode(GPIO.BCM)
for pin in sensor_shutdown:
    GPIO.setup(pin, GPIO.OUT)

# Set all shutdown pins low to turn off each VL53L0X
for pin in sensor_shutdown:
    GPIO.output(pin, GPIO.LOW)

# Keep all low for 1000 ms or so to make sure they reset
time.sleep(1.0)

# Create one object per VL53L0X passing the address to give to each.
for i, pin in enumerate(sensor_shutdown):
    GPIO.output(pin, GPIO.HIGH) # turn on

    # create object with standard address
    tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
    tof.change_address(addr[i]) # change address
    sensors.append(tof) # add to the list
    tof.open()

    print("Sensor[{}] addres set to {}\n".format(i, hex(addr[i]).upper()))
    time.sleep(0.50)

# Set shutdown pin high for the first VL53L0X then
# call to start ranging
#GPIO.output(sensor1_shutdown, GPIO.HIGH)
#time.sleep(0.50)
for i, pin in enumerate(sensor_shutdown):
    GPIO.output(pin, GPIO.HIGH)
    sensors[i].start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
    print("Sensor[{}] started ranging".format(i))

timing = sensors[0].get_timing() # same for all three of them
if timing < 20000:
    timing = 20000
print("Timing %d ms" % (timing/1000))

# ranging

# tune this to accomodate each sensor's error
# cover the laser with the tip of the finger and note the reading:
# the error is =-reading when the sensor is covered
# errors = [-50, -40, -40]
errors = [-40, -40, -40]

import time

interval = 30 # seconds
t_end = time.time() + interval
while time.time() < t_end:

    for i, pin in enumerate(sensor_shutdown):
        distance = sensors[i].get_distance() + errors[i]
        if distance < 0:
            distance = 0
        print('Sensor[{}]:\t{:6.2f}cm\t'.format(i, distance/10.0), end='')
    print()

    # '{:4d}'.format(...) -> format digit over 4 places using ' ' as padding char
    # '{:6.2f}'.format(...) -> format float over 6 places using ' ' as padding char
    #                           rounding to two decimal places
    #print('Sensor[1]:\t{:3d}mm\t{:6.2f}cm\t'.format(distance_1, distance_1/10.0), end='')
    #print('Sensor[2]:\t{:3d}mm\t{:6.2f}cm\t'.format(distance_2, distance_2/10.0), end='')
    #print('Sensor[3]:\t{:3d}mm\t{:6.2f}cm'.format(distance_3, distance_3/10.0))

# stop ranging

for i, pin in enumerate(sensor_shutdown):
    sensors[i].stop_ranging()
    GPIO.output(pin, GPIO.LOW)
    sensors[i].close()

