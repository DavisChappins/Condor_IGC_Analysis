import pyautogui
import keyboard
import os
from datetime import datetime
import time
from pynput import mouse

# Create screenshots directory if it doesn't exist
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

# Screenshot counter
counter = 1

# Define the area to capture (adjust these values as needed)
CAPTURE_X = 990
CAPTURE_Y = 530
CAPTURE_WIDTH = 2200
CAPTURE_HEIGHT = 1300

def on_click(x, y, button, pressed):
    """Callback function that triggers when mouse is clicked"""
    global counter
    
    if pressed and button == button.left:  # Only trigger on left mouse button press
        try:
            # Take the screenshot
            screenshot = pyautogui.screenshot(region=(CAPTURE_X, CAPTURE_Y, CAPTURE_WIDTH, CAPTURE_HEIGHT))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'screenshots/screenshot_{counter}_{timestamp}.png'
            
            # Save the screenshot
            screenshot.save(filename)
            
            print(f'Screenshot saved: {filename}')
            counter += 1
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")

def main():
    print("Screenshot script running...")
    print("Press 'q' to quit")
    print(f"Capture area: {CAPTURE_X}, {CAPTURE_Y}, {CAPTURE_WIDTH}x{CAPTURE_HEIGHT}")
    
    # Create mouse listener
    with mouse.Listener(on_click=on_click) as listener:
        # Keep the script running until 'q' is pressed
        keyboard.wait('q')
        listener.stop()

if __name__ == "__main__":
    main()