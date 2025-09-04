# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import busio
import board
import adafruit_bno055
import sys

try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except Exception as e:
    print(e)
    i2c = board.I2C()

sensor = adafruit_bno055.BNO055_I2C(i2c, address={{ address }})

print("BNO055 9-Axis Absolute Orientation Sensor")
print("=" * 50)

# Check if sensor is detected
if not sensor:
    print("Error: BNO055 sensor not found!")
    print("Please check your wiring and I2C address.")
    sys.exit(1)

print(f"✅ BNO055 sensor detected at address 0x{{ address:02X}}")
print()


# Main sensor reading loop
print("Starting continuous sensor readings...")
print()

while True:
    print(f"Accelerometer (m/s^2): {sensor.acceleration}")
    print(f"Magnetometer (microteslas): {sensor.magnetic}")
    print(f"Gyroscope (rad/sec): {sensor.gyro}")
    print(f"Euler angle: {sensor.euler}")
    print(f"Quaternion: {sensor.quaternion}")
    print(f"Linear acceleration (m/s^2): {sensor.linear_acceleration}")
    print(f"Gravity (m/s^2): {sensor.gravity}")
    print()

    time.sleep(1)
