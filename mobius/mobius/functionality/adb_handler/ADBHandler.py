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
        Dumps the current UI hierarchy to an XML file, pulls it to a temporary file on the host machine,
        and returns the local file path.
        """
        temp_dir = tempfile.gettempdir()
        local_xml_path = os.path.join(temp_dir, "ui.xml")
        device_xml_path = "/sdcard/ui.xml"

        # Step 1: Dump UI hierarchy on the device
        dump_res = self.call("adb shell uiautomator dump /sdcard/ui.xml")
        if not dump_res["succeeded"]:
            return {"output": "Failed to dump UI hierarchy", "succeeded": False}

        # Step 2: Pull UI XML file from device to host
        pull_res = self.call(f"adb pull {device_xml_path} {local_xml_path}")
        if not pull_res["succeeded"]:
            return {"output": "Failed to pull UI XML file", "succeeded": False}

        return local_xml_path

    def get_screenshot(self):
        """
        Captures a screenshot on the device, pulls it to a temporary file on the host machine, 
        and returns the local file path.
        """
        temp_dir = tempfile.gettempdir()
        local_screenshot_path = os.path.join(temp_dir, "screenshot.png")
        device_screenshot_path = "/sdcard/screenshot.png"

        # Step 1: Capture screenshot on the device
        screenshot_res = self.call(f'adb shell screencap -p {device_screenshot_path}')
        if not screenshot_res["succeeded"]:
            return {"output": "Failed to capture screenshot", "succeeded": False}

        # Step 2: Pull screenshot from device to host
        pull_res = self.call(f'adb pull {device_screenshot_path} {local_screenshot_path}')
        if not pull_res["succeeded"]:
            return {"output": "Failed to pull screenshot", "succeeded": False}

        return local_screenshot_path
