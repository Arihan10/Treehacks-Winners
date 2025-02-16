ADBHandler is NOT usable as an instance. There are some class functions. You must use ADBLocalHandler or ADBWiFiHandler to manage individual devices.



USAGE FOR ADB LOCAL HANDLER ----------------------------
If you have a SINGLE android device plugged in:
adb_handler = ADBLocalHandler()
print(adb_handler.setup())

If you have MULTIPLE android devices plugged in locally (i.e. a fleet):
adb_handler = ADBLocalHandler()
print(adb_handler.setup(device_id = "XYZ"))



USAGE FOR ADB WIFI HANDLER  ----------------------------

If you have a SINGLE android device plugged in or already wifi-enabled over adb:
adb_handler = ADBWiFiHandler()
print(adb_handler.setup()) # After this, it will be ready. You can unplug if not already.

If you have MULTIPLE android devices already wifi-enabled for adb:
adb_handler_1 = ADBWiFiHandler()
print(adb_handler.setup(ip=<ip_1>))
adb_handler_2 = ADBWiFiHandler()
print(adb_handler.setup(ip=<ip_2>))
