from mobius.functionality.adb_handler.ADBHandler import ADBHandler
import subprocess
import time

class ADBWifiHandler(ADBHandler):
    def __init__(self):
        self.ip = None

    def call(self, command: str):
        """
        Runs an ADB command given as a string and returns output + success status.
        
        The function expects a command in the form of 'adb x y z', extracts the actual command after 'adb',
        inserts '-s <ip>:5555' if an IP is provided, and executes it.
        """
        parts = command.strip().split()
        
        if not parts or parts[0].lower() != "adb":
            return {"output": "Invalid command format. Must start with 'adb'.", "succeeded": False}
        
        cmd = ["adb", "-s", f"{self.ip}:5555"] + parts[1:] 
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        success = result.returncode == 0
        time.sleep(2)
        
        return {"output": result.stdout.strip() if success else result.stderr.strip(), "succeeded": success}
