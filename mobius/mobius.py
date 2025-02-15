import os
import subprocess
import time
from appium import webdriver


class Mobius:
    def __init__(self, emulator_name="Emulator"):
        """
        Initializes Mobius with a specified emulator name (defaults to 'Emulator').
        """
        self.emulator_name = emulator_name
        self.appium_driver = None

    def list_avds(self):
        """
        Lists available AVDs (Android Virtual Devices).
        """
        try:
            output = subprocess.check_output(
                ["emulator", "-list-avds"], text=True
            ).strip()
            return output.split("\n") if output else []
        except subprocess.CalledProcessError:
            return []

    def start_emulator(self):
        """
        Starts the specified Android emulator if it's not already running.
        """
        print(f"Starting emulator: {self.emulator_name}")

        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "emulator" in result.stdout:
            print("Emulator already running.")
            return

        # Start the emulator in the background
        command = ["emulator", "-avd", self.emulator_name, "-no-snapshot-save"]
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for emulator to boot
        print("Waiting for emulator to boot...")
        while True:
            output = subprocess.check_output(["adb", "devices"], text=True)
            if "device" in output and "emulator" in output:
                break
            time.sleep(5)

        print("Emulator booted successfully.")

    def start_appium(self):
        """
        Starts the Appium server.
        """
        print("Starting Appium Server...")
        subprocess.Popen(
            ["appium"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(10)  # Give time for Appium to initialize

        desired_caps = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # Default Android emulator ID
            "automationName": "UiAutomator2",
            "app": "/path/to/your/app.apk",  # Replace with actual APK path
        }

        self.appium_driver = webdriver.Remote(
            "http://localhost:4723/wd/hub", desired_caps
        )
        print("Appium session started.")

    def create(self):
        """
        Initializes the emulator and Appium session.
        """
        self.start_emulator()
        self.start_appium()
        return self

    def do(self, action: str):
        print("action: " + action)


"""
# Example usage
mobile = Mobius().init()  # Uses default "Emulator"
# Or with a custom emulator
mobile_custom = Mobius("Pixel_7").init()
"""
