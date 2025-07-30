import RPi.GPIO as GPIO
import serial
import time
from ErrorLogger import ErrorLogger


class SensorSetup:
    def __init__(self):
        """
        Initializes the SerialCommunication class.

        This constructor sets up the initial parameters, including GPIO and
        serial configurations, and initializes various lists to hold sensor 
        data.
        """
        # Initialize classes
        self.logger = ErrorLogger.get_instance(directory='/home/plense/error_logs', log_level=40, log_file_name='SetupPlensor.log')
        self.running = True

        # Define the parameters
        self.sensor_id = 99999
        self.sensor_type = "Plensor"
        new_sensor_id = 99999
        self.tof_frequency = 40000
        self.half_cycle_period = 1 / (2 * self.tof_frequency)

        # Setup GPIO
        self.setup_gpio()

        # Set up the serial connection
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=921600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )

        # Pack parameters into to bytes
        self.sensor_id_bytes = [(self.sensor_id >> 16) & 0xFF,
                                (self.sensor_id >> 8)
                                & 0xFF, self.sensor_id & 0xFF]
        self.new_sensor_id = [(new_sensor_id >> 16) & 0xFF,
                              (new_sensor_id >> 8)
                              & 0xFF, new_sensor_id & 0xFF]

        self.data_per_sensor = {}

        # Wait for proper serial comms setup
        time.sleep(2)

    def initialize_sensor_data(self, sensor_id):
        if sensor_id not in self.data_per_sensor:
            self.data_per_sensor[sensor_id] = {
                "timestamps": [],
                "inside_temps": [],
                "inside_humidities": [],
                "outside_temps": [],
                "outside_humidities": [],
                "tof_data": []
            }

    def calculate_checksum(self, data):
        """
        Calculates the checksum by XORing all bytes in the data.

        Parameters:
            data (list of int): The data over which to compute the checksum.

        Returns:
            int: The computed checksum.
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def setup_gpio(self):
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

    def extract_payload(self, response):
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

        if len(response) < 6:
            self.logger.log_error("Invalid response length")
            return None, None

        # Verify the start byte
        start_byte = response[0]
        if start_byte != 0x5A:
            self.logger.log_error(f"Invalid start byte : {start_byte}")
            return None, None

        # Extract and verify the sensor ID
        sensor_id_received = ((response[1] << 16) | (response[2] << 8) |
                              response[3])
        if sensor_id_received != self.sensor_id:
            self.logger.log_error(f"Invalid sensor ID: {sensor_id_received}")
            return None, None

        # Extract payload length
        payload_length = (response[4] << 8) | response[5]

        # Ensure the response length matches the expected length
        expected_length = 6 + payload_length + 1  # 6 header bytes + pyl + chk
        if len(response) != expected_length:
            self.logger.log_error("Response length does not match expected length")
            return None, None

        # Extract and verify the checksum
        calculated_checksum = self.calculate_checksum(response[:-1])
        if response[-1] != calculated_checksum:
            self.logger.log_error("Invalid checksum")
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

    def send_message(self):
        """
        Sends a message to the sensor based on the command byte and
        reads the response.

        This function sends a constructed message to the sensor and
        then listens for a response. It ensures that it listens for at least
        the timeout period but stops if no data is received for 10ms.
        # Frame structure:
        # Start Byte: 1 byte
        # Sensor ID: 3 bytes
        # Payload Length: 2 bytes
        # Payload: n bytes
        # Checksum: 1 byte
        """
        # Construct payload based on command byte
        # GET, TEMP, CAL, RST BYTE
        if self.command_byte in ([0x5B], [0x5F], [0x60], [0x62]):
            payload_bytes = self.command_byte
        # SET BYTE
        elif self.command_byte == [0x61]:
            payload_bytes = self.command_byte + self.new_sensor_id
        # Start byte
        start_byte = [0x5A]

        # Payload length (2 bytes)
        payload_length = list(len(payload_bytes).to_bytes(2, 'big'))

        # Combine all parts to form the frame without checksum
        frame_without_checksum = (start_byte + self.sensor_id_bytes +
                                  payload_length + payload_bytes)

        # Calculate checksum
        checksum = self.calculate_checksum(frame_without_checksum)

        # Append checksum to the frame
        frame = frame_without_checksum + [checksum]

        # Convert to bytearray for transmission
        message_bytes = bytearray(frame)

        # Print the complete message in hexadecimal
        print("Message sent in hex:", message_bytes.hex())

        # Setup transmission
        GPIO.output(18, GPIO.HIGH)
        self.ser.write(message_bytes)
        time.sleep(0.05)  # Wait a bit to ensure the message is sent
        GPIO.output(18, GPIO.LOW)

        # Polling for response with timeout
        start_time = time.time()
        response = bytearray()
        last_data_time = time.time()

        while True:
            # Check for data waiting
            if self.ser.in_waiting > 0:
                response.extend(self.ser.read(self.ser.in_waiting))
                last_data_time = time.time()

            # Check if minimum timeout has been reached and no data for 10ms
            if (time.time() - last_data_time > 0.01) and (time.time() - start_time > self.timeout):
                break

            time.sleep(0.001)  # Adjust polling interval as needed

        if response:
            ack_nak, payload = self.extract_payload(response)

            if payload is not None:
                print(f"Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")
            else:
                print(f"NAK or Error: {ack_nak}, skipping this repetition.")
                return None
        else:
            print("No response received within timeout period.")
            return None

    def set_sensor_id(self, new_sensor_id):
        """
        Set the sensor ID
        """
        try:
            self.command_byte = [0x61]
            self.sensor_id = 16777215
            # self.sensor_id = 1
            self.sensor_id_bytes = [(self.sensor_id >> 16) & 0xFF,
                                        (self.sensor_id >> 8)
                                        & 0xFF, self.sensor_id & 0xFF]
            self.new_sensor_id = [(new_sensor_id >> 16) & 0xFF,
                              (new_sensor_id >> 8)
                              & 0xFF, new_sensor_id & 0xFF]
            self.timeout = 1
            self.send_message()
        except Exception as e:
            self.logger.log_error(f"Exception setting sensor id {e}")

    def get_sensor_id(self, sensor_id):
        """
        Get ACK on a sensor ID
        """
        try:
            self.command_byte = [0x5B]
            self.sensor_id = sensor_id
            self.sensor_id_bytes = [(self.sensor_id >> 16) & 0xFF,
                                        (self.sensor_id >> 8)
                                        & 0xFF, self.sensor_id & 0xFF]
            self.timeout = 1
            return self.send_message()
        except Exception as e:
            self.logger.log_error(f"Exception setting sensor id {e}")

    def scan_rs485_line(self, sensor_id_from, sensor_id_to):
        """
        Sweep the line to check what sensors are currently connected
        since there is a timeout, a sensor id range is requested
        """
        sensors_on_line = []
        print(f"Scanning line for sensors in range ({sensor_id_from},{sensor_id_to})")
        for sen_id in range(sensor_id_from, sensor_id_to+1, 1):
            if self.get_sensor_id(sen_id):
                print(f"Found sensor_id = {sen_id} on line")
                sensors_on_line.append(sen_id)
        
        if sensors_on_line is not None:
            print(f"Found sensors {sensors_on_line} on RS485 line")
            return sensors_on_line
        else: #SUPERFLUOUS CODE
            return None

    def run(self):
        try:
            """
            Main method to run the communication process, handling setup
            and infinite listening for messages.
            Command bytes:
            0x5B: GET BYTE, no params
            0x5C: SINE BYTE, start stop freq, duration
            0x5D: TOF BYTE, start stop freq, duration
            0x5E: BLOCK BYTE, start stop freq, duration
            0x5F: TEMP BYTE, no params
            0x60: CAL BYTE, no params
            0x61: SET BYTE, new sensor id
            0x62: RST BYTE, no params
            """
            # Calibration script
            sensor_ids = self.get_connected_sensors()  # TODO: or with get bytes loop
            for sensor_id in sensor_ids:
                self.initialize_sensor_data(sensor_id)
                print(f"Calibrating sensor_id {sensor_id}")
                self.sensor_id = sensor_id
                self.sensor_id_bytes = [(self.sensor_id >> 16) & 0xFF,
                                        (self.sensor_id >> 8)
                                        & 0xFF, self.sensor_id & 0xFF]
                self.command_byte = [0x60]
                self.timeout = 15
                self.send_message()
                print(f"Setting the damping level of sensor_id {sensor_id}")
                self.damping_level = [0 & 0xFF]
                self.command_byte = [0x63]
                self.timeout = 0.1
                self.send_message()
            while True:
                try:
                    self.timeout = 1
                    self.listen_for_messages()
                except Exception as e:
                    self.logger.log_error(f"Exception occurred: {e}")
        except KeyboardInterrupt:
            print("Program interrupted by user.")
        finally:
            self.ser.close()
            GPIO.cleanup()
            print("Serial port and GPIO cleaned up")
            self.save_data_to_csv()


if __name__ == "__main__":
    sensor_setup = SensorSetup()
    sensor_id_new = 122
    # sensor_setup.set_sensor_id(sensor_id_new)
    sensor_setup.get_sensor_id(sensor_id_new)
    # sensor_setup.scan_rs485_line(0,160)
