import RPi.GPIO as GPIO
import serial
import time
from message_packing_functions import MessagePackingFunctions as mpf

ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=921600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
)


class MessageUnpackingFunctions:
    """
    MessageUnpackingFunctions contains the static functions
    that are needed to extract information from the received
    messages.
    """
    @staticmethod
    def receive_response(message_bytes, timeout) -> bytearray:
        """
        Receives a response from the sensor.

        Parameters:
            message_bytes (bytearray): The message to send to the sensor.
            timeout (float): The maximum time to wait for a response in seconds.

        Returns:
            bytearray: The received response data or None if there was an error.
        """
        try:
            # Setup transmission
            GPIO.output(18, GPIO.HIGH)
            ser.write(message_bytes)
            time.sleep(0.05)  # Wait a bit to ensure the message is sent
            GPIO.output(18, GPIO.LOW)

            response = bytearray()
            start_time = time.time()
            last_data_time = time.time()

            while True:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                    last_data_time = time.time()

                current_time = time.time()
                if ((current_time - last_data_time > 0.01)
                        and (current_time - start_time > timeout)):
                    break

                time.sleep(0.001)  # Adjust polling interval as needed

            if response:
                print(f"Received response (hex): {response.hex()}")
                
            return response if response else None
        except Exception as e:
            print(f"Error while receiving response: {e}")
            return None

    @staticmethod
    def extract_payload(response, sensor_id):
        """
        Extracts the payload from a sensor response, verifying its
        structure and checksum.

        Parameters:
            response (list of int): The full message from the sensor as a
                    list of byte values.

        Returns:
            tuple: (ack_nak, payload) where ack_nak is the status
                    ("ACK", "NAK", or "Error")
                    and payload is the extracted data as a list of bytes.
                    Returns (None, None) if any validation fails.

        # Frame structure:
        # Start Byte: 1 byte
        # Sensor ID: 3 bytes
        # Payload Length: 2 bytes
        # Payload: n bytes (first byte is ACK/NAK)
        # Checksum: 1 byte
        """
        try:
            if len(response) < 6:
                print("Invalid response length")
                return None, None

            # Verify the start byte
            start_byte = response[0]
            if start_byte != 0x5A:
                print(f"Invalid start byte : {start_byte}")
                return None, None

            # Extract and verify the sensor ID
            sensor_id_received = ((response[1] << 16) | (response[2] << 8) |
                                response[3])
            if sensor_id_received != sensor_id:
                print(f"Invalid sensor ID: {sensor_id_received}")
                return None, None

            # Extract payload length
            payload_length = (response[4] << 8) | response[5]

            # Ensure the response length matches the expected length
            expected_length = 6 + payload_length + 1  # 6 header bytes + pyl + chk
            if len(response) != expected_length:
                print(
                    "Response length does not match expected length")
                return None, None

            # Extract and verify the checksum
            calculated_checksum = mpf.calculate_checksum(response[:-1])
            if response[-1] != calculated_checksum:
                print("Invalid checksum")
                return None, None

            # Extract ACK/NAK byte (first byte of the payload)
            ack_nak = response[6]
            if ack_nak == 6:
                ack_nak = "ACK"
            elif ack_nak == 15:
                ack_nak = "NAK"
            else:
                ack_nak = "Error"

            # Extract the rest of the payload
            payload = response[7:6 + payload_length]

            return ack_nak, payload
        except Exception as e:
            print(f"Error while extracting payload: {e}")
            return None, None

    @staticmethod
    def extract_audio(payload):
        """
        Extracts audio data from the payload.

        Parameters:
            payload (list of int): The payload containing audio data.

        Returns:
            list: A list of audio sample values extracted from the payload.
            Returns None if there is an error during extraction.
        """
        try:
            payload_values = []
            for i in range(0, len(payload), 2):
                value = int.from_bytes(payload[i:i+2], byteorder='big',
                                       signed=True)
                payload_values.append(value)
            return payload_values

        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None

    @staticmethod
    def extract_environment(payload):
        """
        Extracts temperature and humidity data from the payload.

        Parameters:
            payload (list of int): The payload containing environment
            sensor data.

        Returns:
            dict: A dictionary with the extracted temperature and humidity
            data. Returns None if the payload length is incorrect.
        """
        try:
            if len(payload) != 8:
                print(
                    "Invalid payload length for temperature and humidity data")
                return None

            inside_temp = (payload[0] << 8 | payload[1]) / 100.0
            inside_humidity = (payload[2] << 8 | payload[3]) / 100.0
            outside_temp = (payload[4] << 8 | payload[5]) / 100.0
            outside_humidity = (payload[6] << 8 | payload[7]) / 100.0

            return {
                "inside_temp": inside_temp,
                "inside_humidity": inside_humidity,
                "outside_temp": outside_temp,
                "outside_humidity": outside_humidity
            }
        except Exception as e:
            print(f"Error while extracting environment: {e}")

    @staticmethod
    def extract_tof(payload):
        """
        Extracts Time of Flight (ToF) data from the payload.

        Parameters:
            payload (list of int): The payload containing ToF data.

        Returns:
            int: The extracted ToF data. Returns None if the payload length
            is incorrect.
        """
        try:
            if len(payload) != 4:
                print("Invalid payload lenght for TOF data")
                return None
            delta_time = ((payload[0] << 24) | (payload[1] << 16) |
                        (payload[2] << 8) | (payload[3]))
            return delta_time
        except Exception as e:
            print(f"Error while extracting TOF: {e}")
