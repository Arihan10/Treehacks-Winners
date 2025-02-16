import subprocess
import time

def get_adb_devices():
    """
    Returns a set of connected ADB device IDs.
    """
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        devices = {line.split()[0] for line in lines[1:] if "device" in line}
        return devices
    except Exception as e:
        print(f"Error retrieving ADB devices: {e}")
        return set()

def create_emulator(avd_name: str):

    """
    Starts the specified Android emulator if it's not already running and retrieves its device ID.

    :param avd_name: The name of the Android Virtual Device (AVD) to start.
    :return: The emulator device ID, or None if it fails to start.
    """
    print(f"Starting emulator: {avd_name}")

    # Get the list of devices before starting the emulator
    devices_before = get_adb_devices()
    print(f"Devices before starting emulator: {devices_before}")

    # Start the emulator in the background
    command = ["emulator", "-avd", avd_name, "-no-snapshot-save", "-scale", "0.75"]
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Wait for emulator to boot and detect the new device
    print("Waiting for emulator to boot...")
    for _ in range(30):  # Check for 30 * 5 = 150 seconds
        devices_after = get_adb_devices()
        new_devices = devices_after - devices_before

        if new_devices:
            device_id = new_devices.pop()
            print(f"Emulator booted successfully with device ID: {device_id}")
            return device_id
        
        time.sleep(5)

    print("Failed to detect new emulator device.")
    return None
