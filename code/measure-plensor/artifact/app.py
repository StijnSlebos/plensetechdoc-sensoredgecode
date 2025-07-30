import json
import os
import platform
import pytz
import queue
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from error_logger import ErrorLogger
from json_handler import JSONHandler
from message_handler import MessageHandler
from queue_manager import QueueManager
from sensor import Sensor
from serial_communication_setup import SerialCommunicationSetup
from threading import Event


scs = SerialCommunicationSetup()


class MeasureProcessManager():
    """
    MeasureSetup handles the Plensor measurement process. Uses singleton pattern.

    Attributes:
        json_handler (JSONHandler): Instance of JSONHandler for loading JSON data.
        logger (ErrorLogger): Instance of ErrorLogger for logging errors.
        metadata_directory (str): Directory path where the sensor metadata files are stored.
    """

    _instance = None  # Class-level attribute for the singleton instance

    @classmethod
    def get_instance(cls, metadata_directory=None):
        """
        Provides a single instance of DampingExtractor.

        Parameters:
            metadata_directory (str): Directory path where the sensor metadata files are stored.

        Returns:
            DampingExtractor: The singleton instance of the class.
        """
        if metadata_directory is None:
            if platform.system() == "Windows":
                metadata_directory = os.path.abspath(os.path.join(os.getcwd(), '..', 'deployments'))
            else:
                metadata_directory = '/home/plense/metadata'

        if cls._instance is None:
            cls._instance = cls(metadata_directory)
        return cls._instance

    def __init__(
            self,
            measurement_dir='/home/plense/plensor_data',
            metadata_directory=None):
        """
        Initializes the MeasureSetup with instances of <CLASSES>.
        """
        if self._instance is not None:
            raise Exception(
                "DampingExtractor is a singleton! Use get_instance()"
                "to retrieve the instance.")

        # Initialize singleton classes
        self.json_handler = JSONHandler.get_instance()
        self.logger = ErrorLogger.get_instance(
            directory='/home/plense/error_logs',
            log_level=20)
        self.logger.log_error("Measure Plensor app has started.")
        # Load app settings from JSON file
        self.load_app_settings()

        # Initialize directories
        if metadata_directory is None:
            if platform.system() == "Windows":
                metadata_directory = os.path.abspath(os.path.join(os.getcwd(), 'deployments'))
            else:
                metadata_directory = '/home/plense/metadata'
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Amsterdam'))
        self.scheduler.start()
        self.last_cycle_completion_time = None
        self.metadata_directory = metadata_directory
        self.measurement_dir = measurement_dir
        self.audio_dir = os.path.join(
            measurement_dir,
            'audio_data',
            'time_domain_not_processed'
        )

        # Get connected sensors and initialize Sensor object classes
        self.unresponsive_sensors = []
        self.connected_sensors = self.get_connected_sensors()
        self.sensors = [
            Sensor(
                sensor["sensor_id"],
                self.logger)
            for sensor in self.connected_sensors]

        # Initialize measurement queue
        self.measurement_queue = queue.Queue()
        self.qm = QueueManager(self.logger, self.sensors, self.measurement_queue, self)
        self.qm.initialize_get_byte_queue()
        self.qm.initialize_calibrate_queue()
        self.qm.initialize_measurement_queue()

        scs.setup_gpio()

        self.mh = MessageHandler(self.logger, self.json_handler, self.sensors, self.measurement_queue, self.measurement_dir, self)

    def load_app_settings(self):
        """
        Loads application settings from app_settings.json and sets class attributes.
        """
        try:
            app_settings_path = '/home/plense/metadata/app_settings.json'
            settings = self.json_handler.safe_json_load(app_settings_path)
            if settings:
                self.log_level = settings.get("log_level", "INFO")
                self.measurement_interval = settings.get("measurement_interval", 300)
                self.logger.log_error(f"Loaded app settings: log_level={self.log_level}, measurement_interval={self.measurement_interval}")
            else:
                self.log_level = "INFO"
                self.measurement_interval = 300
                self.logger.log_warning("Failed to load app settings, using default values.")
        except Exception as e:
            self.logger.log_error(f"Error loading app settings: {e}, setting default settings")
            self.log_level = "INFO"
            self.measurement_interval = 300
    
    def get_connected_sensors(self) -> list:
        """
        Reads the metadata file and extracts connected sensor IDs along with their damping levels.

        Parameters:
            metadata_file_path (str): Path to the metadata JSON file.

        Returns:
            list: A list of dictionaries, each containing 'sensor_id'
            and 'damping_level'.
        """
        try:
            metadata_files = os.listdir(self.metadata_directory)
            for file in metadata_files:
                if file.startswith("metadata_") and file.endswith(".json"):
                    metadata_path = os.path.join(self.metadata_directory, file)
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                sensors = []
                for version, version_data in data.get("sensor_versions", {}).items():
                    default_damping_level = version_data.get(
                        "default_damping_level", 0)
                    for sensor in version_data.get("sensors", []):
                        sensor_id = sensor.get("sensor_id")
                        damping_level = sensor.get(
                            "damping_level", default_damping_level)
                        sensors.append(
                            {"sensor_id": sensor_id,
                             "damping_level": damping_level})
                return sensors
        except Exception as e:
            self.logger.log_error(f"Error while getting connected sensors from metadata: {e}")
            return []

    def handle_interrupt(self):
        """
        Checks for the presence of 'message_interrupt.json' in the metadata folder,
        processes its contents, and adds the messages to the front of the queue.
        """
        try:
            interrupt_file_path = os.path.join(self.metadata_directory, 'message_interrupt.json')
            if os.path.exists(interrupt_file_path):
                # Read and parse the interrupt messages
                with open(interrupt_file_path, 'r') as file:
                    interrupt_data = json.load(file)

                # Process each interrupt message
                for interrupt_message in interrupt_data:
                    self.measurement_queue.queue.appendleft(interrupt_message)
                    self.logger.log_error(f"Interrupt messages: {interrupt_message}")

                # Log the successful interrupt handling
                self.logger.log_error(f"Interrupt messages added to queue from {interrupt_file_path}")

                # Optionally, delete the interrupt file to prevent re-processing
                os.remove(interrupt_file_path)

        except Exception as e:
            self.logger.log_error(f"Error handling interrupt: {e}")

    def handle_metadata_update(self):
        """
        Updates the sensor objects if the update metadata flag
        has been detected.
        """
        try:
            new_connected_sensors = self.get_connected_sensors()
            self.logger.log_error(f"New connected sensors: {new_connected_sensors}")

            # Find disconnected sensors
            disconnected_sensors = [sensor for sensor in self.connected_sensors if sensor not in new_connected_sensors]
            for sensor in disconnected_sensors:
                self.sensors = [s for s in self.sensors if s.sensor_id != sensor["sensor_id"]]
                self.logger.log_error(f"Sensor {sensor['sensor_id']} disconnected.")

            # Find newly connected sensors
            new_sensors = [sensor for sensor in new_connected_sensors if sensor not in self.connected_sensors]
            for sensor in new_sensors:
                new_sensor_obj = Sensor(sensor["sensor_id"], self.logger)
                self.sensors.append(new_sensor_obj)
                self.logger.log_error(f"Sensor {sensor['sensor_id']} connected.")

                # Add get_byte, calibrate, and measurement messages to the front of the queue
                get_byte_msg = new_sensor_obj.create_message(message_type='get_byte')
                calibrate_msg = new_sensor_obj.create_message(message_type='calibrate', measure_after=True)
                self.measurement_queue.queue.appendleft(calibrate_msg)
                self.measurement_queue.queue.appendleft(get_byte_msg)

            # Update connected sensors
            self.connected_sensors = new_connected_sensors
            os.remove(os.path.join(self.metadata_directory, "new_metadata_flag.txt"))
        except Exception as e:
            self.logger.log_error(f"Error from metadata update: {e}")

    def handle_measure_settings_update(self):
        """
        Event handler that triggers when a file is modified in the watched directory.
        """
        try:
            self.logger.log_error(f"Updating measurements settings.")
            with self.measurement_queue.mutex:
                self.measurement_queue.queue.clear()

            # Reinitialize the measurement queue with updated settings
            self.qm.initialize_measurement_queue()
            # Log the successful interrupt handling
            self.logger.log_error(f"New measure settings detected.")

            # Optionally, delete the interrupt file to prevent re-processing
            os.remove(os.path.join(self.metadata_directory, "new_measure_settings_flag.txt"))
            # Start processing the measurement queue again
            # self.process_measurement_queue()

        except Exception as e:
            self.logger.log_error(f"Error handling interrupt: {e}")

    def schedule_next_cycle(self):
        """
        Schedule the next cycle of measurement processing.
        """
        try:
            current_time = time.time()
            if self.last_cycle_completion_time is None:
                # If it's the first cycle, just schedule immediately
                wait_time = 0
            else:
                elapsed_time = self.last_cycle_completion_time - self.last_cycle_start_time
                wait_time = max(0, self.measurement_interval - elapsed_time)
            run_date = datetime.now() + timedelta(seconds=wait_time)
            self.scheduler.add_job(self.process_measurement_queue, 'date', run_date=run_date)
            self.logger.log_error(f"Scheduled next measurement cycle using APScheduler, wait: {wait_time}, run date: {run_date}.")
        except Exception as e:
            self.logger.log_error(f"Error in scheduling next cycle, scheduling right now: {e}")
            self.process_measurement_queue()

    def process_measurement_queue(self) -> None:
        """
        Processes the measurement queue and invokes the appropriate
        function based on the message type.
        Periodically checks for interrupt messages.
        """
        try:
            self.load_app_settings()
            self.last_cycle_start_time = time.time()
            self.logger.log_error(f"Start new iteration processing measurement queue...")
            # Check for user interrupt to the message queue before processing the next message
            metadata_files = os.listdir(self.metadata_directory)
            print(f"Metadata files: {metadata_files}")
            if 'message_interrupt.json' in metadata_files:
                self.handle_interrupt()
            elif 'new_measure_settings_flag.txt' in metadata_files:
                self.handle_measure_settings_update()
            elif 'new_metadata_flag.txt' in metadata_files:
                self.handle_metadata_update()

            while not self.measurement_queue.empty():
                print(f"Measurement queue is not empty: {len(self.measurement_queue.queue)}")

                if 'message_interrupt.json' in metadata_files:
                    self.handle_interrupt()

                # After checking for user interrupt queue alteration,
                # move on to the message handling
                message = self.measurement_queue.get()
                message_type = message["measurement_settings"].get("type")
                sensor_id = message["sensor_id"]

                if message_type == "get_byte":
                    self.mh.handle_get_byte_msg(sensor_id, message)
                elif message_type == "reset":
                    self.mh.handle_reset_msg(sensor_id, message)
                elif message_type == "calibrate":
                    self.mh.handle_calibrate_msg(sensor_id, message)
                elif message_type == "measure":
                    self.mh.handle_measure_msg(sensor_id, message)
                else:
                    self.logger.log_error(f"Unknown message type: {message_type}")
            else:
                print("Measurement queue is emptied, initializing again")
                self.qm.initialize_measurement_queue()
                self.load_app_settings()
                self.last_cycle_completion_time = time.time()
                self.schedule_next_cycle()
                self.logger.log_error(f"Measurement queue is empty. Waiting for new messages.")
                time.sleep(1)
        except Exception as e:
            self.logger.log_error(f"Error in process measurement queue: {e}")
            self.qm.initialize_measurement_queue()
            self.load_app_settings()
            self.last_cycle_completion_time = time.time()
            self.schedule_next_cycle()
            self.logger.log_error(f"Measurement queue is empty. Waiting for new messages.")
            time.sleep(1)

    def start(self):
        """
        Start the measurement loop using APScheduler.
        """
        midnight_trigger = CronTrigger(hour=0, minute=0, timezone=pytz.timezone('Europe/Amsterdam'))
        self.scheduler.add_job(self.midnight_initialize_queue, midnight_trigger)

    def mark_sensor_unresponsive(self, sensor_id):
        """
        Marks a sensor as unresponsive and prevents it from being included in future measurement cycles.

        Parameters:
            sensor_id (int): ID of the sensor to mark as unresponsive.
        """
        try:
            if sensor_id not in self.unresponsive_sensors:
                self.unresponsive_sensors.append(sensor_id)
                self.logger.log_warning(f"Sensor {sensor_id} marked as unresponsive. It will be excluded from future measurements.")
        except Exception as e:
            self.logger.log_error(f"[{sensor_id}]: Error while marking unresponsive: {e}")

    def mark_sensor_responsive(self, sensor_id):
        """
        Marks a sensor as responsive and prevents it from being included in future measurement cycles.

        Parameters:
            sensor_id (int): ID of the sensor to mark as unresponsive.
        """
        try:
            if sensor_id in self.unresponsive_sensors:
                self.unresponsive_sensors.remove(sensor_id)
                self.logger.log_error(f"Sensor {sensor_id} marked as responsive.")
        except Exception as e:
            self.logger.log_error(f"[{sensor_id}]: Error while marking responsive: {e}")

    def get_responsive_sensors(self) -> list:
        """
        Returns a list of sensors that are not marked as unresponsive.

        Returns:
            list: A list of responsive sensor objects.
        """
        return [sensor for sensor in self.sensors if sensor.sensor_id not in self.unresponsive_sensors]

    def midnight_initialize_queue(self):
        with self.measurement_queue.mutex:
            self.measurement_queue.queue.clear()

        self.qm.initialize_get_byte_queue()
        self.qm.initialize_calibrate_queue()
        self.logger.log_error(f"Midnight get byte and calibration loop initialized.")


if __name__ == "__main__":
    mpm = MeasureProcessManager()
    # Run the process measurement queue function directly once
    mpm.process_measurement_queue()
    # And then start the scheduler
    mpm.start()

    # To keep the script running
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scs.close_gpio()
        mpm.scheduler.shutdown()
