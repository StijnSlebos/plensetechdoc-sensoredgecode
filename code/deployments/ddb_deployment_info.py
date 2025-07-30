import boto3
import os
from datetime import datetime, timedelta, timezone

aws_region = os.environ.get('AWS_REGION')
table_name = os.environ.get('TABLE_NAME')

def create_dynamodb_items():
    # Initialize the DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    table = dynamodb.Table(table_name)

    # Common attributes
    pi_id = "plensepi00018"
    begin_timestamp = '2024-07-24T170000'
    pilot_id = "#HEATSTRESS"
    test_id = "#TOMATO"
    customer_id = "#SYNGENTA"
    sensor_type = "PLENSOR"
    sensor_version = "V4.0"
    # ventilation_type = "ventilation"
    # climate_room = "4"
    # par_treatment = "high"
    plot_id = "hot"
    
    # Base end_timestamp
    base_end_timestamp = datetime(2024, 11, 1, 17, 0, 5, tzinfo=timezone.utc)
    
    # Sensor IDs
    sensor_ids = [f"#{str(sensor_id).zfill(5)}" for sensor_id in list(range(44, 53)) + [30]]
    
    # Create and put items into the table
    for i, sensor_id in enumerate(sensor_ids):
        # Increment the base end_timestamp by one second for each sensor
        end_timestamp = base_end_timestamp + timedelta(seconds=i)
        
        # Format the timestamp to the required format
        end_timestamp_str = end_timestamp.strftime('%Y-%m-%dT%H%M%S')

        # Create the item
        item = {
            'pi_id': pi_id,
            'end_timestamp': end_timestamp_str,
            'begin_timestamp': begin_timestamp,
            'pilot_id': pilot_id,
            'test_id': test_id,
            'customer_id': customer_id,
            'sensor_type': sensor_type,
            'sensor_id': sensor_id,
            'sensor_version': sensor_version,
            'plot_id': plot_id
            # 'climate_room': climate_room,
            # 'ventilation_type': ventilation_type,
            # 'par_treatment': par_treatment
        }
        
        # Put the item into the DynamoDB table
        table.put_item(Item=item)
        print(f"Inserted item for sensor_id {sensor_id} with end_timestamp {end_timestamp_str}")

# Example usage
create_dynamodb_items()
