Commands to set up poetry
```
cd mobius 
poetry install (repeat this command whenever you make changes to mobius)
poetry shell 
```

To add new pkgs to poetry, cd mobius then poetry add pkg-name

To run an application, make sure poetry shell is active, then something like:
```
cd app_fleet_test
python main.py
```

if adb devices reveals an emulator that is offline but you already closed the window:

adb -s emulator-5554 emu kill

this takes a while! be patient