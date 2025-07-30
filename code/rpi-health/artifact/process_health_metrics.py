import os
import json
import boto3
import time
from datetime import datetime
from ErrorLogger import ErrorLogger


class RPiHealthProcessor:
    def __init__(self):
        self.logger = ErrorLogger.get_instance(directory='/greengrass/v2/logs', log_level=40, log_file_name='RPiHealthDocker.log')
        self.aws_region = os.getenv('AWS_REGION')
        self.database_name = os.getenv('DATABASE_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        self.hostname_filepath = '/home/plense/metadata/container_hostname'
        self.hostname = self.get_hostname()
        self.log_dir = '/home/plense/pi_readings'
        self.timestream = boto3.client('timestream-write', region_name=self.aws_region)

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


    def upload_to_timestream(self, record_timestamp, cpu_temperature, cpu_usage, memory_usage):
        try:
            response = self.timestream.write_records(
                DatabaseName=self.database_name,
                TableName=self.table_name,
                Records=[
                    {
                        'Dimensions': [
                            {'Name': 'host', 'Value': str(self.hostname)}
                        ],
                        'MeasureName': 'cpu_temperature',
                        'MeasureValue': str(cpu_temperature),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    },
                    {
                        'Dimensions': [
                            {'Name': 'host', 'Value': str(self.hostname)}
                        ],
                        'MeasureName': 'cpu_usage',
                        'MeasureValue': str(cpu_usage),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    },
                    {
                        'Dimensions': [
                            {'Name': 'host', 'Value': str(self.hostname)}
                        ],
                        'MeasureName': 'memory_usage',
                        'MeasureValue': str(memory_usage),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    }
                ]
            )
            print("WriteRecords Status: [%s]" % response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            print("Error:", e)

    def process_and_upload(self):
        while True:
            filelist = self.list_files(self.log_dir)
            if not filelist:
                time.sleep(60)
                continue

            for file in filelist:
                filepath = os.path.join(self.log_dir, file)
                with open(filepath, 'r') as json_file:
                    data = json.load(json_file)

                record_timestamp = data['record_timestamp']
                cpu_temperature = data['cpu_temperature']
                cpu_usage = data['cpu_usage']
                memory_usage = data['memory_usage']

                try:
                    # Upload to Timestream
                    self.upload_to_timestream(
                        record_timestamp,
                        cpu_temperature,
                        cpu_usage,
                        memory_usage
                    )

                    # Remove the file after successful upload
                    os.remove(filepath)
                    self.logger.log_info(f"Processed and uploaded {file}")

                except Exception as e:
                    self.logger.log_error(f"Error processing file {file}: {e}")

            time.sleep(60)

if __name__ == "__main__":
    processor = RPiHealthProcessor()
    processor.process_and_upload()