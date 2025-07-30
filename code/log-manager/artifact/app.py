import os
import re
import socket
import sys
import time
from datetime import datetime
from typing import List, Optional
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ErrorLogger import ErrorLogger


class LogManager:
    """
    This class manages the logs of all the local components
    running on the Raspberry Pi. This includes both the logs which
    are generated from within the running local processes and
    the system logs per component, which are generated at
    the deployment time of the components.

    In this way, when the Raspberry Pi's are in a remote location for
    a very long time, the internal memory will not be cluttered by
    possibly forever growing logs.
    """

    def __init__(self):
        self.logger = ErrorLogger.get_instance(
            directory='/home/plense/error_logs', 
            log_level=20, 
            log_file_name='LogManagerPlense.log'
        )
        self.logger.log_critical('-----New instance started-----')
        self.system_logs_dir = '/var/log'
        self.plense_logs_dir = '/home/plense/error_logs'
        self.pi_id = self.read_hostname_from_system()
        self.special_logs = ['ModemManagerPlense.log']

    def read_hostname_from_system(self) -> str:
        """
        Reads and returns the hostname of the system.
        """
        try:
            hostname = socket.gethostname()
            return hostname
        except Exception as e:
            self.logger.log_error(f"Error reading hostname from system: {e}")
            return "unknown_hostname"

    def save_logs_locally(self, local_key, log_filepath):
        """
        Saves a log file to local storage.

        Args:
            local_key (str): The local path for the saved file.
            log_filepath (str): The path to the log file to be saved.

        Returns:
            bool: True if the file was saved successfully, else False.
        """
        try:
            import shutil
            os.makedirs(os.path.dirname(local_key), exist_ok=True)
            shutil.copy2(log_filepath, local_key)
            self.logger.log_info(f"Log saved locally: {local_key}")
            return True
        except FileNotFoundError:
            self.logger.log_error("The file was not found")
            return False
        except Exception as e:
            self.logger.log_critical(f"Error saving log file locally: {e}")
            return False

    def scan_logs_dir(self, log_dir='/home/plense/error_logs') -> List:
        """
        Scans the predefined logs folder for all logs currently on
        the Raspberry Pi.

        Returns:
            List[str]: A list of file paths for the log files.
        """
        try:
            logs_list = os.listdir(log_dir)
            return logs_list
        except Exception as e:
            self.logger.log_error(f"Error while scanning logs folder {log_dir}: {e}")
            return []

    def extract_log_timestamp(self, log_filename, log_type='plense') -> Optional[str]:
        """
        Checks whether the log filename contains a timestamp, indicating that it is a
        log file which will not be logged to anymore, from both the system log filename format
        and the Plense log filename format using a regular expression.
        """
        try:
            pattern = r'^[a-zA-Z]+\.log\.(\d{4}-\d{2}-\d{2})$'
            match = re.match(pattern, log_filename)
            if match:
                return True

            pattern = r'^[a-zA-Z]+_(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{1,2})\.log$'
            match = re.match(pattern, log_filename)
            if match:
                return True

            return False
        except Exception as e:
            self.logger.log_error(f"Error extracting log timestamp: {e}")
            return False

    def handle_logs_folder(self, log_dir) -> None:
        """
        Handles the logs folder by processing each log file.
        """
        try:
            logs_list = self.scan_logs_dir(log_dir)
            for log_filename in logs_list:
                if log_filename in self.special_logs:
                    self._handle_special_log(log_dir, log_filename)
                else:
                    self._handle_regular_log(log_dir, log_filename, 'plense')
        except Exception as e:
            self.logger.log_error(f"Error handling logs folder: {e}")

    def _handle_special_log(self, log_dir: str, log_filename: str) -> None:
        """
        Handles special log files that need different processing.
        """
        try:
            log_filepath = os.path.join(log_dir, log_filename)
            if os.path.exists(log_filepath):
                # Create local backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                local_key = f"/home/plense/plensor_data/logs/special/{log_filename}_{timestamp}"
                self.save_logs_locally(local_key, log_filepath)
                
                # Remove original file after successful backup
                os.remove(log_filepath)
                self.logger.log_info(f"Special log processed: {log_filename}")
        except Exception as e:
            self.logger.log_error(f"Error handling special log {log_filename}: {e}")

    def _handle_regular_log(self, log_dir: str, log_filename: str, log_type: str) -> None:
        """
        Handles regular log files.
        """
        try:
            log_filepath = os.path.join(log_dir, log_filename)
            if os.path.exists(log_filepath):
                # Check if log has timestamp (indicating it's complete)
                if self.extract_log_timestamp(log_filename, log_type):
                    # Create local backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    local_key = f"/home/plense/plensor_data/logs/{log_type}/{log_filename}_{timestamp}"
                    self.save_logs_locally(local_key, log_filepath)
                    
                    # Remove original file after successful backup
                    os.remove(log_filepath)
                    self.logger.log_info(f"Regular log processed: {log_filename}")
        except Exception as e:
            self.logger.log_error(f"Error handling regular log {log_filename}: {e}")

    def run(self) -> None:
        """
        Main run loop for log management.
        """
        try:
            self.logger.log_info("Starting local log manager...")
            
            while True:
                # Handle Plense logs
                self.handle_logs_folder(self.plense_logs_dir)
                
                # Handle system logs (optional)
                # self.handle_logs_folder(self.system_logs_dir)
                
                # Sleep for a bit before next iteration
                time.sleep(3600)  # Check every hour
                
        except KeyboardInterrupt:
            self.logger.log_info("Log manager stopped by user")
        except Exception as e:
            self.logger.log_error(f"Error in main run loop: {e}")


if __name__ == "__main__":
    log_manager = LogManager()
    log_manager.run()
