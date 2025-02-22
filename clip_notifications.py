from plyer import notification


# notifiaction when text is copied to clipboard via clipboard monitoring
def show_copied_notification(text):
    notification.notify(
        title="Clipboard Saved!",
        message=f"Copied: {text[:50]}...",  # Show first 50 characters
        timeout=2
    )
# notification when monitoring is toggled
def show_toggle_notification(text):
    notification.notify(
        title ="Clipboard saver",
        message = text,
        timeout = 1
    )

