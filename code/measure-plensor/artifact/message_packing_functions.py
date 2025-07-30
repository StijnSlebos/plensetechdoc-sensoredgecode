from datetime import datetime
from error_logger import ErrorLogger


logger = ErrorLogger.get_instance()


class MessagePackingFunctions:
    """
    MessagePackingFunctions contains the base static methods
    to construct hexadecimal messages to communicate with
    the Plensors.
    """
    @staticmethod
    def set_timeout(duration):
        """
        Sets the communication timeout based on the duration of the experiment.

        Parameters:
            duration (int): The duration in microseconds to set the timeout.
        """
        try:
            timeout = (1.2*duration) * (1e-6)
            return timeout
        except Exception as e:
            print(f"Error setting timeout: {e}")
            return None

    @staticmethod
    def construct_payload_single(command_byte):
        """
        Constructs a payload based on a single command byte.

        Parameters:
            command_byte (list of int): The command byte to construct the payload.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # GET, TEMP, CAL, RST BYTE
            if command_byte in ([0x5B], [0x5F], [0x60], [0x62]):
                payload_bytes = command_byte
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes: {e}")
            return None

    @staticmethod
    def construct_payload_bytes_damping(command_byte, damping_level_bytes):
        """
        Constructs a payload that includes a damping level byte.

        Parameters:
            command_byte (list of int): The command byte for the damping setting.
            damping_level (int): The damping level value.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # Damping byte:
            if command_byte == [0x63]:
                payload_bytes = (command_byte + list(damping_level_bytes))
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes damping: {e}")
            return None

    @staticmethod
    def construct_payload_bytes_set(command_byte, new_sensor_id):
        """
        Constructs a payload to set a new sensor ID.

        Parameters:
            command_byte (list of int): The command byte for setting the sensor ID.
            new_sensor_id (list of int): The new sensor ID as a list of bytes.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # SET BYTE
            if command_byte == [0x61]:
                payload_bytes = command_byte + new_sensor_id
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes: {e}")
            return None

    @staticmethod
    def construct_payload_bytes_sine_block(command_byte, start_freq, stop_freq, duration):
        """
        Constructs a payload for sine wave or block wave.

        Parameters:
            command_byte (list of int): The command byte for the sine/block wave.
            start_freq (int): The starting frequency of the wave.
            stop_freq (int): The stopping frequency of the wave.
            duration (int): The duration of the wave.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # SINE, BLOCK BYTE
            if command_byte in ([0x5C], [0x5E]):
                start_freq_bytes = MessagePackingFunctions.freq_to_bytes(start_freq)
                stop_freq_bytes = MessagePackingFunctions.freq_to_bytes(stop_freq)
                duration_bytes = MessagePackingFunctions.duration_to_bytes(duration)
                payload_bytes = (
                    command_byte
                    + start_freq_bytes
                    + stop_freq_bytes
                    + duration_bytes)
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes: {e}")
            return None

    @staticmethod
    def construct_payload_bytes_tof_impulse(command_byte, tof_timeout):
        """
        Constructs a payload for a Time of Flight (ToF) impulse.

        Parameters:
            command_byte (list of int): The command byte for the ToF impulse.
            tof_timeout (list of int): The timeout value for the ToF as a list of bytes.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # TOF impulse byte:
            if command_byte == [0x5D]:
                tof_duration_bytes = MessagePackingFunctions.duration_to_bytes(tof_timeout)
                payload_bytes = command_byte + tof_duration_bytes + [0x00]  # Added 1 byte of zeroes
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes: {e}")
            return None

    @staticmethod
    def construct_payload_bytes_tof_block(command_byte, tof_timeout, tof_half_periods):
        """
        Constructs a payload for a Time of Flight (ToF) block wave.

        Parameters:
            command_byte (list of int): The command byte for the ToF block wave.
            tof_timeout (list of int): The timeout value for the ToF.
            tof_half_periods (list of int): The number of half periods for the ToF.

        Returns:
            list: The constructed payload bytes.
        """
        try:
            # Construct payload based on command byte
            # TOF blockwave byte:
            if command_byte == [0x64]:
                tof_duration_bytes = MessagePackingFunctions.duration_to_bytes(tof_timeout)
                print(f"TOF Duration bytes: {tof_duration_bytes}")
                tof_half_period_bytes = MessagePackingFunctions.half_periods_to_bytes(tof_half_periods)
                print(f"TOF Half period bytes: {tof_half_period_bytes}")
                payload_bytes = (command_byte + tof_duration_bytes + tof_half_period_bytes)
                print(f"Final payload bytes: {payload_bytes}")
            return payload_bytes
        except Exception as e:
            print(f"Exception while constructing payload bytes: {e}")
            return None

    @staticmethod
    def calculate_checksum(data) -> int:
        """
        Calculates the checksum by XORing all bytes in the data.

        Parameters:
            data (list of int): The data over which to compute the checksum.

        Returns:
            int: The computed checksum.
        """
        try:
            checksum = 0
            for byte in data:
                checksum ^= byte
            return checksum
        except Exception as e:
            print(f"Error while constructing checksum: {e}")
            return None

    @staticmethod
    def construct_message(sensor_id: int, payload_bytes) -> bytearray:
        """
        Constructs the complete payload message including the checksum.

        Parameters:
            sensor_id (int): The ID of the sensor.
            payload_bytes (list of int): The bytes representing the payload.

        Returns:
            bytearray: The complete message as a bytearray ready for transmission.
        """
        try:
            start_byte = [0x5A]
            # Sensor ID to bytes
            sensor_id_bytes = [
                (sensor_id >> 16) & 0xFF,
                (sensor_id >> 8) & 0xFF,
                sensor_id & 0xFF]
            # Payload length (2 bytes)
            payload_length = list(len(payload_bytes).to_bytes(2, 'big'))

            # Combine all parts to form the frame without checksum
            frame_without_checksum = (
                start_byte
                + sensor_id_bytes
                + payload_length
                + payload_bytes
            )
            checksum = (
                MessagePackingFunctions
                .calculate_checksum(frame_without_checksum)
            )

            # Append checksum to the frame
            frame = frame_without_checksum + [checksum]

            # Convert to bytearray for transmission
            return bytearray(frame)
        except Exception as e:
            print(f"Exception while constructing payload: {e}")
            return None

    @staticmethod
    def freq_to_bytes(freq):
        """
        Converts a frequency value to bytes.

        Parameters:
            freq (int): The frequency value to be converted.

        Returns:
            list: The frequency value as a list of bytes.
        """
        try:
            freq_bytes = [(freq >> 16) & 0xFF, (freq >> 8)
                          & 0xFF, freq & 0xFF]
            return freq_bytes

        except Exception as e:
            logger.log_error(f"Error while converting frequency to bytes: {e}")
            return None

    @staticmethod
    def duration_to_bytes(duration):
        """
        Converts a duration value to bytes.

        Parameters:
            duration (int): The duration value to be converted.

        Returns:
            list: The duration value as a list of bytes.
        """
        try:
            duration_bytes = [(duration >> 8) & 0xFF, duration & 0xFF]
            return duration_bytes

        except Exception as e:
            logger.log_error(f"Error while converting duration to bytes: {e}")
            return None
    
    @staticmethod
    def half_periods_to_bytes(half_periods):
        """
        Converts a half period value to bytes.

        Parameters:
            half periods (int): The half period value to be converted.

        Returns:
            list: The half period value as a single-byte list.
        """
        try:
            # Ensure the value fits in a single byte (0-255)
            if half_periods > 255:
                logger.log_error(f"Half periods value {half_periods} exceeds maximum (255), capping at 255")
                half_periods = 255
            half_periods_bytes = [half_periods & 0xFF]  # Only use the lowest byte
            return half_periods_bytes

        except Exception as e:
            logger.log_error(f"Error while converting half periods to bytes: {e}")
            return None

