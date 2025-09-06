from pywiner.system.process import exec_vbs
import sys

def msgbox(icon="information", title="Pywiner", content=""):
    """
    Displays a native Windows message box.

    Args:
        icon (str): The icon to display.
                    Possible values: "information", "warning", "critical".
        title (str): The title of the message box window.
        content (str): The main message content of the box.
    """
    
    # Map friendly icon names to VBScript integer values
    icons = {
        "information": 64,  # vbInformation
        "warning": 48,      # vbExclamation
        "critical": 16      # vbCritical
    }

    vbs_icon_value = icons.get(icon.lower(), 64) # Default to information if not found

    # Sanitize inputs to prevent VBScript errors with quotes
    clean_content = str(content).replace('"', '""')
    clean_title = str(title).replace('"', '""')

    # Construct the VBScript code
    vbs_code = f"""
    Dim objShell
    Set objShell = CreateObject("WScript.Shell")
    objShell.Popup "{clean_content}", 0, "{clean_title}", {vbs_icon_value}
    """
    
    # Execute the VBScript using your pywiner.system module
    exec_vbs(vbs_code)

if __name__ == '__main__':
    # This is a basic test. For a real test, you should publish the library first.
    
    # Test 1: Information message box
    msgbox(
        icon="information",
        title="Welcome",
        content="This is an information message from Pywiner!"
    )

    # Test 2: Warning message box
    msgbox(
        icon="warning",
        title="Attention!",
        content="This is a warning message."
    )
    
    # Test 3: Critical message box
    msgbox(
        icon="critical",
        title="Error!",
        content="This is a critical error message."
    )