import boto3
import json
import subprocess

# Initialize the Greengrass client
client = boto3.client('greengrassv2')

# Push the image to ECR
def build_and_push_image(image_tag, component_name):
    command = f"docker build -t 106005884410.dkr.ecr.eu-central-1.amazonaws.com/ggrepository:{image_tag} --push ."
    
    # Specify the working directory where the command should be executed
    working_directory = f"../components/{component_name}/artifact/"
    
    # Execute the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_directory)

    # Wait for the process to finish and capture output
    stdout, stderr = process.communicate()

    # Check if there were any errors
    if process.returncode != 0:
        print("Error:", stderr.decode())
    else:
        print("Command executed successfully:", stdout.decode())
        # Path to the JSON configuration file
        config_file_path = f'../components/{component_name}/recipe/config.json'
        create_component_version(config_file_path)

# Create a new component version update
def create_component_version(config_file_path):
    print("Creating new component version")

    # I need to pass the parameters dynamically to the json file

    # Read deployment configuration from the local JSON file
    with open(config_file_path, 'r') as file:
        component_version = json.load(file)

    print(component_version)

    # encoding the JSON object
    bytes = json.dumps(component_version).encode('utf-8')

    # Create component version
    response = client.create_component_version(
        inlineRecipe=bytes,
    )

    print("Component version created successfully", response)

def main():
    # Prompt user for deployment description
    print()
    component_name = input("Enter the name of the component to update: ")
    # image_tag = input("Enter the image tag: ")

    # Create the deployment
    # build_and_push_image(image_tag, component_name)
    config_file_path = f'../components/{component_name}/recipe/config.json'
    create_component_version(config_file_path)


if __name__ == "__main__":
    main()