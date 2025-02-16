import subprocess
import time
def pair():
    """
    Configures ADB WiFi connection automatically.
    - If a **single device is connected via WiFi**, return its IP.
    - If a **single device is connected via USB**, convert it to WiFi and return its IP.
    - If there are **multiple devices** or **no devices**, print an error.
    """
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]  # Skip header line
    
    devices = [line.split("\t")[0] for line in lines if "device" in line]
    ip_devices = [d for d in devices if ":" in d]  # IP-connected devices
    usb_devices = [d for d in devices if ":" not in d]  # USB devices

    if len(ip_devices) == 1:
        return ip_devices[0]

    if len(ip_devices) > 1:
        print("Error: Multiple WiFi-connected devices found. Cannot auto-select.")
        return None

    if len(usb_devices) == 1:
        return setup_wifi(usb_devices[0])

    print("Error: No connected ADB devices found.")
    return None

def setup_wifi(device_id):
    """Converts a USB-connected ADB device to WiFi mode and returns its IP."""
    print(f"Switching {device_id} to ADB over WiFi...")
    subprocess.run(["adb", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    result = subprocess.run(["adb", "-s", device_id, "devices"], capture_output=True, text=True)
    if device_id not in result.stdout:
        print("Error: Lost USB connection after disconnecting WiFi ADB.")
        return None

    subprocess.run(["adb", "-s", device_id, "tcpip", "5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    result = subprocess.run(["adb", "-s", device_id, "shell", "ip route"], capture_output=True, text=True)
    if not result.stdout:
        print("Error: Failed to retrieve IP route information.")
        return None

    ip_address = None
    for line in result.stdout.strip().split("\n"):
        if "src" in line:
            ip_address = line.split("src")[-1].strip()
            break

    if not ip_address:
        print("Error: Failed to determine device IP address.")
        return None

    connect_result = subprocess.run(["adb", "connect", f"{ip_address}:5555"], capture_output=True, text=True)
    if "connected" not in connect_result.stdout.lower():
        print(f"Error: Failed to connect to {ip_address}:5555")
        return None

    return f'{ip_address}:5555'


def attempt_pair(retries=3):
    """
    Attempts to run `pair()` up to `retries` times if it fails.
    Returns the IP address on success or None after all attempts fail.
    """
    for attempt in range(retries):
        try:
            return pair()
        except:
            pass

    print("All attempts to pair failed.")
    return None  # Return None if all retries fail

import os
import logging

LOG_FILE = "voicify.log"

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

clear_log()

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

ip = attempt_pair()
print(ip)

if ip is None: exit()

from mobius import start_server
url = start_server(full_attach_ip = ip)

while True:
    pass