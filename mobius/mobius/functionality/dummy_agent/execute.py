from mobius.models import ActiveTask
import os
import logging

async def execute(task: ActiveTask):
    logging.info(task.handler.call("adb shell wm size"))
    logging.info(task.handler.get_xml())
    logging.info(task.handler.get_screenshot())

    return True
    