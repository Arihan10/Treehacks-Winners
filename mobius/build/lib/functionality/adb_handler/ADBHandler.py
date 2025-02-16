import subprocess

class ADBHandler:
    """
    Base class for ADB operations.
    Provides common functions like ping and ui_dump.
    Child classes must implement their own call() method.
    """
    def call(self, args, **kwargs):
        raise NotImplementedError("Subclasses must implement the call method.")
    
    def ping(self):
        """Checks if the device is connected by echoing 'ping'."""
        return self.call(["shell", "echo", "ping"])
    
    def ui_dump(self):
        """
        Dumps the current UI hierarchy to an XML file and retrieves its contents.
        """
        dump_res = self.call(["shell", "uiautomator", "dump", "/sdcard/ui.xml"])
        if not dump_res["succeeded"]:
            return dump_res
        

        pull_res = self.call(["pull", "/sdcard/ui.xml", "ui.xml"])
        if not pull_res["succeeded"]:
            return pull_res
        
        try:
            with open("ui.xml", "r", encoding="utf-8") as f:
                xml_content = f.read()
            return {"output": xml_content, "succeeded": True}
        except Exception as e:
            return {"output": str(e), "succeeded": False}
