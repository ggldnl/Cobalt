# VL53L0 library

I used [this python API](https://github.com/pimoroni/VL53L0X-python/tree/master/) that is apparently a wrapper for the official c library provided by the manufacturer. This library was not created by me and is intended to provide access to the low level VL53L0 APIs. Please refer to the link for any questions or issues related to the library.

# Using multiple sensors

Before using multiple sensors it is necessary to configure them. Being identical they will have the same address on the I2C bus. It is necessary to connect and disable (with the `xshut` pin to LOW) all of them, activate them one at a time using the standard address and change it before moving on to the next. Once you change the address, you can't turn the sensor off, otherwise it will reset and discard the changes. I developed a simple library that abstracts this logic and make it simple to directly instantiate a VL53L0 sensor with a specific address as well as providing logging.
