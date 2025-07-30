from datetime import datetime
from message_packing_functions import MessagePackingFunctions as mpf
from message_unpacking_functions import MessageUnpackingFunctions as muf


class CalibrateSensorMixin:
    def calibrate_plensor(self) -> bool:
        """
        Calibrates the Plensor.
        """
        try:
            self.logger.log_error(f" Calibrating sensor_id {self.sensor_id}")
            command_byte = [0x60]
            self.timeout = 15
            payload_bytes = mpf.construct_payload_single(command_byte)
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)
            # Print the complete message in hexadecimal
            self.logger.log_error(f"[{self.sensor_id}]: Message sent in hex: {message_bytes.hex()}")
            response = muf.receive_response(message_bytes, timeout=15)

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
            self.logger.log_error(f"[{self.sensor_id}]: Exception setting sensor id {e}")
