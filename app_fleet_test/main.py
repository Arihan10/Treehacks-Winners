from mobius import create_controller, create_emulator
import time

pixel7 = create_emulator('pixel7')
pixel6a = create_emulator('pixel6a')

Mobius = create_controller()

Mobius.do(pixel7, "Check my messages for any new messages from Brian")
Mobius.do(pixel6a, "Create a new contact named Donald Duck")

time.sleep(30)

Mobius.close_all_emulators()