import json
import os
import socket


def create_json_files(sensor_ids, output_dir, **kwargs):
    os.makedirs(output_dir, exist_ok=True)

    hostname = socket.gethostname()

    for sensor_id in sensor_ids:
        sensor_id_str = f"#{str(sensor_id).zfill(5)}"
        filename = f"Plensor{sensor_id_str}_metadata.json"

        # Determine the sensor version based on sensor_id
        if 9 <= int(sensor_id) <= 68:
            print(f"Sensor id: {int(sensor_id)}, so version V4.0")
            sensor_version = "V4.0"
        else:
            sensor_version = "V5.0"
            print(f"Sensor id: {int(sensor_id)}, so version V5.0")

        data = {
            "sensor_id": sensor_id_str,
            "pi_id": hostname,
            "sensor_type": "PLENSOR",
            "sensor_version": sensor_version,
            **kwargs
        }

        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Created: {filepath}")


if __name__ == "__main__":
    try:
        file_path = input("Enter the path to the JSON file with inputs: ").strip()
        output_dir = input("Enter the output dir for the metadata files: ").strip()
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                sensor_ids = data.pop("sensor_ids")
                create_json_files(sensor_ids, output_dir, **data)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    except ValueError as e:
        print(f"Invalid input: {e}")