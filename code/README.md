Welcome to the edge code repository. Grab a hot tea and enjoy :)

- The measure-plensor folder contains the code to communicate with a connected Plensor and save the measurements locally in the corresponding folders.
- The process-data folder contains the code that processes the locally stored measurements: it lists the files in a folder, calculates the spectra, uploads all measurement types to the corresponding cloud locations and deletes the local measurements if the upload was successfull.
- The installer_scripts folder contains shell scripts that automate parts of the Raspberry Pi installation and configuration process.
- The log-manager folder contains code that manages the error logging that is done by the different components running on the Pi in a centralized manner.
- The rpi-health folder contains code that reads out the Raspberry Pi health metrics, and logs them to our AWS ecosystem.
- The deployments folder contains json files that contain the deployment information per pilot, per edge computer. These files govern the measurement process.
- The cron folder contains cron files that run on the edge computers, governing automatic, small processes like uploading the logs and rebooting the edge computer at a set time.

By splitting the measure process and the data process, the Raspberry Pi keeps reading out Plensor measurements, also in case internet connection is lost.

The gitignore will ignore everything but Python files, the README.md and the requirements.txt
