import boto3
import logging
import os
from datetime import datetime
from ErrorLogger import ErrorLogger
from JSONHandler import JSONHandler


class ComponentHandler:
    """
    Custom functionality that is used in multiple Plense Docker
    container Greengrass components to handle different sensor
    types.
    """
    _instance = None

    @classmethod
    def get_instance(cls, directory=None, log_level=logging.ERROR):
        if cls._instance is None:
            cls._instance = cls(directory, log_level=log_level)
        return cls._instance

    def __init__(
            self,
            directory=None,
            log_level=logging.ERROR,
            log_file_name='error.log'):
        """
        Initializes the ErrorLogger, setting up the logging configuration
        including the log file name, format, and log level.

        Parameters:
            - directory (str): The directory where the log file will be stored.
            - log_file_name (str): The name of the file where log messages will
              be stored.
            - log_level (int): The logging level (e.g., logging.ERROR,
              logging.DEBUG).
        """
        if self._instance is not None:
            raise Exception("ErrorLogger is a singleton!")
        self.logger = ErrorLogger.get_instance()
        self.json_handler = JSONHandler.get_instance()
        self.aws_region = os.getenv('AWS_REGION')
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        self.s3 = boto3.client('s3')

    def as_component(self):
        """
        Checks whether the script runs as a Greengrass component
        Docker container.
        """
        try:
            AS_COMPONENT = os.environ.get('AS_COMPONENT', False)
            if AS_COMPONENT:
                self.logger.log_info("In a container.")
            else:
                self.logger.log_info("Not in a container.")

        except Exception as e:
            self.logger.log_error(
                f"Exception checking if the script runs as a component: {e}"
            )

        return AS_COMPONENT

    def read_hostname_from_file(self):
        """
        Reads and returns the pi_id hostname.
        """
        try:
            base_dir = os.getcwd()
            hostname_file_path = os.path.join(
                base_dir,
                'etc',
                'container_hostname'
            )
        except Exception as e:
            self.logger.log_error(f"Error reading hostname from file: {e}")

        try:
            with open(hostname_file_path, 'r') as file:
                # Read the first line and strip any newline characters
                hostname = file.readline().strip()
                self.logger.log_error(f"Hostname: {hostname}")
            return hostname
        except Exception as e:
            self.logger.log_error(f"Error reading hostname: {e}")
            return None

    def get_metadata_from_cache(
            self,
            sensor_type="TEST_SENSOR_TYPE",
            sensor_id="#TEST_PI_ID"):
        """
        Read in the metadata of the specified sensor_type sensor_id.
        """
        try:
            # base_dir = os.getcwd()
            base_dir = '/home/plense'
            filename = (sensor_type + sensor_id + '_metadata.json')
            filepath = os.path.join(base_dir, 'metadata', filename)

            metadata = self.json_handler.safe_json_load(filepath)
            return metadata

        except Exception as e:
            self.logger.log_error(f"Error getting metadata from cache: {e}")

    def get_metadata_by_type(self, sensor_type="TEST_SENSOR"):
        """
        Read in the locally cached metadata of the specified sensor_type.
        This function is used for sensor type of which only one sensor is
        connected to one Raspberry Pi.
        """
        try:
            base_dir = os.getcwd()  # Base directory to search
            metadata_dir = os.path.join(base_dir, 'metadata')
            print(metadata_dir)
            for filename in os.listdir(metadata_dir):
                if (filename.startswith(sensor_type)
                        and filename.endswith('_metadata.json')):
                    filepath = os.path.join(metadata_dir, filename)
                    metadata = self.json_handler.safe_json_load(filepath)
            return metadata
        except Exception as e:
            self.logger.log_error(f"Error getting metadata from cache"
                                  f" based on sensor type {sensor_type}: {e}")

    def save_logs_to_s3(
            self, sensor_type, pi_id, date, s3_client, logfile='error.log'):
        """
        Save logs of the sensor components to S3 to a dedicated subfolder
        that is defined by the sensor_type of the component that uses this
        function. Consecutively, the name of the log is defined by the
        pi_id and the date.
        """
        try:
            s3_log_filename = (
                'pi_errorlogs/'
                + sensor_type
                + '/'
                + pi_id
                + '#'
                + date
                + '.log'
            )
        except Exception as e:
            self.logger.log_error(f"Error creating S3 log filename: {e}")

        try:
            s3_client.upload_file(logfile, self.bucket_name, s3_log_filename)
        except Exception as e:
            self.logger.log_error(f"Error uploading log file to S3: {e}")

    def create_item_in_ddb(
            self, metadata, record_timestamp, ddb_client):
        """
        Create an item in the DynamoDB table that has the metadata attributes
        in it. This ensures that the DynamoDB table has an overview of all S3
        keys in the all/ subfolder, even when the data pipeline is broken.

        Parameters:
        - metadata (dict): The metadata dictionary to store in DynamoDB.
        - ddb_client (boto3.client): A boto3 DynamoDB client.
        - table_name (str): Name of the DynamoDB table.

        Returns:
        - response (dict): The response from the DynamoDB service.
        """
        try:
            # Construct the item to insert into DynamoDB
            item = {key: {'S': str(value)} for key, value in metadata.items()}
            item['record_timestamp'] = {'S': record_timestamp}

            # Insert the item into DynamoDB
            response = ddb_client.put_item(TableName=self.table_name, Item=item)
            print("Successfully created item in DynamoDB:", response)
            return response
        except Exception as e:
            print(f"Error creating item in DynamoDB: {e}")
            raise

    def create_s3_key_ddb_style(self, metadata, record_date, record_time, input_signal='BLOCK'):
        try:
            s3_key = (
                input_signal
                + '#' + metadata['sensor_type']['S']
                + metadata['pilot_id']['S']
                + metadata['sensor_id']['S']
                + '_'
                + record_date
                + 'T'
                + record_time
            )
            return s3_key
        except Exception as e:
            self.logger.log_error(f"Error creating S3 key string: {e}")

    def create_s3_key_plain_style(self, metadata, record_date, record_time, input_signal='BLOCK'):
        try:
            s3_key = (
                input_signal
                + '#' + metadata['sensor_type']
                + metadata['pilot_id']
                + metadata['sensor_id']
                + '_'
                + record_date
                + 'T'
                + record_time
            )
            return s3_key
        except Exception as e:
            self.logger.log_error(f"Error creating S3 key string: {e}")

    def safe_create_s3_key(self, metadata, record_date, record_time, input_signal='BLOCK'):
        """
        Creates the main part of the S3 key for measurements of all different
        sensor types. First checks the format of the metadata and handles
        accordingly.

        Parameters:
            - metadata (dict):

        Returns:
            - s3_key (string): main part of the S3 key.
        """
        try:
            metadata_format = self.determine_metadata_format(metadata)
        except Exception as e:
            self.logger.log_error(f"Error determining metadata format: {e}")

        try:
            if metadata_format == 'ddb':
                s3_key = self.create_s3_key_ddb_style(
                    metadata, record_date, record_time, input_signal)
            elif metadata_format == 'plain':
                s3_key = self.create_s3_key_plain_style(
                    metadata, record_date, record_time, input_signal)
            return s3_key
        except Exception as e:
            self.logger.log_error(f"Error creating S3 key: {e}")

    def determine_metadata_format(self, metadata):
        """
        Determine the format of the passed metadata dictionary.

        Args:
            metadata (dict): A dictionary representing the metadata.

        Returns:
            str: A string indicating the format of the metadata:
                'ddb' for DynamoDB format (e.g., {"S": "value"}),
                'plain' for plain format (e.g., "value"),
                'unknown' if the format cannot be determined.
        """
        if not metadata or not isinstance(metadata, dict):
            return 'unknown'

        # Check if the metadata is in DynamoDB format
        if all(isinstance(value, dict) and 'S' in value
               and isinstance(value['S'], str) for value in metadata.values()):
            return 'ddb'

        # Check if the metadata is in plain format
        elif all(isinstance(value, str) for value in metadata.values()):
            return 'plain'

        # If the format is not recognized
        return 'unknown'

    def save_ultrasound_to_s3(
            self, measurement, metadata):
        """
        Save an ultrasound measurement with the attached metadata to our
        S3 bucket.

        Parameters:
            - measurement (array):
            - metadata (dict):

        Returns:
            - True when the upload to S3 is successfull.
        """
        try:
            ultrasound_and_metadata = {
                "metadata": metadata,
                "settings": self.json_handler.safe_json_load("settings.json"), # TODO Thijs: check of dit nice is
                "data": measurement  # TODO measurement in int16
            }
            json_string = (
                self.json_handler.safe_json_dumps(ultrasound_and_metadata)
            )
            encoded_string = json_string.encode('utf-8')
            s3_key = (
                'all/'
                + self.safe_create_s3_key(metadata)
                + '.json'
            )
            self.s3.put_object(
                Bucket=self.bucket_name, Key=s3_key, Body=encoded_string)
            return True
        except Exception as e:
            self.logger.log_error(f"Exception putting item in S3: {e}")