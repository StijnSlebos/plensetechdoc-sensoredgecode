import time
import RPi.GPIO as GPIO

# Set up GPIO numbering
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

# Turn on the transceiver
GPIO.setup(18, GPIO.OUT)  # Set GPIO 18 as output
GPIO.setup(4, GPIO.OUT)   # Set GPIO 4 as output

# Set GPIO pin 4 to high
GPIO.output(18, GPIO.LOW)
GPIO.output(4, GPIO.HIGH)
# Wait for proper serial comms setup
time.sleep(2)

# Get status
status4 = GPIO.input(4)
status18 = GPIO.input(18)

# Print the status
print(f"GPIO pin 18 is {'HIGH (1)' if status18 == GPIO.HIGH else 'LOW (0)'}")
print(f"GPIO pin 4 is {'HIGH (1)' if status4 == GPIO.HIGH else 'LOW (0)'}")

# Set GPIO pins to low
GPIO.output(18, GPIO.LOW)
GPIO.output(4, GPIO.LOW)
time.sleep(15)

# Get status
status4 = GPIO.input(4)
status18 = GPIO.input(18)

# Print the status
print(f"GPIO pin 18 is {'HIGH (1)' if status18 == GPIO.HIGH else 'LOW (0)'}")
print(f"GPIO pin 4 is {'HIGH (1)' if status4 == GPIO.HIGH else 'LOW (0)'}")

# Set GPIO pin 4 to high
GPIO.output(4, GPIO.HIGH)
status4 = GPIO.input(4)

# Print the status
print(f"GPIO pin 18 is {'HIGH (1)' if status18 == GPIO.HIGH else 'LOW (0)'}")
print(f"GPIO pin 4 is {'HIGH (1)' if status4 == GPIO.HIGH else 'LOW (0)'}")
