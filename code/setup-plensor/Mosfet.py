import RPi.GPIO as GPIO
import time

PIN = 4

class PihatRelay:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN, GPIO.OUT)

    def turn_off_turn_on(self):
        GPIO.output(PIN, GPIO.HIGH)
        print(" LINE OPEN ")

        time.sleep(1)

        GPIO.output(PIN, GPIO.LOW)
        print(" LINE CLOSED ")

        time.sleep(30)

        GPIO.output(PIN, GPIO.HIGH)
        print(" LINE OPEN ")

try:
    MOSFET = PihatRelay()
    print("MOSFET POWER CYCLING ...")
    MOSFET.turn_off_turn_on()
    #time.sleep(10)
except KeyboardInterrupt:
    print(" Byee ")

