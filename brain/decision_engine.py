def decide_action(command):
    command = command.lower()

    if "email" in command or "mail" in command:
        return "gmail"
    elif "calendar" in command or "schedule" in command:
        return "calendar"
    elif "whatsapp" in command or "message" in command:
        return "whatsapp"
    elif any(word in command for word in ["android", "phone", "screenshot", "battery", "volume", "apps", "call"]):
        return "android"
    elif "remote" in command or "server" in command or "dashboard" in command:
        return "remote"
    elif "file" in command or "search" in command:
        return "file_search"
    elif "shutdown" in command or "restart" in command or "system" in command:
        return "system"
    else:
        return "ai"