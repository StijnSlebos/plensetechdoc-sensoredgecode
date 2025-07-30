import subprocess
import threading

def run_log_temperature():
    subprocess.run(["python", "log_health_metrics.py"])

def run_process_temperatures():
    subprocess.run(["python", "process_health_metrics.py"])

if __name__ == "__main__":
    # Create threads for each script
    log_thread = threading.Thread(target=run_log_temperature)
    process_thread = threading.Thread(target=run_process_temperatures)

    # Start both threads
    log_thread.start()
    process_thread.start()

    # Wait for both threads to finish
    log_thread.join()
    process_thread.join()
