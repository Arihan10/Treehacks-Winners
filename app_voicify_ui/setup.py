import subprocess

def setup(self, ip=None):
    """
    Configures ADB WiFi connection based on available devices.
    If an IP address is provided, it will attempt to connect to that IP.
    Otherwise, it checks for available ADB devices and decides the next steps.
    """
    if ip:
        self.ip = ip
        return self.call(["connect", f"{self.ip}:5555"], use_ip=False)
    
    # Get list of connected devices
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, shell=True)
    lines = result.stdout.strip().split("\n")
    devices = [line.split("\t")[0] for line in lines[1:] if "device" in line]
    
    ip_devices = [d for d in devices if ":" in d]  # Filter IP-connected devices
    usb_devices = [d for d in devices if ":" not in d]  # Filter USB devices
    
    if len(ip_devices) == 1:
        self.ip = ip_devices[0]
        return {"output": f"Using WiFi device: {self.ip}", "succeeded": True}
    elif len(ip_devices) > 1:
        return {"output": "Multiple WiFi-connected devices found. Please specify an IP.", "succeeded": False}
    elif len(usb_devices) == 1:
        self.device_id = usb_devices[0]
        return self.setup_wifi()
    else:
        return {"output": "No connected devices found.", "succeeded": False}
    
def setup_wifi(self):
    """
    Converts a USB ADB connection into a WiFi connection.
    """
    if not self.device_id:
        return {"output": "No USB-connected device found", "succeeded": False}
    
    # Remove all WiFi ADB connections
    subprocess.run(["adb", "disconnect"], shell=True)
    
    # Ensure ADB is still connected via USB
    result = subprocess.run(["adb", "-s", self.device_id, "devices"], capture_output=True, text=True, shell=True)
    if self.device_id not in result.stdout:
        return {"output": "Lost USB connection after disconnecting WiFi ADB", "succeeded": False}
    
    # Enable ADB over TCP
    self.call(["tcpip", "5555"], use_ip=False)

    # Get device IP
    result = self.call(["shell", "ip route"], use_ip=False)
    if not result["succeeded"]:
        return result
    
    # Extract IP from output
    lines = result["output"].strip().split("\n")
    for line in lines:
        if "src" in line:
            self.ip = line.split("src")[-1].strip()
            break
    if not self.ip:
        return {"output": "Failed to determine IP", "succeeded": False}
    
    # Connect to the device over WiFi
    return self.call(["connect", f"{self.ip}:5555"], use_ip=False)
