import boto3
import json

# Initialize the Greengrass client
client = boto3.client('greengrassv2')

def create_deployment(description, config_file_path):
    # Read deployment configuration from the local JSON file
    with open(config_file_path, 'r') as file:
        deployment_config = json.load(file)


    # Create deployment
    response = client.create_deployment(
        targetArn=deployment_config['targetArn'],
        deploymentName=description,
        components=deployment_config['components'],
    )

    print("Deployment created successfully:")
    print(json.dumps(response, indent=4))
    print()


def main():
    # Prompt user for deployment description
    print()
    description = input("Enter the description of the deployment: ")

    # Path to the JSON configuration file
    config_file_path = 'deployments/plensepi00003.json'

    # Create the deployment
    create_deployment(description, config_file_path)


if __name__ == "__main__":
    main()
