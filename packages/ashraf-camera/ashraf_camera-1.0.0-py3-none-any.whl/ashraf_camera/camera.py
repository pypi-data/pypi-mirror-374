import cv2
import pyautogui

def capture(action: str, filename: str = None):
    action = action.lower().strip()

    if action == "screenshot":
        if not filename:
            filename = "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")

    elif action == "photo me":
        if not filename:
            filename = "photo.png"
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            cv2.imwrite(filename, frame)
            print(f"Photo saved as {filename}")
        else:
            print("❌ Failed to capture photo")
        cam.release()
        cv2.destroyAllWindows()

    else:
        print("⚠️ Unknown command. Use 'screenshot' or 'photo me'.")
