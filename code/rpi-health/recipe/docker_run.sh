docker run \
    --privileged \
    -v /greengrass/v2/logs:/greengrass/v2/logs \
    -v /home/plense/pi_readings:/home/plense/pi_readings \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /etc/hostname:/etc/container_hostname \
    -v /home/plense/.aws/credentials:/.aws/credentials \
    -e IN_CONTAINER=True \
    -e AWS_CONFIG_FILE=/.aws/credentials \
    -e AWS_REGION=eu-west-1 \
    -e BUCKET_NAME=dev-signal-bucket \
    -e TABLE_NAME=sensor-table-dev \
    -v {kernel:rootPath}/ipc.socket:{kernel:rootPath}/ipc.socket \
    -e SVCUID \
    -e AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT \
    -e MQTT_TOPIC=\"{configuration:/topic}\" \
    -e MQTT_MESSAGE=\"{configuration:/message}\" \
    -e MQTT_QOS=\"{configuration:/qos}\" \
    106005884410.dkr.ecr.eu-west-1.amazonaws.com/ggrepository:internal-temp-003

docker run \
    --privileged \
    -v /greengrass/v2/logs:/greengrass/v2/logs \
    -v /home/plense/pi_readings:/home/plense/pi_readings \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /etc/hostname:/etc/container_hostname \
    -v /home/plense/.aws/credentials:/.aws/credentials \
    -e IN_CONTAINER=True \
    -e AWS_CONFIG_FILE=/.aws/credentials \
    -e AWS_REGION=eu-west-1 \
    -e DATABASE_NAME=rpi-health \
    -e TABLE_NAME=plense-fleet-manager-exp \
    rpi-health:latest
    106005884410.dkr.ecr.eu-west-1.amazonaws.com/ggrepository:internal-temp-001
