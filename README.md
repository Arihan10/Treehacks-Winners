## Sample API Usage

Create() -> spawns an emulator or controller
Do("Task") -> uses LLM/VLM technology to intelligently execute the task.

Spawn a fleet of agents
```
from mobius import create_controller, create_emulator
import time

pixel4 = create_emulator('pixel4')
pixel6a = create_emulator('pixel6a')
pixel8 = create_emulator('pixel8')

Mobius = create_controller()

# NATURAL LANGUAGE-DEFINED UNIT TESTS
Mobius.do(pixel6a, "Use Yelp app to find best breakfast nearby")
Mobius.do(pixel4, "Use Yelp app to view user's most recently viewed items")
Mobius.do(pixel8, "Use Yelp app to scroll through local picks")

Mobius.close_all_emulators()
```

Spawn a single agent
```
from mobius import create_controller

Mobius = create_controller()

Mobius.do(device, "Go to instacart and add costco cup noodles to my cart for later")
```

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
