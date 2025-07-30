import json
from ErrorLogger import ErrorLogger


class JSONHandler:
    """
    JSONHandler provides utilities for loading configuration data from JSON
    files and safely parsing JSON strings, with error logging for issues
    encountered in these processes.

    Attributes:
        logger (ErrorLogger): An instance of ErrorLogger for logging errors.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Initializes JSONHandler with an ErrorLogger instance.
        """
        if self._instance is not None:
            raise Exception("JSONHandler is a singelton!")
        self.logger = ErrorLogger.get_instance()

    def load_config(self, path='/home/plense/metadata/settings.json'):
        """
        Loads configuration data from the specified JSON file, logging any
        errors encountered.

        Parameters:
            path (str): Path to the JSON configuration file.

        Returns:
            dict: The configuration data loaded from the file, or an empty dict
            if loading fails.
        """
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.log_error(f"Configuration file not found: {path}")
        except json.JSONDecodeError:
            self.logger.log_error("Error decoding JSON from the configuration "
                                  f"file: {path}")
        except Exception as e:
            self.logger.log_error("Unexpected error loading configuration:"
                                  f" {e}")
        return {}

    def safe_json_loads(self, json_string):
        """
        Safely parses a JSON string, logging any errors encountered and
        returning an empty dictionary as a fallback in case of parsing failure.

        Parameters:
            json_string (str): The JSON string to parse.

        Returns:
            dict: The parsed JSON data as a dictionary, or an empty dict if
            parsing fails.
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            self.logger.log_error("Error decoding JSON string.")
        except Exception as e:
            self.logger.log_error(f"Unexpected error parsing JSON string: {e}")
        return {}

    def safe_json_load(self, file_path):
        """
        Safely loads JSON data from the specified filepath, logging any errors
        encountered and returning an empty dictionary as a fallback in
        case of loading failure.

        Parameters:
            file_path (str): The filepath of the JSON file to load.

        Returns:
            dict: the JSON dict, or an empty dict if the loading fails.
        """
        try:
            with open(file_path, 'r') as file:
                JSON_data = json.load(file)
            return JSON_data
        except json.JSONDecodeError as e:
            self.logger.log_error(
                f"Error decoding JSON from file {file_path}: {e}")
        except IOError as e:
            self.logger.log_error(f"Error reading file {file_path}: {e}")
        except Exception as e:
            self.logger.log_error(f"Unexpected error loading JSON file: {e}")
        return {}

    def save_to_json(self, data, file_path, indent=4):
        """
        Saves the provided data to a JSON file specified by file_path.

        Parameters:
            data (dict or list): The data to be saved into the JSON file.
            file_path (str): The path to the file where the data should be
                saved.
            indent (int): The indentation level to use for formatting the
                saved JSON data.
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=indent)
        except TypeError as e:
            self.logger.log_error(f"TypeError in saving JSON data: {e}")
        except OSError as e:
            self.logger.log_error("IOError in saving to file {file_path}: "
                                  f"{e}")
        except Exception as e:
            self.logger.log_error("Unexpected error saving to JSON file "
                                  f"{file_path}: {e}")

    def safe_json_dumps(self, data):
        """
        Safely dumps data to a JSON string, logging any errors encountered and
        returning an empty dictionary as a fallback in case of parsing failure.

        Parameters:
            data (array): The data to dump into a JSON string.

        Returns:
            json_string: The JSON string.
        """
        try:
            return json.dumps(data)
        except Exception as e:
            self.logger.log_error(f"Unexpected error parsing JSON string: {e}")
        return {}