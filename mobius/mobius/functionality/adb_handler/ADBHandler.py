import os
import subprocess
import tempfile

class ADBHandler:
    """
    Base class for ADB operations.
    Provides common functions like ping, UI hierarchy dump, and screenshot.
    Child classes must implement their own call() method.
    """

    def call(self, args, **kwargs):
        raise NotImplementedError("Subclasses must implement the call method.")

    def ping(self):
        """Checks if the device is connected by echoing 'ping'."""
        return self.call(["shell", "echo", "ping"])

    def get_xml(self):
        """
        Dumps the current UI hierarchy to an XML file and retrieves its contents.
        """
        dump_res = self.call(["shell", "uiautomator", "dump", "/sdcard/ui.xml"])
        if not dump_res["succeeded"]:
            return dump_res
        
        pull_res = self.call(["pull", "/sdcard/ui.xml", "ui.xml"])
        if not pull_res["succeeded"]:
            return pull_res
        
        try:
            with open("ui.xml", "r", encoding="utf-8") as f:
                xml_content = f.read()
            return {"output": xml_content, "succeeded": True}
        except Exception as e:
            return {"output": str(e), "succeeded": False}

    def get_screenshot(self):
        """
        Captures a screenshot on the device, pulls it to a temporary file on the host machine, 
        and returns the local file path.
        """
        temp_dir = tempfile.gettempdir()
        local_screenshot_path = os.path.join(temp_dir, "screenshot.png")
        device_screenshot_path = "/sdcard/screenshot.png"

        # Step 1: Capture screenshot on the device
        screenshot_res = self.call(["shell", "screencap", "-p", device_screenshot_path])
        if not screenshot_res["succeeded"]:
            return {"output": "Failed to capture screenshot", "succeeded": False}

        # Step 2: Pull screenshot from device to host
        pull_res = self.call(["pull", device_screenshot_path, local_screenshot_path])
        if not pull_res["succeeded"]:
            return {"output": "Failed to pull screenshot", "succeeded": False}

        return {"output": local_screenshot_path, "succeeded": True}
