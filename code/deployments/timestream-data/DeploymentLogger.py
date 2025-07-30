import boto3
import os
import pandas as pd
import time
from datetime import datetime
from ErrorLogger import ErrorLogger


class DeploymentLogger:
    def __init__(self):
        self.logger = ErrorLogger.get_instance()
        self.log_level = os.environ.get('LOG_LEVEL')
        self.logger.set_log_level(self.log_level)
        self.logger.log_critical('---------New instance------------')
        self.aws_region = os.environ.get('AWS_REGION')
        self.timestream_database_name = os.environ.get(
            'TIMESTREAM_DATABASE_NAME'
        )
        self.timestream_table_name = os.environ.get('TIMESTREAM_TABLE_NAME')
        self.timestream = boto3.client(
            'timestream-write',
            region_name=self.aws_region
        )

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
        except Exception as e:
            print(f"Error in converting timestamps: {e}")

    def load_excel_pilot_pi_metadata(self, excel_file_path, sheet_name):
        try:
            # Load the Excel data into a pandas DataFrame
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

            # Display the DataFrame to ensure it's loaded correctly
            print(df)

            # Generate the mappings for host_id and sensor_id
            mappings = []

            for index, row in df.iterrows():
                host_id = row['host_id']
                mapping = {
                    'host_id': host_id,
                    'customer_id': row['customer_id'],
                    'pilot_id': row['pilot_id'],
                    'test_id': row['test_id'],
                    'host_id_start_datetime': row['pi_id_start_date'],
                    'host_id_end_datetime': row['pi_id_end_date']
                }
                mappings.append(mapping)

            # Display the generated mappings
            print(mappings)
            return mappings
        except Exception as e:
            self.logger.log_error(f"Error whilde loading Excel metadata: {e}")

    def insert_pilot_pi_in_timestream(self, mappings):
        try:
            for mapping in mappings:
                self.logger.log_info(f"Inserting mapping: {mapping}")
                records = []

                # Insert start time
                records.append({
                    'Dimensions': [
                        {'Name': 'host_id', 'Value': mapping['host_id']},
                        {'Name': 'customer_id',
                         'Value': mapping['customer_id']}
                    ],
                    'MeasureName': 'host_id_start_datetime',
                    'MeasureValue': mapping['host_id_start_datetime'],
                    'MeasureValueType': 'VARCHAR',
                    # Use current time as mapping time
                    'Time': str(int(time.time() * 1000))
                })

                # Insert end time if it exists
                if pd.notnull(mapping['host_id_end_datetime']):
                    records.append({
                        'Dimensions': [
                            {'Name': 'host_id', 'Value': mapping['host_id']},
                            {'Name': 'customer_id',
                             'Value': mapping['customer_id']}
                        ],
                        'MeasureName': 'host_id_end_datetime',
                        'MeasureValue': mapping['host_id_end_datetime'],
                        'MeasureValueType': 'VARCHAR',
                        # Use current time as mapping time
                        'Time': str(int(time.time() * 1000))
                    })

                # Write records to Timestream
                if records:
                    self.timestream.write_records(
                        DatabaseName=self.timestream_database_name,
                        TableName=self.timestream_table_name,
                        Records=records
                    )
        except Exception as e:
            self.logger.log_error(
                f"Error while inserting metadata in Timestream: {e}"
            )

    def load_excel_pi_sensor_metadata(self, excel_file_path, sheet_name):
        try:
            # Load the Excel data into a pandas DataFrame
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

            # Display the DataFrame to ensure it's loaded correctly
            print(df)

            # Generate the mappings for host_id and sensor_id
            mappings = []

            for index, row in df.iterrows():
                host_id = row['host_id']
                mapping = {
                    'host_id': host_id,
                    'customer_id': row['customer_id'],
                    'sensor_id': row['sensor_id'],
                    'sensor_id_start_datetime':
                        row['sensor_id_start_datetime'],
                    'sensor_id_end_datetime': row['sensor_id_end_datetime']
                }
                mappings.append(mapping)

            # Display the generated mappings
            print(mappings)
            return mappings
        except Exception as e:
            self.logger.log_error(f"Error while loading Excel metadata: {e}")

    def insert_pi_sensor_in_timestream(self, mappings):
        try:
            for mapping in mappings:
                self.logger.log_info(f"Inserting mapping: {mapping}")
                records = []

                # Insert start time
                records.append({
                    'Dimensions': [
                        {'Name': 'host_id', 'Value': mapping['host_id']},
                        {'Name': 'customer_id',
                         'Value': mapping['customer_id']},
                        {'Name': 'sensor_id', 'Value': mapping['sensor_id']}
                    ],
                    'MeasureName': 'sensor_id_start_datetime',
                    'MeasureValue': mapping['sensor_id_start_datetime'],
                    'MeasureValueType': 'VARCHAR',
                    # Use current time as mapping time
                    'Time': str(int(time.time() * 1000))
                })

                # Insert end time if it exists
                if pd.notnull(mapping['sensor_id_end_datetime']):
                    records.append({
                        'Dimensions': [
                            {'Name': 'host_id', 'Value': mapping['host_id']},
                            {'Name': 'customer_id',
                             'Value': mapping['customer_id']},
                            {'Name': 'sensor_id',
                             'Value': mapping['sensor_id']}
                        ],
                        'MeasureName': 'sensor_id_end_datetime',
                        'MeasureValue': mapping['sensor_id_end_datetime'],
                        'MeasureValueType': 'VARCHAR',
                        # Use current time as mapping time
                        'Time': str(int(time.time() * 1000))
                    })

                # Write records to Timestream
                if records:
                    self.timestream.write_records(
                        DatabaseName=self.timestream_database_name,
                        TableName=self.timestream_table_name,
                        Records=records
                    )
        except Exception as e:
            self.logger.log_error(
                f"Error while inserting metadata in Timestream: {e}"
            )
