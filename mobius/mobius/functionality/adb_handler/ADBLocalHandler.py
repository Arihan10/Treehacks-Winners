from mobius.functionality.adb_handler.ADBHandler import ADBHandler
import subprocess
import time

class ADBLocalHandler(ADBHandler):
    """
    Handles ADB operations over a local (USB) connection.
    This handler uses a device_id to run ADB commands.
    """
    def __init__(self, device_id):
        self.device_id = device_id

    def call(self, command: str):
        """
        Runs an ADB command using the specified USB-connected device.
        
        The function expects a command in the form of 'adb x y z', extracts the actual command after 'adb',
        inserts '-s <device_id>' if a device ID is provided, and executes it.
        """
        parts = command.strip().split()
        
        if not parts or parts[0].lower() != "adb":
            return {"output": "Invalid command format. Must start with 'adb'.", "succeeded": False}
        
        cmd = ["adb", "-s", self.device_id] + parts[1:]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        success = result.returncode == 0
        time.sleep(2)
        
        return {"output": result.stdout.strip() if success else result.stderr.strip(), "succeeded": success}