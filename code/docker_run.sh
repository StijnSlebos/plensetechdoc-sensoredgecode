docker run \
    --privileged \
    -e AWS_REGION=eu-west-1 \
    -e BUCKET_NAME=dev-signal-bucket \
    -e TABLE_NAME=sensor-table-dev \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /home/plense/plensor_data:/home/plense/plensor_data \
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
    -e MQTT_QOS=\"{configuration:/qos}\"
    process-data:latest

docker run \
    --privileged \
    -e AWS_REGION=eu-west-1 \
    -e BUCKET_NAME=dev-signal-bucket \
    -e TABLE_NAME=sensor-table-dev \
    -v /home/plense/metadata:/home/plense/metadata \
    -v /home/plense/plensor_data:/home/plense/plensor_data \
    -v /etc/timezone:/etc/timezone:ro \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/hostname:/etc/container_hostname \
    -v /home/plense/.aws/credentials:/.aws/credentials \
    -e AWS_CONFIG_FILE=/.aws/credentials \
    process-data:latest