# SPDX-FileCopyrightText: 2025 John Romkey
#
# SPDX-License-Identifier: CC0-1.0

import time
import board
import busio
import adafruit_pcf8591.pcf8591 as PCF8591
from adafruit_pcf8591.analog_in import AnalogIn
from adafruit_pcf8591.analog_out import AnalogOut

# Initialize I2C with fallback
try:
    i2c = busio.I2C({{ scl }}, {{ sda }})
except:
    i2c = board.I2C()

# Initialize PCF8591
try:
    pcf = PCF8591.PCF8591(i2c, address={{ address }})
except Exception as e:
    print(f"Error initializing PCF8591: {e}")
    import sys
    sys.exit(1)

print("PCF8591 8-bit ADC/DAC Converter")
print("=" * 40)

# Create analog input and output objects
analog_in_0 = AnalogIn(pcf, PCF8591.A0)
analog_in_1 = AnalogIn(pcf, PCF8591.A1)
analog_in_2 = AnalogIn(pcf, PCF8591.A2)
analog_in_3 = AnalogIn(pcf, PCF8591.A3)
analog_out = AnalogOut(pcf, PCF8591.OUT)

# Display sensor information
print(f"I2C Address: 0x{{ address }}")
print(f"Reference Voltage: {analog_in_0.reference_voltage:.2f}V")
print(f"ADC Resolution: 8-bit (0-255)")
print(f"DAC Resolution: 8-bit (0-255)")
print()

# Main reading loop
while True:
    # Read all ADC channels
    adc_0 = analog_in_0.value
    adc_1 = analog_in_1.value
    adc_2 = analog_in_2.value
    adc_3 = analog_in_3.value
    
    # Convert to voltage
    voltage_0 = analog_in_0.voltage
    voltage_1 = analog_in_1.voltage
    voltage_2 = analog_in_2.voltage
    voltage_3 = analog_in_3.voltage
    
    # Display ADC readings
    print("ADC Readings:")
    print(f"  A0: {adc_0:3d} ({voltage_0:.3f}V)")
    print(f"  A1: {adc_1:3d} ({voltage_1:.3f}V)")
    print(f"  A2: {adc_2:3d} ({voltage_2:.3f}V)")
    print(f"  A3: {adc_3:3d} ({voltage_3:.3f}V)")
    
    # Generate a simple DAC output pattern (sawtooth wave)
    dac_value = (int(time.time() * 2) % 256)
    analog_out.value = dac_value
    dac_voltage = (dac_value / 255.0) * analog_in_0.reference_voltage
    
    print(f"DAC Output: {dac_value:3d} ({dac_voltage:.3f}V)")
    print("-" * 40)
    
    time.sleep(1)
