from datetime import datetime
import json

from message_packing_functions import MessagePackingFunctions as mpf
from message_unpacking_functions import MessageUnpackingFunctions as muf


class SetDampingMixin:
    def set_damping_byte(self, damping_level: int = None) -> bool:
        """
        Calibrates the Plensor.
        """
        try:
            if damping_level:
                self.damping_level = damping_level
                self.damping_level_bytes = self._process_damping_level(damping_level)
            else:
                self.damping_level_bytes = self.damping_level_bytes_base

            self.logger.log_error(f"[{self.sensor_id}]: Setting damping byte {self.damping_level_bytes}")
            command_byte = [0x63]
            payload_bytes = mpf.construct_payload_bytes_damping(command_byte, self.damping_level_bytes)
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)

            # Print the complete message in hexadecimal
            self.logger.log_error(f"[{self.sensor_id}]: Message sent in hex: {message_bytes.hex()}")
            response = muf.receive_response(message_bytes, timeout=0.1)

            if response:
                ack_nak, payload = muf.extract_payload(response, self.sensor_id)

                if payload is not None:
                    self.logger.log_error(f"[{self.sensor_id}]: Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")
                    return True

                else:
                    self.logger.log_error(f"[{self.sensor_id}]: NAK or Error: {ack_nak}, skipping this repetition.")
                    return None
            else:
                self.logger.log_error(f"[{self.sensor_id}]: No response received within timeout period.")
                return None
        except Exception as e:
            self.logger.log_error(f"[{self.sensor_id}]: Exception setting damping byte {e}")

    def _process_damping_level(self, damping_level: int) -> bytes:
        """
        Processes the damping level based on the sensor version.

        Parameters:
            damping_level (int): The damping level.

        Returns:
            bytes: The processed damping level bytes.
        """
        if self.sensor_version.startswith("V3.0"):
            self.logger.log_error(f"Sensor {self.sensor_id}: No damping byte applied (V3.0 or lower).")
            return None

        elif self.sensor_version.startswith("V4.0"):
            if damping_level not in [0, 1, 2, 3]:
                damping_level = 0  # Default to 0 if not valid

            self.logger.log_error(f"Sensor {self.sensor_id}: Using damping byte {damping_level} (V4.0).")
            return damping_level.to_bytes(1 if self.sensor_id <= 68 else 2, byteorder='big')

        elif self.sensor_version.startswith("V5.0"):
            if not (0 <= damping_level <= 257):
                damping_level = 0  # Default to 0 if out of range

            self.logger.log_error(f"Sensor {self.sensor_id}: Using damping byte {damping_level} (V5.0).")
            return damping_level.to_bytes(2, byteorder='big')

        else:
            self.logger.log_error(f"Unsupported sensor_version {self.sensor_version} for sensor {self.sensor_id}. Setting damping_level to 0.")
            return self._default_damping_level()
