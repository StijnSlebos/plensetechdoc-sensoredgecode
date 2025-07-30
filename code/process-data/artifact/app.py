import boto3
import json
import numpy as np
import os
import scipy
import soundfile as sf
import time
from datetime import datetime
from ComponentHandler import ComponentHandler
from ErrorLogger import ErrorLogger
from JSONHandler import JSONHandler
from PreProcessor import Preprocessor
from xedge_plense_tools import LocalDataLoader_edge, SignalOperator_edge, PreprocessingOperator_edge


class SignalProcessor:
    """
    SignalProcessor has functionality to process the signals.
    """

    def __init__(self):
        """
        Initializes the DataManager class.
        """
        # Initialize classes
        self.logger = ErrorLogger.get_instance(directory='/home/plense/error_logs', log_level=40, log_file_name='ProcessDataDocker.log')
        self.edge_preprocessor = PreprocessingOperator_edge('/home/plense/plensor_data/audio_data/time_domain_not_processed','/home/plense/plensor_data/audio_data/time_domain_processed')
        self.logger.log_info("New instance started -------")
        self.logger.set_log_level('ERROR')
        self.component_handler = ComponentHandler()
        self.json_handler = JSONHandler.get_instance()
        self.metadata_dir = '/home/plense/metadata'
        # Get the AWS region from the environment variable passed at Docker runtime
        self.aws_region = os.getenv('AWS_REGION')
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        self.timestream_database_name = os.getenv('TIMESTREAM_DATABASE_NAME')
        self.timestream_table_name = os.getenv('TIMESTREAM_TABLE_NAME')
        self.running = True
        self.ddb_client = boto3.client('dynamodb', region_name=self.aws_region)
        self.timestream = boto3.client('timestream-write', region_name=self.aws_region)

    def list_files(self, directory):
        """
        List all files and directories in a given directory using os.scandir.

        Parameters:
        - directory (str): The path to the directory to list files from.

        Returns:
        - list: A list of filenames found in the directory.
        """
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

    def save_file_to_s3(self, filepath, s3_key):
        """
        Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified, file_name is used
        :return: True if file was uploaded, else False
        """
        try:
            s3 = boto3.client('s3', region_name=self.aws_region)
            self.logger.log_info(f"Bucket to save to: {self.bucket_name}")
            response = s3.upload_file(
                Filename=filepath, Bucket=self.bucket_name, Key=s3_key)
            return True
        except FileNotFoundError:
            self.logger.log_error("The file was not found")
            return False
        except Exception as e:
            self.logger.log_critical(f"Error saving flac to S3: {e}")
            return False

    def get_input_signal_from_key(self, key):
        """
        Extract the input signal from the key.

        Parameters:
            key: the key

        Returns:
            input signal (str): Either BLOCK or SINE.
        """
        try:
            input_signal = key.split('#')[0]
            return input_signal
        except Exception as e:
            self.logger.log_error(f"Error extracting input signal from filename: {e}")

    def create_or_update_item_in_ddb(self, sensor_id, record_timestamp, file_metadata, measurement_metadata, ddb_client):
        """
        Create or update an item in the DynamoDB table that has the metadata attributes
        in it. This ensures that the DynamoDB table has an overview of all S3
        keys in the all/ subfolder, even when the data pipeline is broken.

        Parameters:
        - metadata (dict): The metadata dictionary to store in DynamoDB.
        - record_timestamp (str): The timestamp of the record.
        - input_signal (str): The input signal value.
        - successful_reps (int): Number of successful repetitions.
        - std_fft (str): Standard FFT value.
        - ddb_client (boto3.client): A boto3 DynamoDB client.

        Returns:
        - response (dict): The response from the DynamoDB service.
        """
        try:
            # Prepare the update expression and expression attribute values dynamically
            update_expression = 'SET input_signal = :input_signal'
            expression_attribute_values = {
                ':input_signal': {'S': str(file_metadata['meas_id'])},
            }
            # Add measurement metadata to DDB expression
            for key, value in measurement_metadata.items():
                if key not in ['sensor_id']:
                    update_expression += f', {key} = :{key}'
                    expression_attribute_values[f':{key}'] = {'S': str(value)}
            # Insert the item into DynamoDB
            response = ddb_client.update_item(
                TableName=self.table_name,
                Key={
                    'record_timestamp': {'S': record_timestamp},
                    'sensor_id': {'S': sensor_id}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            self.logger.log_info(f"Successfully created or updated item in DynamoDB: {response}")
            return response
        except Exception as e:
            self.logger.log_error(f"Error creating or updating item in DynamoDB: {e}")
            raise

    def create_env_item_ddb(self, sensor_id, record_timestamp, env_data, ddb_client):
        """
        Update an item in the DynamoDB table with the metadata of the
        sensor and the environmental measurements.

        Parameters:
            - metadata: Dictionary containing metadata attributes.
            - record_timestamp: Timestamp of the record.
            - env_data: Dictionary containing environmental measurements.
            - ddb_client: Boto3 DynamoDB client.
        """
        try:
            # Prepare the update expression and attribute values
            update_expression = 'SET '
            expression_attribute_values = {}

            # Add environmental data to the update expression and attribute values
            for key, value in env_data.items():
                update_expression += f'{key} = :{key}, '
                expression_attribute_values[f':{key}'] = {'S': str(value)}

            # Remove trailing comma and space from the update expression
            update_expression = update_expression.rstrip(', ')

            # Update the item in DynamoDB
            response = ddb_client.update_item(
                TableName=self.table_name,
                Key={
                    'record_timestamp': {'S': record_timestamp},
                    'sensor_id': {'S': sensor_id}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )

            self.logger.log_info(
                f"Successfully updated env item in DynamoDB: {response}")
            return response

        except Exception as e:
            self.logger.log_error(f"Error updating env item in DDB: {e}")
            return None

    def create_tof_item_ddb(self, metadata, record_timestamp, tof_data, prefix, ddb_client):
        """
        Update an item in the DynamoDB table with the metadata of the
        sensor and the TOF measurements.

        Parameters:
            - metadata: Dictionary containing metadata attributes.
            - record_timestamp: Timestamp of the record.
            - tof_data: Dictionary containing TOF measurements.
            - ddb_client: Boto3 DynamoDB client.
        """
        try:
            # Prepare the update expression and attribute values
            update_expression = 'SET '
            expression_attribute_values = {}

            # Create attribute keys for TOF based on number of TOF repetitions
            for i in range(len(tof_data)):
                key = f"{prefix}_{i+1}"
                update_expression += f'{key} = :{key}, '
                expression_attribute_values[f':{key}'] = {'S': str(tof_data[i])}

            # Add metadata to the update expression and attribute values
            for key, value in metadata.items():
                if key not in ['sensor_id']:  # Exclude primary key from update expression
                    update_expression += f'{key} = :{key}, '
                    expression_attribute_values[f':{key}'] = {'S': str(value)}

            # Remove trailing comma and space from the update expression
            update_expression = update_expression.rstrip(', ')

            # Update the item in DynamoDB
            response = ddb_client.update_item(
                TableName=self.table_name,
                Key={
                    'record_timestamp': {'S': record_timestamp},
                    'sensor_id': {'S': metadata['sensor_id']}
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )

            self.logger.log_info(
                f"Successfully updated TOF item in DynamoDB: {response}")
            return response

        except Exception as e:
            self.logger.log_error(f"Error updating env item in DDB: {e}")
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

    def add_timestream_health_log(self, sensor_id, data_type, input_signal, health_metric_name, health_metric_value, record_timestamp):
        """
        Creates a timestream log in the FLIR table in the health-monitor database.
        It logs the following health metrics:

        record_timestamp + sensor_id + upload size per ata item that is uploaded to S3
        Upload size is in bytes.
        """
        try:
            response = self.timestream.write_records(
                DatabaseName=self.timestream_database_name,
                TableName=self.timestream_table_name,
                Records=[
                    {
                        'Dimensions': [
                            {'Name': 'sensor_id', 'Value': str(sensor_id)},
                            {'Name': 'input_signal_type', 'Value': input_signal},
                            {'Name': 'data_type', 'Value': data_type}
                        ],
                        'MeasureName': health_metric_name,
                        'MeasureValue': str(health_metric_value),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    }
                ]
            )
            print("health WriteRecords Status: [%s]" % response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            print("Error:", e)

    def add_timestream_environment_log(self, sensor_id, inside_temperature, outside_temperature, inside_humidity, outside_humidity, record_timestamp):
        """
        Add all Plensor environment readings to the timestream table plensor-health.
        """
        try:
            response = self.timestream.write_records(
                DatabaseName=self.timestream_database_name,
                TableName=self.timestream_table_name,
                Records=[
                    {
                        'Dimensions': [
                            {'Name': 'sensor_id', 'Value': str(sensor_id)},
                            {'Name': 'input_signal_type', 'Value': "all"},
                            {'Name': 'data_type', 'Value': "environment"}
                        ],
                        'MeasureName': "inside_temp",
                        'MeasureValue': str(inside_temperature),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    },
                    {
                        'Dimensions': [
                            {'Name': 'sensor_id', 'Value': str(sensor_id)},
                            {'Name': 'input_signal_type', 'Value': "all"},
                            {'Name': 'data_type', 'Value': "environment"}
                        ],
                        'MeasureName': "outside_temp",
                        'MeasureValue': str(outside_temperature),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    },
                    {
                        'Dimensions': [
                            {'Name': 'sensor_id', 'Value': str(sensor_id)},
                            {'Name': 'input_signal_type', 'Value': "all"},
                            {'Name': 'data_type', 'Value': "environment"}
                        ],
                        'MeasureName': "inside_hum",
                        'MeasureValue': str(inside_humidity),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    },
                    {
                        'Dimensions': [
                            {'Name': 'sensor_id', 'Value': str(sensor_id)},
                            {'Name': 'input_signal_type', 'Value': "all"},
                            {'Name': 'data_type', 'Value': "environment"}
                        ],
                        'MeasureName': "outside_hum",
                        'MeasureValue': str(outside_humidity),
                        'MeasureValueType': 'DOUBLE',
                        'Time': self.convert_to_epoch_millis(record_timestamp)
                    }
                ]
            )
            print("Env WriteRecords Status: [%s]" % response['ResponseMetadata']['HTTPStatusCode'])
        except Exception as e:
            self.logger.log_error(f"Error while adding environment measurements to timestream: {e}")

    def process_time_domain(self, execute_preprocessing = True, segment_length=25000, process_num_segments=10):
        """
        Scans the time-domain folder and processes the contents.
        """
        # Process time-domain measurements
        source_directory = '/home/plense/plensor_data/audio_data/time_domain_not_processed'
        target_directory = '/home/plense/plensor_data/audio_data/time_domain_processed'
        filelist = self.list_files(source_directory)

        for file in filelist:
            try:
                # Extract file data
                self.logger.log_info(f"Processing signal {file}")
                # get file metadata from basename:
                file_metadata = LocalDataLoader_edge.interpret_measurementfile_basename(file)
                file_path = os.path.join(source_directory, file)
                sensor_id = file_metadata['sensor_id']
                record_timestamp = LocalDataLoader_edge.plense_datetime_to_stringtime(file_metadata['datetime'])

                # PREPROCESSING
                preprocessing_type = 'pp002'
                transfer_file_path = file_path
                new_filename = file
                timestream_info_dict = {'max_amp': None, 'successful_reps': None, 'filesize': None, 'sum_of_squares': None}

                # Read out existing file
                self.logger.log_error(f"Preprocessing file {file}")
                audio_data_int16 = LocalDataLoader_edge.load_audio_file(file_path, flc_type="int16", expected_segment_length=segment_length)
                
                timestream_info_dict['successful_reps'] = int(len(audio_data_int16) / segment_length)
                timestream_info_dict['max_amp'] = max(audio_data_int16.astype(np.float32) / 32767.0)
                timestream_info_dict['sum_of_squares'] = np.sum(np.square(audio_data_int16.astype(np.float32) / 32767.0))/timestream_info_dict['successful_reps']
                timestream_info_dict['filesize'] = os.path.getsize(transfer_file_path)

                if timestream_info_dict['successful_reps'] < process_num_segments:
                    raise Exception(f"Repetitions is less than required repetitions of {process_num_segments}: {timestream_info_dict['successful_reps']}")

                if execute_preprocessing:
                    try:

                        if preprocessing_type == 'pp002' and audio_data_int16 is not None:
                            processed_audio_signal = (
                                self
                                .edge_preprocessor
                                .preprocess_pp002(
                                    audio_data_int16,
                                    no_mean=True,
                                    segments_to_keep=int(process_num_segments*0.9),
                                    segments=process_num_segments)
                            )
                            pass
                        else: 
                            processed_audio_signal = None

                        if processed_audio_signal is not None:
                            # Update timestream data:
                            timestream_info_dict['max_amp'] = max(processed_audio_signal)
                            timestream_info_dict['sum_of_squares'] = np.sum(np.square(processed_audio_signal))

                            # If processing succeeded: save new file and update the transfer file path
                            file_metadata['meas_id'] = file_metadata["meas_id"]+preprocessing_type
                            new_filename = LocalDataLoader_edge.build_measurementfile_basename(file_metadata)
                            transfer_file_path = os.path.join(target_directory, new_filename)
                            
                            # Save processed audio to new filepath
                            sf.write(transfer_file_path, processed_audio_signal, samplerate=500000, subtype='PCM_24')

                            timestream_info_dict['filesize'] = os.path.getsize(transfer_file_path)
                            # Remove original file, once processed file is built
                            os.remove(file_path)
                        else:
                            raise Exception("Save/upload the original file, error has occurred in processing")
                        
                    except Exception as e:
                        self.logger.log_error(f"Error processing the audio file: {e}")
                else: 
                    pass

                measurement_type = file_metadata['meas_id']
                
                # Upload the preprocessed file to S3
                try:
                    upload_success = self.save_file_to_s3(transfer_file_path, 'time_domain/' + new_filename)
                    if upload_success:
                        self.add_timestream_health_log(sensor_id, "time_domain", measurement_type, "upload_size", timestream_info_dict['filesize'], record_timestamp)
                        self.add_timestream_health_log(sensor_id, "time_domain", measurement_type, "max_amp", timestream_info_dict['max_amp'], record_timestamp)
                        self.add_timestream_health_log(sensor_id, "time_domain", measurement_type, "successful_reps", timestream_info_dict['successful_reps'], record_timestamp)
                        self.add_timestream_health_log(sensor_id, "time_domain", measurement_type, "sum_of_squares", timestream_info_dict['sum_of_squares'], record_timestamp)
                        os.remove(transfer_file_path)
                        self.logger.log_info(f"Upload to S3 successful, deleting {transfer_file_path}")
                    else:
                        self.logger.log_error("Uploading to S3 did not work")
                except Exception as e:
                    self.logger.log_error(f"Error uploading time-domain data to S3: {e}")

                # Update DDB
                self.create_or_update_item_in_ddb(
                        sensor_id,
                        record_timestamp,
                        file_metadata,
                        timestream_info_dict,
                        self.ddb_client)
                time.sleep(1)

            except Exception as e:
                self.logger.log_error(f"Error processing time-domain signal: {e}")

    def process_tof(self):
        # Process TOF measurements
        tof_dir = '/home/plense/plensor_data/audio_data/tof'
        tof_filelist = self.list_files(tof_dir)

        for tof_file in tof_filelist:
            try:
                self.logger.log_info(f"Processing TOF")
                # Split the filename by '#' and verify the number of parts
                file_parts = tof_file.split('#')
                if len(file_parts) >= 4:
                    # Old logic for files with 4 or more parts
                    sensor_id = '#' + file_parts[3].split('_')[0]
                    record_timestamp = tof_file.split('_')[-1].split('.')[0]
                else:
                    # New logic for files with fewer than 4 parts
                    sensor_id = '#' + file_parts[1].split('_')[0]
                    record_timestamp = tof_file.split('_')[-1].split('.')[0]
                metadata = self.component_handler.get_metadata_from_cache('Plensor', sensor_id)
                tof_filepath = tof_dir + '/' + tof_file

                with open(tof_filepath, 'r') as json_file:
                    tof_data = json.load(json_file)
                    tof_ns = tof_data["tof_ns"]
                    half_cycles = tof_data["half_cyles"]
                # Get the number of non-null tof_ns entries
                non_null_entries = sum(1 for value in tof_ns if value is not None)

                tof_ns_prefix = "tof_ns"
                tof_success = self.create_tof_item_ddb(
                    metadata,
                    record_timestamp,
                    tof_ns,
                    tof_ns_prefix,
                    self.ddb_client)
                
                half_cycles_prefix = "half_cycles"
                half_cycles_success = self.create_tof_item_ddb(
                    metadata,
                    record_timestamp,
                    half_cycles,
                    half_cycles_prefix,
                    self.ddb_client
                )

                if tof_success and half_cycles_success and os.path.exists(tof_filepath):
                    self.add_timestream_health_log(sensor_id, "TOF", "all", "upload_size", os.path.getsize(tof_filepath), record_timestamp)
                    self.add_timestream_health_log(sensor_id, "TOF", "all", "num_tof_ns", len(tof_ns), record_timestamp)
                    self.add_timestream_health_log(sensor_id, "TOF", "all", "num_tof_ns_filled", non_null_entries, record_timestamp)
                    os.remove(tof_filepath)
                else:
                    self.logger.log_error("No successful environment DDB ingestion.")
            except Exception as e:
                self.logger.log_error(
                    f"Error processing TOF measurement: {e}")

    def process_environment(self):
        # Process environmental measurements
        env_dir = '/home/plense/plensor_data/environment_data'
        env_filelist = os.listdir(env_dir)

        for env_file in env_filelist:
            try:
                self.logger.log_info(f"Processing signal {env_file}")
                # Split the filename by '#' and verify the number of parts
                file_parts = env_file.split('#')
                if len(file_parts) >= 4:
                    # Old logic for files with 4 or more parts
                    sensor_id = '#' + file_parts[3].split('_')[0]
                    record_timestamp = env_file.split('_')[-1].split('.')[0]
                else:
                    # New logic for files with fewer than 4 parts
                    sensor_id = '#' + file_parts[1].split('_')[0]
                    record_timestamp = env_file.split('_')[-1].split('.')[0]
                env_filepath = env_dir + '/' + env_file

                with open(env_filepath, 'r') as json_file:
                    env_data = json.load(json_file)

                env_success = self.create_env_item_ddb(
                    sensor_id,
                    record_timestamp,
                    env_data,
                    self.ddb_client)

                if env_success and os.path.exists(env_filepath):
                    self.add_timestream_health_log(sensor_id, "environment", "all", "upload_size", os.path.getsize(env_filepath), record_timestamp)
                    self.add_timestream_environment_log(
                        sensor_id,
                        env_data["inside_temp"],
                        env_data["outside_temp"],
                        env_data["inside_humidity"],
                        env_data["outside_humidity"],
                        record_timestamp)
                    os.remove(env_filepath)
                else:
                    self.logger.log_error("No successful environment DDB ingestion.")
            except Exception as e:
                self.logger.log_error(
                    f"Error processing environment measurement: {e}")
                
    def get_preprocessing_config(self):
        """
        Fetches the preprocessing boolean, determining whether or not
        the preprocessing will be executed.
        """
        try:
            app_settings = self.json_handler.safe_json_load(
                os.path.join(
                    self.metadata_dir,
                    "app_settings.json"
                )
            )
            setting_segment_length = app_settings.get("segment_length", 25000)
            setting_process_segments = app_settings.get("process_segments", 10)
            setting_preprocess_bool = app_settings.get("preprocess", True)
            return {'segment_length': setting_segment_length, 'process_segments': setting_process_segments, 'preprocess': setting_preprocess_bool}
        except Exception as e:
            self.logger.log_error(
                f"Error while fetching preprocessing setting: {e}"
                " setting to default: True"
            )
            return True

    def run(self):
        """
        Check the specified directory for existing files.
        If measurements exist, process them and move them to
        the folder time_domain_processed.
        """
        try:
            while True:
                self.logger.set_log_level("INFO")

                preprocessing_configuration = self.get_preprocessing_config()
                self.process_time_domain(
                    execute_preprocessing=preprocessing_configuration['preprocess'], 
                    segment_length=preprocessing_configuration['segment_length'], 
                    process_num_segments=preprocessing_configuration['process_segments'])
                
                # self.process_tof()
                self.process_environment()

                time.sleep(60)
        except Exception as e:
            self.logger.log_error(f"Error running main loop: {e}")


if __name__ == '__main__':
    # Add 5s sleep time so the SD card has time to mount
    time.sleep(5)
    sp = SignalProcessor()
    sp.run()
