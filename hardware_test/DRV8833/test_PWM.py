import RPi.GPIO as GPIO
import time

# Set the GPIO pins
AIN1 = 21
AIN2 = 20
#BIN1 = 16
#BIN2 = 12

# Set the GPIO mode and pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set the output pins
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
#GPIO.setup(BIN1, GPIO.OUT)
#GPIO.setup(BIN2, GPIO.OUT)

# The recommended max PWM input frequency is 100kHz
pwm_AIN1 = GPIO.PWM(AIN1, 1000)
pwm_AIN2 = GPIO.PWM(AIN2, 1000)
#pwm_BIN1 = GPIO.PWM(BIN1, 1000)
#pwm_BIN2 = GPIO.PWM(BIN2, 1000)

pwm_start = 30
increment = 1

pwm_AIN1.start(0)
pwm_AIN2.start(0)
try:


    """
    
    +------+------+-------------------------+
    | xIN1 | xIN2 |       FAST DECAY        |
    +------+------+-------------------------+
    | PWM  | 0    | Forward PWM, fast decay |
    | 0    | PWM  | Reverse PWM, fast decay |
    +------+------+-------------------------+
    
    """

    while True:

        # channel A backward
        pwm_AIN2.ChangeDutyCycle(0)
        for dc in range(pwm_start, 101, increment):
            print('backward at duty cycle {}'.format(dc))
            pwm_AIN1.ChangeDutyCycle(dc)
            time.sleep(0.1)

        pwm_AIN1.stop()
        pwm_AIN2.stop()
        time.sleep(1)
        pwm_AIN1.start(0)
        pwm_AIN2.start(0)

        # channel A forward
        pwm_AIN1.ChangeDutyCycle(0)
        for dc in range(pwm_start, 101, increment):
            print('forward at duty cycle {}'.format(dc))
            pwm_AIN2.ChangeDutyCycle(dc)
            time.sleep(0.1)

        pwm_AIN1.stop()
        pwm_AIN2.stop()
        time.sleep(1)
        pwm_AIN1.start(0)
        pwm_AIN2.start(0)

except KeyboardInterrupt:
    pass

pwm_AIN1.stop()
pwm_AIN2.stop()
GPIO.cleanup()