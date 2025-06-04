# MediaHand

This code uses MediaPipe to detect when your thumb and pinky touch and then toggles your system’s media play/pause while showing FPS and real-time media status.

## Features
- Pinky + Thumb Gesture: Detects when your pinky and thumb touch and sends a media play/pause keystroke.
- Debounce Filter: Requires the touch to be detected across multiple consecutive frames to avoid accidental activations.
- Angle Check: Ensures pinky is folded toward thumb (angle < 60°) before toggling media.  
- Dynamic Threshold: Normalizes touch distance by the hand’s bounding-box height, making the gesture robust at different zoom levels.
- Live Feedback: Displays real-time FPS (frames per second) and the actual “Media: On/Off” status (synchronized with the system’s current media session).
- Closing the program: Press 'q'

## Requirements
- Operating System: Windows 10 or later.
- Python: recommended 3.11.
- Webcam: Any standard USB/internal camera that OpenCV can access.
- Dependencies (all installed via `pip`):
  - `opencv-python`
  - `mediapipe`
  - `pynput`
  - `winrt-Windows.Media.Control`
 - To run the program: Run the file PausePlayMedia.py
