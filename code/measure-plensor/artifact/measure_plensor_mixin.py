from datetime import datetime
from message_packing_functions import MessagePackingFunctions as mpf
from message_unpacking_functions import MessageUnpackingFunctions as muf


class MeasurePlensorMixin:
    """
    Mixin class for measurement commands to be inherited by the Sensor
    object classes.
    """
    def measure_block_or_sine(self, measurement_settings):
        try:
            # Construct message
            if measurement_settings['command'] == 'BLOCK':
                command_byte = [0x5E]
            elif measurement_settings['command'] == 'SINE':
                command_byte = [0x5C]

            payload_bytes = mpf.construct_payload_bytes_sine_block(
                command_byte,
                measurement_settings['start_frequency'],
                measurement_settings['stop_frequency'],
                measurement_settings['duration']
            )
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)

            # Initialize variables for retry logic
            aggregated_data = []
            self.timeout = (1.2*measurement_settings['duration']) * (1e-6)
            successful_reps = 0
            retry = 0
            timeout = mpf.set_timeout(measurement_settings['duration'])

            while successful_reps < measurement_settings['repetitions'] and retry < 3:
                self.logger.log_error(f"[{self.sensor_id}]: Repetition: {successful_reps+1}, retry: {retry}")
                response = muf.receive_response(message_bytes, timeout)

                if response:
                    ack_nak, payload = muf.extract_payload(response, self.sensor_id)
                    if payload is not None:
                        self.logger.log_error(f"[{self.sensor_id}]: Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")

                    if ack_nak == "ACK":
                        if payload is not None:
                            audio = muf.extract_audio(payload)
                        else:
                            self.logger.log_error("[{self.sensor_id}]: Payload mismatch or processing error, skipping this repetition.")
                            audio = None
                    else:
                        self.logger.log_error(f"[{self.sensor_id}]: NAK or Error: {ack_nak}, skipping this repetition.")
                        audio = None
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No response received within timeout period.")
                    audio = None

                if audio is not None:
                    self.logger.log_error(f"[{self.sensor_id}]: Length audio: {len(audio)}")
                    aggregated_data = aggregated_data + audio
                    # aggregated_data.append(audio)
                    successful_reps += 1
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No audio. Retrying...")
                    retry += 1
                    continue  # Skip the rest of the current loop iteration

            return aggregated_data
        except Exception as e:
            self.logger.log_error(f"Error while measuring block or sine: {e}")
            return None

    def measure_env(self):
        """
        Function to measure the environmental variables.
        """
        try:
            payload_bytes = mpf.construct_payload_single([0x5F])
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)
            self.logger.log_error(f"[{self.sensor_id}]: Message sent in hex: {message_bytes.hex()}")
            timeout = 1
            response = muf.receive_response(message_bytes, timeout)

            if response:
                ack_nak, payload = muf.extract_payload(response, self.sensor_id)

                if payload is not None:
                    self.logger.log_error(f"[{self.sensor_id}]: Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")
                    env_measurement = muf.extract_environment(payload)
                    return env_measurement

                else:
                    self.logger.log_error(f"[{self.sensor_id}]: NAK or Error: {ack_nak}, skipping this repetition.")
                    return None
            else:
                self.logger.log_error(f"[{self.sensor_id}]: No response received within timeout period.")
                return None
        except Exception as e:
            self.logger.log_error(f"[{self.sensor_id}]: Error while measuring environment: {e}")
            return None

    def measure_tof_impulse(self, measurement_settings):
        """
        Function to measure Time Of Flight.
        """
        try:
            # Construct message
            command_byte = [0x5D]

            payload_bytes = mpf.construct_payload_bytes_tof_impulse(
                command_byte,
                measurement_settings['timeout_duration']
            )
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)
            
            # Print message in hex format
            print(f"[{self.sensor_id}]: TOF impulse message (hex): {message_bytes.hex()}")
            self.logger.log_error(f"[{self.sensor_id}]: TOF impulse message (hex): {message_bytes.hex()}")

            # Initialize variables for retry logic
            aggregated_data = []
            self.timeout = (2*measurement_settings['timeout_duration']) * (1e-6)
            successful_reps = 0
            retry = 0
            timeout = mpf.set_timeout(measurement_settings['timeout_duration'])

            while successful_reps < measurement_settings['repetitions'] and retry < 3:
                self.logger.log_error(f"[{self.sensor_id}]: Repetition: {successful_reps+1}, retry: {retry}")
                response = muf.receive_response(message_bytes, timeout)

                if response:
                    ack_nak, payload = muf.extract_payload(response, self.sensor_id)
                    if payload is not None:
                        self.logger.log_error(f"[{self.sensor_id}]: Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")

                    if ack_nak == "ACK":
                        if payload is not None:
                            tof = muf.extract_tof(payload)
                        else:
                            self.logger.log_error("[{self.sensor_id}]: Payload mismatch or processing error, skipping this repetition.")
                            tof = None
                    else:
                        self.logger.log_error(f"[{self.sensor_id}]: NAK or Error: {ack_nak}, skipping this repetition.")
                        tof = None
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No response received within timeout period.")
                    tof = None

                if tof is not None:
                    self.logger.log_error(f"[{self.sensor_id}]: Tof: {int(tof)} ns")
                    aggregated_data.append(int(tof))
                    # aggregated_data.append(audio)
                    successful_reps += 1
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No audio. Retrying...")
                    retry += 1
                    continue  # Skip the rest of the current loop iteration

            return aggregated_data

        except Exception as e:
            self.logger.log_error(f"[{self.sensor_id}]: Error while measuring TOF impulse: {e}")

    def measure_tof_block(self, measurement_settings):
        """
        Function to measure Time Of Flight.
        """
        try:
            # Construct message
            command_byte = [0x64]

            payload_bytes = mpf.construct_payload_bytes_tof_block(
                command_byte,
                measurement_settings['timeout_duration'],
                measurement_settings['tof_half_periods'],
            )
            message_bytes = mpf.construct_message(self.sensor_id, payload_bytes)
            
            # Print message in hex format
            print(f"[{self.sensor_id}]: TOF_BLOCK message (hex): {message_bytes.hex()}")
            self.logger.log_error(f"[{self.sensor_id}]: TOF_BLOCK message (hex): {message_bytes.hex()}")

            # Initialize variables for retry logic
            aggregated_data = []
            self.timeout = (2*measurement_settings['timeout_duration']) * (1e-6)
            successful_reps = 0
            retry = 0
            timeout = mpf.set_timeout(measurement_settings['timeout_duration'])

            while successful_reps < measurement_settings['repetitions'] and retry < 3:
                self.logger.log_error(f"[{self.sensor_id}]: Repetition: {successful_reps+1}, retry: {retry}")
                response = muf.receive_response(message_bytes, timeout)

                if response:
                    ack_nak, payload = muf.extract_payload(response, self.sensor_id)
                    if payload is not None:
                        self.logger.log_error(f"[{self.sensor_id}]: Confirmation: {ack_nak}, Payload: {payload[0:20].hex()}")

                    if ack_nak == "ACK":
                        if payload is not None:
                            tof = muf.extract_tof(payload)
                        else:
                            self.logger.log_error("[{self.sensor_id}]: Payload mismatch or processing error, skipping this repetition.")
                            tof = None
                    else:
                        self.logger.log_error(f"[{self.sensor_id}]: NAK or Error: {ack_nak}, skipping this repetition.")
                        tof = None
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No response received within timeout period.")
                    tof = None

                if tof is not None:
                    self.logger.log_error(f"[{self.sensor_id}]: Tof: {int(tof)} ns")
                    aggregated_data.append(int(tof))
                    # aggregated_data.append(audio)
                    successful_reps += 1
                else:
                    self.logger.log_error(f"[{self.sensor_id}]: No audio. Retrying...")
                    retry += 1
                    continue  # Skip the rest of the current loop iteration

            return aggregated_data

        except Exception as e:
            self.logger.log_error(f"[{self.sensor_id}]: Error while measuring TOF block: {e}")
