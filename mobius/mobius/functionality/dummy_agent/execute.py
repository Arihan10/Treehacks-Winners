from mobius.models import ActiveTask
import os
import logging

LOG_FILE = "execution.log"

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

clear_log()

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

async def execute(task: ActiveTask):
    logging.info(task.handler.call("adb shell wm size"))
    logging.info(task.handler.get_xml())
    logging.info(task.handler.get_screenshot())

    return True
    