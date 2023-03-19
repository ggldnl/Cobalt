import RPi.GPIO as GPIO
import time

# Set the GPIO pins
AIN1 = 21
AIN2 = 20
BIN1 = 16
BIN2 = 12

# Set the GPIO mode and pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set the output pins
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# Motor A: Forward
def motor_a_forward():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)

# Motor A: Reverse
def motor_a_reverse():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)

# Motor A: OFF
def motor_a_off():
    #GPIO.output(STBY, GPIO.LOW)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)

# Motor B: Forward
def motor_b_forward():
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)

# Motor B: Reverse
def motor_b_reverse():
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)

# Motor B: OFF
def motor_b_off():
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)

# Test the motors
try:

    # Motor A forward
    motor_a_forward()
    time.sleep(2)
    #motor_a_off()

    # Motor A reverse
    motor_a_reverse()
    time.sleep(2)
    motor_a_off()

    # Motor B forward
    motor_b_forward()
    time.sleep(2)
    #motor_b_off()

    # Motor B reverse
    motor_b_reverse()
    time.sleep(2)
    motor_b_off()
    
    
except KeyboardInterrupt:
    GPIO.cleanup()
