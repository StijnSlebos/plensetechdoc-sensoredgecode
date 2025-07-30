import RPi.GPIO as GPIO
import time

PIN = 21

class PihatRelay:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)

    def turn_off_turn_on(self, time_sleep = 30):
        GPIO.output(PIN, GPIO.LOW)
        print(" LINE OPEN ")
        time.sleep(1)

        GPIO.output(PIN, GPIO.HIGH)
        print(" LINE CLOSED ")

        time.sleep(time_sleep)

        GPIO.output(PIN, GPIO.LOW)
        print(" LINE OPEN ")

try:
    RLY = PihatRelay()
    print("RELAY POWER CYCLING ...")
    RLY.turn_off_turn_on()
except KeyboardInterrupt:
    print(" Byee ")
finally:
    GPIO.output(PIN, GPIO.LOW)
