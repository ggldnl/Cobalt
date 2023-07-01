# DRV8833 motor driver

This small library was created by me and is intended to provide an easy to use interface on the motor driver. Feel free to contribute!

# Usage 

```python

    with DRV8833() as motor_driver:

        # do stuff
        channel = 'A'
        rate = 0.5
        motor_driver.write(channel, rate)

```

```python

    motor_driver = DRV8833(
        IN_1_A = 21, IN_2_A = 20,   # control pins for left motor
        IN_1_B = 16, IN_2_B = 12,   # control pins for right motor
        ENABLE = 7
    )

    # do stuff
    channel = 'A'
    rate = 0.5
    motor_driver.write(channel, rate)

    motor_driver.close()

```