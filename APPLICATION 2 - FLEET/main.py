import sys; import os
sys.path.append(os.path.abspath(r"C:\Users\tminh\Downloads\Treehacks-Winners"))

from mobius.src import create_emulator, start_server

devices = [
    'pixel7',
    'pixel6a'
]

device_ids = []
for device in devices:
    device_ids.append(create_emulator(device))

url = start_server()

