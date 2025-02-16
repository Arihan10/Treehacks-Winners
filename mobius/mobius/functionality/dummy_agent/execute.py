from mobius.models import ActiveTask

import logging

logging.basicConfig(
    filename="execution.log",   # Log file name
    level=logging.INFO,    # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def execute(task: ActiveTask):
    logging.info("HALHKFHSJDHSLKJFLSKJFD")
    logging.info(task.handler.call("adb shell get wm size"))
    