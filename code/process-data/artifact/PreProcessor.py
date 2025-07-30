import os
import soundfile as sf
import numpy as np
from xedge_plense_tools import SignalOperator_edge as SignalOperator


class Preprocessor:
    def __init__(self):
        """
        Initializes the Preprocessor class with hardcoded directories.
        """
        self.preprocessed_data_dir = '/home/plense/plensor_data/audio_data/time_domain_processed'

    def process_measurement_file(self, measurementfile):
        """
        Processes a single measurement file: performs segmentation, FFT, and IFFT,
        saves the processed file, and returns the maximum amplitude.

        Args:
            measurementfile (str): Path to the measurement file.

        Returns:
            float: Maximum amplitude of the processed signal, or None if the processing failed.
        """
        # Create the new filename for processed data
        new_filename = self.add_24_before_hash(os.path.basename(measurementfile))
        processed_file_path = os.path.join(self.preprocessed_data_dir, new_filename)

        # Check if the file has already been processed
        if not os.path.exists(processed_file_path):
            os.makedirs(self.preprocessed_data_dir, exist_ok=True)

            try:
                # Load the raw audio data
                audio_data_int16, sample_rate = sf.read(measurementfile, dtype="int16")
                if sample_rate != 500000:
                    print(f"Inconsistent sample rate in file {measurementfile}")
                    return None
            except Exception as e:
                print(f"Error loading {measurementfile}: {e}")
                return None

            # Perform FFT and IFFT transformation
            try:
                audio_data_processed = self.segment_and_transform(audio_data_int16, sample_rate)
            except Exception as e:
                print(f"Error in signal transformation for {measurementfile}: {e}")
                return None

            # Save the processed file
            try:
                self.save_processed_file(processed_file_path, audio_data_processed)
            except Exception as e:
                print(f"Error saving processed file {measurementfile}: {e}")
                return None

            # Remove the raw file
            os.remove(measurementfile)

            # Calculate and return the maximum amplitude
            max_amp = np.max(audio_data_processed)
            return max_amp, processed_file_path # TODO ADD OUTLIER SEGMENTS USED AND STD OVER USED SEGMENTS
        else:
            # File has already been processed
            print(f"File {new_filename} already processed, skipping.")
            return None

    def add_24_before_hash(self, filename):
        """
        Adds '24' before the first occurrence of '#' in the filename.

        Args:
            filename (str): The original filename.

        Returns:
            str: The modified filename with '24' added before the first '#'.
        """
        # Find the index of the first '#'
        index = filename.find('#')

        # If '#' is found, insert '24' before it
        if index != -1:
            return filename[:index] + '24' + filename[index:]
        else:
            return filename


    def segment_and_transform(self, audio_data, sample_rate):
        """
        Segments the audio data, performs FFT, and applies inverse FFT.

        Args:
            audio_data (np.array): The raw audio data to process.

        Returns:
            np.array: The processed audio data.
        """
        # Perform FFT on segmented audio data
        audio_data_fft_f64n, std_fft, num_used_segments, _ = SignalOperator._transform_segments_fft(audio_data)

        # Convert to float32 for processing
        audio_data_fft_f32n = np.complex64(audio_data_fft_f64n)

        # Apply inverse FFT and scale to [-1, 1] in float32
        audio_data_processed = (SignalOperator._transform_segments_ifft(audio_data_fft_f32n)).astype(np.float32) / 32767.0

        return audio_data_processed, std_fft, num_used_segments

    def save_processed_file(self, filepath, processed_data):
        """
        Saves the processed audio data as a 24-bit signal.

        Args:
            filepath (str): The path to save the processed file.
            processed_data (np.array): The processed audio data.
        """
        sf.write(filepath, processed_data, samplerate=500000, subtype='PCM_24')
        print(f"Processed file saved: {filepath}")
