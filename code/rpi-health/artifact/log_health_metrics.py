import os
import time
import json
import psutil
from datetime import datetime
from ErrorLogger import ErrorLogger

class TemperatureLogger:
    def __init__(self, templog_dir='temperature_logs', interval=60):
        self.logger = ErrorLogger.get_instance(directory='/home/plense/error_logs', log_level=40, log_file_name='RPiHealthLocal.log')
        self.log_dir = templog_dir
        self.interval = interval
        self.hostname_filepath = '/etc/hostname'
        self.ensure_log_directory()

    def ensure_log_directory(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_cpu_temperature(self):
        try:
            # Read the temperature from the system file
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
                temp = file.read()
            # Convert the temperature to Celsius
            temp_c = float(temp) / 1000.0
            return temp_c
        except FileNotFoundError:
            return "Temperature file not found."
        except Exception as e:
            return f"An error occurred: {e}"

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        memory_info = psutil.virtual_memory()
        return memory_info.percent
    
    def get_hostname(self):
        with open(self.hostname_filepath, 'r') as file:
            # Read the first line and strip any newline characters
            hostname = file.readline().strip()
        return hostname

    def log_health_metrics(self):
        while True:
            cpu_temperature = self.get_cpu_temperature()
            cpu_usage = self.get_cpu_usage()
            memory_usage = self.get_memory_usage()
            record_timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
            log_data = {
                'record_timestamp': record_timestamp,
                'hostname': self.get_hostname(),
                'cpu_temperature': cpu_temperature,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage
            }
            log_filename = os.path.join(self.log_dir, f'temp_log_{record_timestamp}.json')
            try:
                with open(log_filename, 'w') as json_file:
                    json.dump(log_data, json_file, indent=4)
                self.logger.log_info(f"Logged temperature: {cpu_temperature}°C to {log_filename}")
            except Exception as e:
                self.logger.log_error(f"Error writing to JSON file: {e}")
            time.sleep(self.interval)

if __name__ == "__main__":
    temp_logger = TemperatureLogger(templog_dir='/home/plense/pi_readings', interval=120)
    temp_logger.log_health_metrics()
