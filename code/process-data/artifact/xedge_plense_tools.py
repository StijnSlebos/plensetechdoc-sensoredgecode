# xedge_plense_tools.py

import numpy as np
import os, re
import datetime
from typing import Union, List, Tuple

from datetime import datetime
from scipy.signal import savgol_filter, welch, lfilter
from scipy.fft import fft, fftfreq, ifft
from scipy.ndimage import gaussian_filter1d

import soundfile as sf
import warnings

class LocalDataLoader_edge:

    @staticmethod
    def load_audio_file(file, flc_type="float32", expected_sample_rate=500000, expected_segment_length=25000):
        """
        Load an audio file and return its data.
        """
        try:
            audio_data, sample_rate = sf.read(file, dtype=flc_type)
            if sample_rate != expected_sample_rate:
                raise Exception(f"Inconsistent sample rate in file {file}: {sample_rate}")
            if len(audio_data) % expected_segment_length != 0:
                raise Exception(f"Length of array in file {file} is not a multiple of segment length of {expected_segment_length}")
            return audio_data
        except Exception as e:
            print(f"Error loading {file}: {e}")
            return None

    @staticmethod
    def interpret_measurementfile_basename(file: str, basename_version = None) -> dict:
        """
        Interpret the information encapsulated in the filename string
        """
        try:
            file_name = os.path.basename(file)
            file_metadata = re.split(r'[#.]', file_name)
            
            if basename_version is None:      
                if len(file_metadata) == 3:
                    basename_version = 'b2025'
                elif len(file_metadata) == 5:
                    basename_version = 'legacy5'
                else:
                    raise Exception(f"nonvalid measurement-file name, metaelements={file_metadata}")

            file_metadata_dict = {}
            # General File metadata
            file_metadata_dict["meas_id"] = file_metadata[0]
            measurement_specific_metadata = file_metadata[-2].split("_")
            file_metadata_dict["sensor_id"] = '#' + measurement_specific_metadata[0]
            file_metadata_dict["datetime"] = LocalDataLoader_edge.plense_stringtime_to_datetime(measurement_specific_metadata[1])
            file_metadata_dict["filetype"] = file_metadata[-1]

            if basename_version == 'b2025':
                pass
            # Legacy stuff
            if basename_version == 'legacy5':
                file_metadata_dict["sensortype"] = file_metadata[1]
                file_metadata_dict["pilot_id"] = file_metadata[2]
                
            return file_metadata_dict
        except Exception as e:
            print(f"Error in interpreting measurement basename: {e}")

    @staticmethod
    def build_measurementfile_basename(file_meta_dict: dict, basename_version = 'b2025') -> str:
        """
        Reconstruct the filename string from the file metadata dictionary
        """
        file_name = None
        required_keys = [["meas_id","sensor_id", "datetime", "filetype"],["sensortype", "pilot_id"]]
        for key in required_keys[0]:
                if key not in file_meta_dict:
                    raise ValueError(f"Missing required key: {key} for basename type {basename_version}")
        if basename_version is None:
            # Ensure all necessary keys are in the dictionary
            basename_version = 'b2025'
        
        # Convert datetime back to the original string format
        datetime_str = LocalDataLoader_edge.plense_datetime_to_stringtime(file_meta_dict["datetime"])
        # Remove the '#' from sensor_id
        sensor_id_str = file_meta_dict["sensor_id"].lstrip('#')

        if basename_version == 'legacy5':
            for key in required_keys[1]:
                if key not in file_meta_dict:
                    raise ValueError(f"Missing required key: {key} for basename type {basename_version}")
            # Rebuild the filename
            file_name = f"{file_meta_dict['meas_id']}#{file_meta_dict['sensortype']}#{file_meta_dict['pilot_id']}#{sensor_id_str}_{datetime_str}.{file_meta_dict['filetype']}"  
        elif basename_version == 'b2025':
            # Rebuild the filename
            file_name = f"{file_meta_dict['meas_id']}#{sensor_id_str}_{datetime_str}.{file_meta_dict['filetype']}"
        
        return file_name



    @staticmethod
    def plense_stringtime_to_datetime(time_: str):
        date_format = "%Y-%m-%dT%H%M%S"  # Plense Default format
        if isinstance(time_, list):
            return [datetime.strptime(t, date_format) for t in time_]
        else:
            return datetime.strptime(time_, date_format)

    @staticmethod
    def plense_datetime_to_stringtime(time_: datetime):
        date_format = "%Y-%m-%dT%H%M%S"  # Plense Default format
        if isinstance(time_, list):
            return [t.strftime(date_format) for t in time_]
        else:
            return time_.strftime(date_format)
    
    @staticmethod
    def plensor_id_int_to_str(id: Union[int, List[int]]) -> Union[str, List[str]]:
        if isinstance(id, list):
            return [f"#{str(i).zfill(5)}" for i in id]
        else:
            return f"#{str(id).zfill(5)}"

    @staticmethod
    def plensor_id_str_to_int(id: Union[str, List[str]]) -> Union[int, List[int]]:
        if isinstance(id, list):
            return [int(i.lstrip('#')) for i in id]
        else:
            return int(id.lstrip('#'))

class SignalOperator_edge:
    @staticmethod
    def _td_SE(signal: np.ndarray) -> tuple:
        """
        Calculates the mean square (MS) and root mean square (RMS)
        of a given signal. \n
        $$ {MS} = {frac{1}{n} \sum_{i=1}^{n} x_i^2} $$
        $$ {RMS} = \sqrt{frac{1}{n} \sum_{i=1}^{n} x_i^2} $$

        Parameters:
            signal (np.ndarray): Input array representing the signal.

        Returns:
            tuple: (mean_square (np.float64), rms (np.float64))
        """
        MS = np.sum(np.multiply(signal, signal))/len(signal)

        return MS

    @staticmethod
    def _transform_segments_ifft(signal, check_imag=False):
        """
        Give the inverse fft of a signal. 
        TODO include faultsafe checks and data checks
        """
        inverse_fft_signal = ifft(signal)
        if check_imag:
            max_j = np.max(np.abs(np.imag(inverse_fft_signal)))
            if max_j > 1e-9:
                warnings.warn(f"high imaginary component in ifft signal found: [{max_j}], potential leading error")
        return np.real(inverse_fft_signal)

    @staticmethod
    def _transform_segments_fft(signal, segments=10, normalize=False, subtract_mean=True, phase_averaging_mode='first-phase'):
        """
        Perform FFT on signal split into segments and apply optional processing steps.

        Args:
            signal (ndarray): Input signal array to be transformed.
            segments (int, optional): Number of segments to split the signal into. Defaults to 10.
            normalize (bool, optional): Whether to normalize the FFT output. Defaults to False.
            subtract_mean (bool, optional): Whether to subtract the mean from each segment before FFT. Defaults to True.
            phase_averaging_mode (str, optional): Mode for phase averaging. Options: 'default' (legacy) or 'first-phase'. 
                                                Defaults to 'first-phase'.

        Returns:
            tuple: 
                - audio_fft (ndarray): The averaged FFT result (normalized if selected).
                - audio_power (float): Power of the signal (if normalized, else returns 1).
        
        TODO: include try/except statements
        """
        # Split in given segments
        audio_data_segments = np.split(signal, segments)
        # Apply FFT with optional mean subtraction
        audio_fft_segments = [fft((seg - np.mean(seg)) if subtract_mean else seg) for seg in audio_data_segments]
        # average over the transformed segments
        if phase_averaging_mode == 'default':
            audio_fft = np.average(audio_fft_segments, axis=0)
        elif phase_averaging_mode == 'first-phase':
            magnitude_average = np.average([np.abs(fft_segment) for fft_segment in audio_fft_segments], axis=0)
            audio_fft = magnitude_average * np.exp(1j * np.angle(audio_fft_segments[0]))

        if normalize:
            # Calibrate for Power (normalize)
            audio_power = np.sum(np.abs(audio_fft)**2)
            audio_fft_normalized = np.divide(audio_fft, np.sqrt(audio_power))
            return audio_fft_normalized, audio_power
        return audio_fft, 1


class PreprocessingOperator_edge:
    """
    Edge adapted class of preprocessing class to perform preprocessing of retrieved audiodata
    """    
    
    def __init__(self, target_td_dir: str, source_td_dir : str, configuration='PRD') -> None:
        """
        Parameters:
            topdirectory (str): Path to the topdirectory containing the folders: 
                - [DEPLOYMENT] 
                - [PRD] 
                - [RAW_PRD_DB]
            configuration (str): 'PRD' or 'DEV'
        """

        self.target_td_dir = target_td_dir
        self.source_td_dir = source_td_dir

        # self.topdirectory = topdirectory
        # self.configuration = configuration.capitalize()
        # self.deployment_directory = os.path.join(self.topdirectory, 'DEPLOYMENT')
        # self.raw_db_directory = os.path.join(self.topdirectory, f'RAW_{self.configuration}_DB')
        # self.target_directory = os.path.join(self.topdirectory, f'{self.configuration}')
        # with open(os.path.join(self.deployment_directory, 'plense_deployment_config.json'), 'r') as f:
        #     settings = json.load(f)
        # self.processing_settings = settings
        # pass

    def preprocess_pp002(self, audio_data_int16, no_mean=True, segments_to_keep=9, segments=10):
        segment_length = len(audio_data_int16)//segments
        
        # Split audio in base-segments
        audio_segments = [audio_data_int16[i*segment_length: (i+1)*segment_length] for i in range(segments)]

        # Find MS of segments without hammer element 2% on both sides
        audio_meansquare = [np.sum(np.square(seg[(segment_length//50):(segment_length-(segment_length//50))])) for seg in audio_segments]
        # find median-deviation
        audio_mediandeviation = [abs(np.median(audio_meansquare)-audio_ms) for audio_ms in audio_meansquare]
        # Sort segments by increasing median deviation
        sorted_audio_segments = [seg for _, seg in sorted(zip(audio_mediandeviation, audio_segments), key=lambda x: x[0])]
        
        # Make one new audiofile up until the droprate
        audio_data_sx_int16 = np.concatenate(sorted_audio_segments[:segments_to_keep])

        # Parse first x segments into the fft/segment/operator
        audio_data_sx_fft_f64, _ = SignalOperator_edge._transform_segments_fft(audio_data_sx_int16, normalize=False, subtract_mean=no_mean, segments=segments_to_keep, phase_averaging_mode='first-phase')

        # Forcefit fft into 32bit/ complex64bit
        audio_data_sx_fft_f32 = np.complex64(audio_data_sx_fft_f64)

        # Inverse averaged segment back
        audio_data_sx_processed_int32 = SignalOperator_edge._transform_segments_ifft(audio_data_sx_fft_f32)

        # parse back to float32 and scale back to -1 to 1 range.
        audio_data_sx_processed_f32 = audio_data_sx_processed_int32.astype(np.float32) / 32767.0

        # Return processed audiodata
        return audio_data_sx_processed_f32