import subprocess

import os
import logging

LOG_FILE = "app_simple_intent_physical_device.log"

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

clear_log()

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

def get_adb_device():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = [line.split("\t")[0] for line in result.stdout.strip().split("\n")[1:] if "device" in line]
    if len(devices) != 1:
        return None, None
    device_id = devices[0]
    connection_type = "wifi" if ":" in device_id else "local"
    return device_id, connection_type

device, id = get_adb_device()

if device is None:
    print("won't work")
    exit()

print(device)

from mobius import create_controller

Mobius = create_controller()

# Mobius.do(device, "Add my friend's contact to my contacts list")
Mobius.do(device, "Add my friend Arihan Sharma's number of 647 513 1305 to my contacts list")


