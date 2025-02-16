from ...models import ActiveTask

def execute(task: ActiveTask):
    print("Executing main_do with handler:", task.handler)
    
    task.handler.call("adb...")
    task.handler.ui_dump(...)

    async def process():
        await task.send_message("Processing started...")
        await task.send_message(f"Using handler: {task.handler.__class__.__name__}")
        response = await task.send_message("Processing finished. Awaiting confirmation...")
        print(f"Received response: {response}")
    
    return process()