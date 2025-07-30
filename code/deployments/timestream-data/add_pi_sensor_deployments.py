import os
from DeploymentLogger import DeploymentLogger

# Set environment variables
os.environ['AWS_REGION'] = 'eu-central-1'
os.environ['TIMESTREAM_DATABASE_NAME'] = 'deployment-database-prd'
os.environ['TIMESTREAM_TABLE_NAME'] = 'pi-sensor-deployment'


def main():
    dl = DeploymentLogger()
    excel_file_path = (
        r"C:\Users\MirandavanDuijn\OneDrive - Plense Technologies\Documents - "
        r"Research & Development\Operations\Raspberry Pi and sensor fleet.xlsx"
    )
    sheet_name = 'Sensor @ pi'  # Specify the sheet name
    mappings = dl.load_excel_pi_sensor_metadata(excel_file_path, sheet_name)
    dl.insert_pi_sensor_in_timestream(mappings)


if __name__ == '__main__':
    main()
