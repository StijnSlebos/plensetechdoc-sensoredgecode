import os
import json
import time
from datetime import datetime
from ErrorLogger import ErrorLogger


class RPiHealthProcessor:
    def __init__(self):
        self.logger = ErrorLogger.get_instance(
            directory='/home/plense/error_logs', 
            log_level=40, 
            log_file_name='RPiHealthLocal.log'
        )
        self.hostname_filepath = '/home/plense/metadata/container_hostname'
        self.hostname = self.get_hostname()
        self.log_dir = '/home/plense/pi_readings'

    def get_hostname(self):
        try:
            if not os.path.exists(self.hostname_filepath):
                raise FileNotFoundError(f"The file {self.hostname_filepath} does not exist.")
            
            with open(self.hostname_filepath, 'r') as file:
                hostname = file.read().strip()
                if not hostname:
                    raise ValueError("The file is empty, no hostname found.")
                return hostname
        
        except Exception as e:
            self.logger.log_error(f"An unexpected error occurred: {e}")
            raise

    def list_files(self, directory):
        try:
            with os.scandir(directory) as entries:
                files = [entry.name for entry in entries if entry.is_file()]
                return files
        except FileNotFoundError:
            self.logger.log_error("The directory does not exist.")
            return None
        except PermissionError:
            self.logger.log_error("Permission denied.")
            return None
        except Exception as e:
            self.logger.log_error(f"An error occurred: {e}")
            return None

    def convert_to_epoch_millis(self, timestamp_str):
        """
        Convert a timestamp from 'YYYY-MM-DDTHHMMSS' format to Unix epoch time in milliseconds.

        Args:
            timestamp_str (str): The timestamp string in 'YYYY-MM-DDTHHMMSS' format.

        Returns:
            int: The timestamp in Unix epoch time (milliseconds).
        """
        try:
            # Parse the input timestamp string
            parsed_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H%M%S")
            
            # Convert to Unix epoch time in milliseconds
            epoch_millis = str(int(parsed_timestamp.timestamp() * 1000))
            
            return epoch_millis
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e

    def save_health_data_locally(self, record_timestamp, cpu_temperature, cpu_usage, memory_usage):
        """
        Save health metrics to local storage instead of Timestream.
        """
        try:
            health_data = {
                'hostname': str(self.hostname),
                'record_timestamp': record_timestamp,
                'cpu_temperature': cpu_temperature,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            output_dir = '/home/plense/plensor_data/health_metrics'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"health_{self.hostname}_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(health_data, f, indent=2)
            
            self.logger.log_info(f"Health data saved locally: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error saving health data locally: {e}")
            return False

    def process_and_save(self):
        """
        Process health metrics and save them locally.
        """
        try:
            self.logger.log_info("Starting health metrics processing...")
            
            # Get current timestamp
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
            
            # Simulate health metrics (in real implementation, these would be actual measurements)
            cpu_temperature = 45.5  # Example temperature
            cpu_usage = 25.3        # Example CPU usage percentage
            memory_usage = 60.7     # Example memory usage percentage
            
            # Save health data locally
            success = self.save_health_data_locally(
                current_timestamp, 
                cpu_temperature, 
                cpu_usage, 
                memory_usage
            )
            
            if success:
                self.logger.log_info("Health metrics processed and saved successfully")
            else:
                self.logger.log_error("Failed to process and save health metrics")
                
        except Exception as e:
            self.logger.log_error(f"Error in process_and_save: {e}")

    def run(self):
        """
        Main run loop for health metrics processing.
        """
        try:
            self.logger.log_info("Starting RPi health processor...")
            
            while True:
                self.process_and_save()
                time.sleep(300)  # Process every 5 minutes
                
        except KeyboardInterrupt:
            self.logger.log_info("Health processor stopped by user")
        except Exception as e:
            self.logger.log_error(f"Error in main run loop: {e}")


if __name__ == "__main__":
    processor = RPiHealthProcessor()
    processor.run()