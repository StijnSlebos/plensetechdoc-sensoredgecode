import matplotlib.pyplot as plt
import numpy as np
import json
import os
import soundfile as sf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Local_Storage_Path = "/home/plense/plensor_data/audio_data/time_domain_not_processed"


def plot_audio_files(latest_n: int = 3):
    local_storage_path = Local_Storage_Path
    # microphone_names = ["Udev0", "Udev1"]

    # for rpi_node in config["rpi_nodes"]:
    #     rpi_node_name = rpi_node["name"]
    #     rpi_node_path = os.path.join(local_storage_path, rpi_node_name)
        
    plot_path = os.path.join(local_storage_path, "plots")
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    files: list[str] = []  # 1 node, 2 channels/microphones
    # for mic in microphone_names:
    m_files = [f for f in os.listdir(local_storage_path) if f.endswith(f".flac")]
    files = m_files[-latest_n:]

    # plot the files
    # for mic_idx, mic in enumerate(microphone_names):
    for file in files:
        plotname = file.split(".")[0]+f"_plot"
        plot_file_path = os.path.join(plot_path, f"{plotname}.png")
        if not os.path.exists(plot_file_path):
            file_path = os.path.join(local_storage_path, file)
            logger.info(f"Plotting {file_path} to {plot_file_path}")
            plot_file(file_path, plot_file_path, plotname=plotname)


def plot_file(file_path: str, plot_file_path: str, plotname: str | None = None):
    data, samplerate = sf.read(file_path)
    time = np.arange(len(data)) / samplerate
    plt.plot(time, data)
    if plotname:
        plt.title(plotname)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.savefig(plot_file_path)
    plt.close()
    logger.info(f"Saved plot to {plot_file_path}")


if __name__ == "__main__":
    # config = json.load(open(CONFIG_PATH))
    plot_audio_files()
