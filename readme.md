# Hand Gesture Control System

## Overview

This project uses OpenCV, MediaPipe, and PyAutoGUI to enable gesture-based control of your computer. It recognizes hand gestures through a webcam and performs actions such as mouse control and keyboard shortcuts based on detected gestures. Specifically, it implements a pinch gesture to simulate a long left click and a Cmd+Tab functionality for switching applications.

## Features

- **Pinch Gesture Detection:** Recognizes pinch gestures to simulate long left clicks.
- **Mouse Control:** Moves the cursor based on hand position.
- **Cmd+Tab Shortcut:** Detects an open palm gesture to hold down the Cmd key and press Tab to switch applications.
- **Real-time Feedback:** Displays hand gesture information in a smaller window.

## Requirements

- Python 3.x
- OpenCV
- MediaPipe
- PyAutoGUI

You can install the required Python libraries using pip:

```bash
pip install opencv-python mediapipe pyautogui
```

## Installation

1. **Clone the Repository**

   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/shaileshsaravanan/hand-gesture-based-macos-controls.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd hand-gesture-control
   ```

3. **Install Dependencies**

   Ensure you have all the necessary Python packages installed:

   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt` file, install the libraries individually:

   ```bash
   pip install opencv-python mediapipe pyautogui
   ```

## Usage

1. **Run the Script**

   Execute the script to start the gesture control system:

   ```bash
   python final.py
   ```

2. **Gesture Instructions**

   - **Pinch Gesture:** Bring your thumb and index finger close together to simulate a long left click. Hold the pinch to keep the left mouse button pressed. Release the pinch to release the button.
   - **Cmd+Tab Shortcut:** Open your hand with all fingers extended to hold down the Cmd key and press Tab to switch applications. Close your hand to release the Cmd key.

3. **Debugging**

   The script prints the pinch distance to the console for debugging purposes. Adjust the `PINCH_THRESHOLD` constant if the pinch detection is not working as expected.

## Configuration

You can adjust the following constants in the script to suit your needs:

- `PINCH_THRESHOLD`: Distance threshold to consider it a pinch.
- `DRAG_THRESHOLD_TIME`: Time in seconds to determine if a pinch is considered a long press.
- `SMOOTHING_FACTOR`: Smoothing factor for cursor movement.

## Notes

- Ensure you have good lighting and a clear view of your hand for accurate gesture recognition.
- The script uses the default webcam (camera index 0). If you have multiple cameras, adjust the `cv2.VideoCapture` index accordingly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
