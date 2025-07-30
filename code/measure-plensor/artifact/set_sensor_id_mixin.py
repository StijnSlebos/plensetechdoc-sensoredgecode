# TODO: this is still a work in progress, not yet tested.


class SetSensorIDMixin:
    def set_sensor_id(self, new_sensor_id):
        """
        Set the sensor ID
        """
        try:
            self.command_byte = [0x61]
            self.sensor_id = 16777215
            # self.sensor_id = 21
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
