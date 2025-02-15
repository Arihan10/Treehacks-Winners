from .ADBHandler import ADBHandler
import subprocess

class ADBLocalHandler(ADBHandler):
    """
    Handles ADB operations over a local (USB) connection.
    This handler uses a device_id to run ADB commands.
    """
    def __init__(self, device_id=None):
        self.device_id = device_id

    # def call(self, args):
    #     """
    #     Runs an ADB command using the specified USB-connected device.
    #     """
    #     cmd = ["adb"]
    #     if self.device_id:
    #         cmd += ["-s", self.device_id]
    #     cmd += args
        
    #     result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    #     success = result.returncode == 0
    #     return {
    #         "output": result.stdout.strip() if success else result.stderr.strip(),
    #         "succeeded": success
    #     }
    
    # def setup(self, device_id=None):
    #     """
    #     Configures the local (USB) ADB connection.
        
    #     - If a device_id is provided, it will use that device.
    #     - Otherwise, it lists devices (filtering out those with ':' in their ID)
    #       and if exactly one USB-connected device is found, that device will be used.
    #     """
    #     if device_id:
    #         self.device_id = device_id
    #         # Verify the device is present
    #         result = subprocess.run(["adb", "devices"], capture_output=True, text=True, shell=True)
    #         if self.device_id in result.stdout:
    #             return {"output": f"Using specified device: {self.device_id}", "succeeded": True}
    #         else:
    #             return {"output": f"Device {self.device_id} not found.", "succeeded": False}
        
    #     # List connected devices and filter for USB (non-WiFi) devices
    #     result = subprocess.run(["adb", "devices"], capture_output=True, text=True, shell=True)
    #     lines = result.stdout.strip().split("\n")
    #     usb_devices = [
    #         line.split("\t")[0]
    #         for line in lines[1:]
    #         if "device" in line and ":" not in line.split("\t")[0]
    #     ]
        
    #     if len(usb_devices) == 1:
    #         self.device_id = usb_devices[0]
    #         return {"output": f"Using USB device: {self.device_id}", "succeeded": True}
    #     elif len(usb_devices) > 1:
    #         return {"output": "Multiple USB-connected devices found. Please specify a device_id.", "succeeded": False}
    #     else:
    #         return {"output": "No USB-connected devices found.", "succeeded": False}
    
    # def convert_to_wifi(self):
    #     """
    #     Converts a USB ADB connection into a WiFi connection.
        
    #     Steps:
    #       1. Disconnect any existing WiFi connections.
    #       2. Ensure the USB connection is still alive.
    #       3. Enable ADB over TCP/IP on port 5555.
    #       4. Retrieve the device’s IP address.
    #       5. Connect to the device over WiFi.
        
    #     Returns:
    #       On success, a dictionary with 'succeeded': True, a message, and a new
    #       ADBWifiHandler instance under the key 'wifi_handler'.
    #     """
    #     if not self.device_id:
    #         return {"output": "No USB-connected device found", "succeeded": False}
        
    #     # Disconnect all WiFi ADB connections
    #     subprocess.run(["adb", "disconnect"], shell=True)
        
    #     # Verify that the USB connection is still active
    #     result = subprocess.run(["adb", "-s", self.device_id, "devices"],
    #                             capture_output=True, text=True, shell=True)
    #     if self.device_id not in result.stdout:
    #         return {"output": "Lost USB connection after disconnecting WiFi ADB", "succeeded": False}
        
    #     # Enable ADB over TCP/IP
    #     self.call(["tcpip", "5555"])
        
    #     # Retrieve the device's IP address
    #     result = self.call(["shell", "ip route"])
    #     if not result["succeeded"]:
    #         return result
        
    #     ip = None
    #     for line in result["output"].splitlines():
    #         if "src" in line:
    #             ip = line.split("src")[-1].strip()
    #             break
        
    #     if not ip:
    #         return {"output": "Failed to determine IP", "succeeded": False}
        
    #     # Connect to the device over WiFi (note: use the raw adb connect command)
    #     connect_result = subprocess.run(["adb", "connect", f"{ip}:5555"],
    #                                     capture_output=True, text=True, shell=True)
    #     if connect_result.returncode != 0:
    #         return {"output": connect_result.stderr.strip(), "succeeded": False}
        
    #     # Create a new ADBWifiHandler with the detected IP and return it
    #     wifi_handler = ADBWifiHandler(ip=ip)
    #     return {
    #         "output": f"Converted to WiFi mode with IP: {ip}",
    #         "succeeded": True,
    #         "wifi_handler": wifi_handler
    #     }
