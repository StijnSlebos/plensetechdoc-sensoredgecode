import RPi.GPIO as GPIO
import time


class SerialCommunicationSetup:
    """
    SerialCommunicationSetup.
    """
    @staticmethod
    def setup_gpio():
        try:
            """
            Sets up the GPIO pins for communication with the sensor.

            This function configures the GPIO mode and sets the initial states of the GPIO pins used.
            """
            # Turn on the transceiver
            GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
            GPIO.setup(18, GPIO.OUT)  # Set GPIO 18 as output
            GPIO.setup(4, GPIO.OUT)   # Set GPIO 4 as output

            # Set GPIO pins to high
            GPIO.output(18, GPIO.LOW)
            GPIO.output(4, GPIO.HIGH)
            # Wait for proper serial comms setup
            time.sleep(2)
        except Exception as e:
            print(f"Error while setting up GPIO: {e}")

    @staticmethod
    def close_gpio():
        """
        Cleans the GPIO pins for the communication with the sensor.
        Explicitly sets the pins to LOW before cleaning.
        """
        try:
            # Set GPIO pins to low
            GPIO.output(18, GPIO.LOW)
            GPIO.output(4, GPIO.LOW)
            GPIO.cleanup()
        except Exception as e:
            print(f"Error while closing GPIO: {e}")
