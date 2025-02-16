import subprocess
import time

def get_adb_devices():
    """
    Returns a set of connected ADB device IDs.
    """
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        # Only include lines that contain "device" (which may include offline devices)
        devices = {line.split()[0] for line in lines[1:] if "device" in line}
        return devices
    except Exception as e:
        print(f"Error retrieving ADB devices: {e}")
        return set()

def is_emulator_booted(device_id):
    """
    Checks if the emulator is fully booted by polling the sys.boot_completed property.
    Returns True if booted, else False.
    """
    try:
        result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "sys.boot_completed"],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "1"
    except Exception as e:
        print(f"Error checking boot status for device {device_id}: {e}")
        return False

def wait_for_boot(device_id, timeout=300):
    """
    Waits until the emulator is fully booted by polling sys.boot_completed every 5 seconds.
    Returns True if booted within the timeout, else False.
    """
    print(f"Waiting for emulator {device_id} to fully boot...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_emulator_booted(device_id):
            print(f"Emulator {device_id} is fully booted!")
            return True
        time.sleep(5)
    print(f"Timeout waiting for emulator {device_id} to boot.")
    return False

def create_emulator(avd_name: str):
    """
    Starts the specified Android emulator if it's not already running and retrieves its device ID.
    Waits until the emulator is fully booted before returning the device ID.

    :param avd_name: The name of the Android Virtual Device (AVD) to start.
    :return: The emulator device ID if successfully booted, or None if it fails to start.
    """
    print(f"Starting emulator: {avd_name}")

    # Get the list of devices before starting the emulator
    devices_before = get_adb_devices()
    print(f"Devices before starting emulator: {devices_before}")

    # Start the emulator in the background
    command = ["emulator", "-avd", avd_name, "-no-snapshot-save", "-scale", "0.75"]
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for the emulator to appear in adb devices
    print("Waiting for emulator to appear in adb devices...")
    device_id = None
    for _ in range(30):  # Check every 5 seconds for up to 150 seconds
        devices_after = get_adb_devices()
        new_devices = devices_after - devices_before
        if new_devices:
            device_id = new_devices.pop()
            print(f"Emulator detected with device ID: {device_id}")
            break
        time.sleep(5)
    
    if not device_id:
        print("Failed to detect new emulator device.")
        return None

    # Wait until the emulator is fully booted
    if wait_for_boot(device_id):
        print(f"Emulator {device_id} is fully booted and ready to use!")
        return device_id
    else:
        print(f"Emulator {device_id} failed to fully boot within the timeout period.")
        return None
