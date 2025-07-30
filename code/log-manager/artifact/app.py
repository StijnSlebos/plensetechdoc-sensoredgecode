import boto3
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
    This class manages the logs of all the Greengrass components
    running on the Raspberry Pi. This includes both the logs which
    are generated from within the running Docker containers and
    the Greengrass native logs per component, which are generated at
    the deployment time of the components.

    In this way, when the Raspberry Pi's are in a remote location for
    a very long time, the internal memory will not be cluttered by
    possibly forever growing logs.
    """

    def __init__(self):
        self.logger = ErrorLogger.get_instance(
            directory='/home/plense/error_logs', log_level=20, log_file_name='LogManagerPlense.log')
        self.logger.log_critical('-----New instance started-----')
        self.gg_logs_dir = '/greengrass/v2/logs'
        self.plense_logs_dir = '/home/plense/error_logs'
        self.pi_id = self.read_hostname_from_system()
        self.s3 = boto3.client('s3')
        self.bucket_name = os.environ.get('BUCKET_NAME')
        self.aws_region = os.environ.get('AWS_REGION')
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

    def upload_logs_to_s3(self, s3_key, log_filepath):
        """
        Uploads a log file to our S3 bucket.

        Args:
            s3_key (str): The S3 key for the uploaded file.
            log_filepath (str): The path to the log file to be uploaded.

        Returns:
            bool: True if the file was uploaded successfully, else False.
        """
        try:
            s3 = boto3.client('s3', region_name=self.aws_region)
            self.logger.log_info(f"Bucket to save to: {self.bucket_name}")
            s3.upload_file(
                Filename=log_filepath, Bucket=self.bucket_name, Key=s3_key)
            return True
        except FileNotFoundError:
            self.logger.log_error("The file was not found")
            return False
        except Exception as e:
            self.logger.log_critical(f"Error saving log file to S3: {e}")
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
        log file which will not be logged to anymore, from both the GG log filename format
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
            else:
                return None

        except Exception as e:
            self.logger.log_error(f"Error while extracting log timestamp: {e}")
            return None

    def handle_logs_folder(self, log_dir) -> None:
        """
        Handles the logs folder for either the GG logs or the Plense logs.
        Args:
            log_dir (str): Path to the directory containing log files to process.
                          Can be either Greengrass logs or Plense logs directory.

        Returns:
            None: This function does not return anything.
        """
        try:
            if log_dir == self.gg_logs_dir:
                logs_file_list = self.scan_logs_dir(self.gg_logs_dir)
                log_type = 'gg'
            elif log_dir == self.plense_logs_dir:
                logs_file_list = self.scan_logs_dir(self.plense_logs_dir)
                log_type = 'plense'
            else:
                logs_file_list = []
                raise ValueError(f"Invalid log directory: {log_dir}")

            for log_filename in logs_file_list:
                print(f"Handling log {log_filename}")
                
                try:
                    if log_filename in self.special_logs:
                        self._handle_special_log(log_dir, log_filename)
                        continue

                    self._handle_regular_log(log_dir, log_filename, log_type)

                except PermissionError as e:
                    self.logger.log_error(f"Permission denied while handling log {log_filename}: {e}")
                    continue
                except IOError as e:
                    self.logger.log_error(f"I/O error while handling log {log_filename}: {e}")
                    continue
                except Exception as e:
                    self.logger.log_error(f"Unexpected error while handling log {log_filename}: {e}")
                    continue
        except FileNotFoundError as e:
            self.logger.log_error(f"Log directory not found: {log_dir} - {e}")
        except PermissionError as e:
            self.logger.log_error(f"Permission denied accessing log directory {log_dir}: {e}")
        except Exception as e:
            self.logger.log_error(f"Unexpected error while processing logs folder {log_dir}: {e}")

    def _handle_special_log(self, log_dir: str, log_filename: str) -> None:
        """
        Handle special log files that need daily uploads.
        Special log files are logs that are generated by shell scripts,
        which do not get timestamp appendices when the log files are
        of yesterday.
        Args:
            log_dir (str): Directory path containing the log files
            log_filename (str): Name of the special log file to handle

        Returns:
            None: This function does not return anything
        """
        try:
            # Create a timestamped copy of the log file
            timestamp = datetime.now().strftime('%Y-%m-%d')
            timestamped_filename = f"{log_filename}.{timestamp}"

            # Create a copy of the log file with timestamp
            source_path = os.path.join(log_dir, log_filename)
            dest_path = os.path.join(log_dir, timestamped_filename)

            try:
                with open(source_path, 'r') as source:
                    with open(dest_path, 'w') as dest:
                        dest.write(source.read())
            except IOError as e:
                raise IOError(f"Failed to copy log file {log_filename}: {e}")

            # Upload the timestamped copy
            log_s3_key = f"pi_errorlogs/{self.pi_id}/{timestamped_filename}"
            log_upload_success = self.upload_logs_to_s3(log_s3_key, dest_path)

            if log_upload_success:
                self.logger.log_info(f"Special log file {timestamped_filename} uploaded successfully.")
                try:
                    # Remove the timestamped copy
                    os.remove(dest_path)
                    # Clear the original log file but keep it
                    open(source_path, 'w').close()
                except OSError as e:
                    self.logger.log_error(f"Error cleaning up log files: {e}")

        except Exception as e:
            raise RuntimeError(f"Failed to handle special log {log_filename}: {e}")

    def _handle_regular_log(self, log_dir: str, log_filename: str, log_type: str) -> None:
        """Handle regular log files with timestamps."""
        try:
            logs_timestamp = self.extract_log_timestamp(log_filename, log_type)
            if logs_timestamp:
                log_s3_key = f"pi_errorlogs/{self.pi_id}/{log_filename}"
                log_path = os.path.join(log_dir, log_filename)

                log_upload_success = self.upload_logs_to_s3(log_s3_key, log_path)
                if log_upload_success:
                    self.logger.log_info(f"Log file {log_filename} uploaded successfully.")
                    try:
                        os.remove(log_path)
                    except OSError as e:
                        self.logger.log_error(f"Error removing log file {log_filename}: {e}")

        except Exception as e:
            raise RuntimeError(f"Failed to handle regular log {log_filename}: {e}")

    def run(self) -> None:
        """
        Runs the LogManager class once every day. This function scans the logs folder,
        processes each log file by determining its type (internal or Greengrass),
        extracts timestamps, creates S3 keys, and uploads the logs to an S3 bucket.
        Successfully uploaded logs are then removed from the local filesystem.

        The process repeats every 24 hours.

        Logs information about each step and any errors encountered.
        """
        try:
            self.handle_logs_folder(log_dir=self.gg_logs_dir)
            self.handle_logs_folder(log_dir=self.plense_logs_dir)

        except Exception as e:
            self.logger.log_error(f"Error in main loop: {e}")


if __name__ == '__main__':
    log_manager = LogManager()
    log_manager.run()
