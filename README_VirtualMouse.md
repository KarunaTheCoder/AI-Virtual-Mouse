# AI Virtual Mouse

Control your computer's mouse using hand gestures captured from a webcam,
powered by MediaPipe hand tracking and a Streamlit interface.

## Overview
This application uses computer vision to detect hand landmarks in real
time and translates specific finger gestures into mouse actions: cursor
movement, left clicks, scrolling, and a "fist" gesture macro that
minimizes all windows.

## Features
- **Cursor control:** move the index finger to move the mouse pointer,
  with smoothing (EMA filter) to reduce jitter
- **Left click:** pinch the thumb and index finger together
- **Scroll mode:** raise index, middle, and ring fingers together to
  scroll up/down
- **Macro trigger:** close your fist to minimize all open windows
  (`Win + D`), with a 1.5-second cooldown to prevent repeated firing
- **Adjustable settings** via the sidebar: smoothing strength, frame
  skip rate (for performance), and click sensitivity distance

## How It Works
1. OpenCV captures frames from your webcam.
2. MediaPipe's HandLandmarker model detects 21 hand landmarks per frame.
3. Finger positions are checked to determine which fingers are "up."
4. Based on the finger combination, the app enters one of three modes:
   Navigation, Scroll, or Macro.
5. PyAutoGUI translates the detected gesture into real mouse/keyboard
   actions on the host machine.

## Tech Stack
- **OpenCV** — webcam capture and frame processing
- **MediaPipe** — hand landmark detection
- **PyAutoGUI** — simulating mouse movement, clicks, and hotkeys
- **Streamlit** — web-based control panel and live video display

## Requirements
```
opencv-python
mediapipe
pyautogui
streamlit
```
You also need the MediaPipe hand landmark model file, `hand_landmarker.task`,
placed in the project root (download from MediaPipe's model hub).

## Running the App
```bash
pip install -r requirements.txt
streamlit run final_file.py
```
Check the **Start** box in the sidebar to activate the webcam and begin
gesture control.

## Controls Summary
| Gesture | Action |
|---|---|
| Index finger up, others down | Move cursor |
| Thumb + index pinch | Left click |
| Index + middle + ring up | Scroll |
| Closed fist | Minimize all windows (macro) |

## Sidebar Settings
| Setting | Purpose |
|---|---|
| EMA Smoothing Alpha | Controls cursor movement smoothness vs. responsiveness |
| Frame Skip Rate | Skips frames to improve performance on slower machines |
| Click Distance Threshold | Pinch distance (in pixels) required to register a click |
| Enable Fist Macro Trigger | Turns the minimize-all gesture on/off |

## Limitations
- Requires good, consistent lighting for reliable hand detection
- Works with one hand at a time
- Cursor smoothing may introduce slight lag at low alpha values
- Not tested across all operating systems/webcam configurations

## Disclaimer
This tool simulates real mouse and keyboard input on your system.
Use with care, and keep the browser window with webcam access focused
so you can stop it (uncheck **Start**) if gestures misbehave.

## Files
- `final_file.py` — main application (Streamlit UI + gesture logic)
- `hand_landmarker.task` — MediaPipe hand landmark model (not included,
  download separately)
- `requirements.txt` — Python dependencies
