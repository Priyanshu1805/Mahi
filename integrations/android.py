import os

def open_app(package):
    """
    Opens an Android app using its package name via ADB.
    Example: open_app("com.whatsapp")
    """
    os.system(f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1")
    return f"Attempting to open {package}"

def send_text(text):
    """
    Sends text input to the Android device via ADB.
    Handles spaces and common special characters by escaping them.
    """
    import shlex
    # Escape characters that 'adb shell input text' doesn't like
    # Characters like & ( ) < > | * ' " needs to be escaped or quoted
    # We'll use a simple replacement for spaces and then quote the whole thing
    escaped_text = text.replace(" ", "%s").replace("'", "\\'").replace("\"", "\\\"").replace("&", "\\&").replace("(", "\\(").replace(")", "\\)")
    os.system(f'adb shell input text "{escaped_text}"')
    return f"Sent text: {text}"

def tap(x, y):
    """
    Taps on the specified coordinates (x, y) on the Android screen.
    """
    os.system(f"adb shell input tap {x} {y}")
    return f"Tapped at {x}, {y}"

def call_number(number):
    """
    Initiates a phone call to the specified number via ADB.
    """
    os.system(f"adb shell am start -a android.intent.action.CALL -d tel:{number}")
    return f"Calling {number}"

def take_screenshot(filename="screenshot.png"):
    """
    Takes a screenshot of the Android device and pulls it to the local machine.
    """
    os.system(f"adb shell screencap -p /sdcard/{filename}")
    os.system(f"adb pull /sdcard/{filename} .")
    return f"Screenshot saved as {filename}"

def get_battery_level():
    """
    Returns the current battery level of the Android device.
    """
    import subprocess
    try:
        result = subprocess.run(["adb", "shell", "dumpsys", "battery"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "level:" in line:
                return line.split(":")[1].strip() + "%"
    except Exception as e:
        return f"Error: {e}"
    return "Could not retrieve battery level"

def set_volume(level):
    """
    Sets the media volume of the Android device (typically 0-15).
    """
    os.system(f"adb shell media volume --set {level}")
    return f"Volume set to {level}"

def list_installed_apps():
    """
    Lists all third-party installed apps on the Android device.
    """
    import subprocess
    try:
        result = subprocess.run(["adb", "shell", "pm", "list", "packages", "-3"], capture_output=True, text=True)
        apps = [line.replace("package:", "") for line in result.stdout.splitlines()]
        return "\n".join(apps) if apps else "No third-party apps found"
    except Exception as e:
        return f"Error: {e}"

def send_tasker_command(command_name, data=None):
    """
    Keep as a bridge for Tasker if needed, but primary control is now ADB.
    """
    print(f"Tasker bridge: {command_name} - {data}")
    return "Tasker command received (via ADB bridge)"
