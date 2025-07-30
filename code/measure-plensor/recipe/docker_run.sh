# docker run command for AWS Greengrass component
docker run \
    --privileged \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /home/plense/plensor_data:/home/plense/plensor_data \
    -v /home/plense/error_logs:/home/plense/error_logs \
    -v /greengrass/v2/logs:/greengrass/v2/logs \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v {kernel:rootPath}/ipc.socket:{kernel:rootPath}/ipc.socket \
    -v /etc/hostname:/etc/container_hostname \
    -v /home/plense/.aws/credentials:/.aws/credentials \
    -e IN_CONTAINER=True \
    -e AWS_CONFIG_FILE=/.aws/credentials \
    -e SVCUID \
    -e AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT \
    -e MQTT_TOPIC=\"{configuration:/topic}\" \
    -e MQTT_MESSAGE=\"{configuration:/message}\" \
    -e MQTT_QOS=\"{configuration:/qos}\" \
    --rm 106005884410.dkr.ecr.eu-west-1.amazonaws.com/ggrepository:measure-plensor-002

# docker run command for local testing
docker run \
    --privileged \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /home/plense/plensor_data:/home/plense/plensor_data \
    -v /home/plense/error_logs:/home/plense/error_logs \
    -v /greengrass/v2/logs:/greengrass/v2/logs \
    -v /home/plense/error_logs:/home/plense/error_logs \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/hostname:/etc/container_hostname \
    -v /home/plense/.aws/credentials:/.aws/credentials \
    -e IN_CONTAINER=True \
    -e AWS_CONFIG_FILE=/.aws/credentials \
    measure-plensor:latest