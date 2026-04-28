import os

def execute_system(command):
    """Executes system-level commands."""
    command = command.lower()
    
    if "shutdown" in command:
        os.system("shutdown /s /t 10")
        return "Shutting down the system in 10 seconds."
    
    elif "restart" in command:
        os.system("shutdown /r /t 10")
        return "Restarting the system in 10 seconds."
    
    elif "notepad" in command:
        os.system("notepad")
        return "Opening Notepad."
    
    else:
        return "System command not recognized."
