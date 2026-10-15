# Gesture Mouse — Windows 11

A lightweight local hand-gesture mouse controller using OpenCV, MediaPipe, and PyAutoGUI. It does not use an LLM, Ollama, cloud AI APIs, or cloud video processing.

## Gestures

- Index finger only: move the cursor.
- Index + middle fingers: double-click once while that gesture remains held.
- Index + middle + ring fingers: scroll; move the hand up/down to scroll.
- Open palm: pause when control is active.
- P: pause/resume (preview window must have focus).
- Q or Esc: quit.
- Starts paused. PyAutoGUI fail-safe remains enabled; move cursor to the top-left screen corner to trigger it.

Gesture recognition is heuristic and works best with the palm facing the camera and fingers pointing generally upward.

## Requirements

- Windows 10/11, Python 3.12 64-bit recommended.
- A webcam, or an iPhone camera exposed to Windows as a virtual webcam.
- Internet for initial dependency installation only.

## Install

Open PowerShell in this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

This creates `.venv` and installs packages. No language model is installed.

## Run

```powershell
.\run.bat
```

When the preview opens, focus its window and press **P** to activate control. Test in a harmless window first. Press P to pause and Q/Esc to quit.

## iPhone as a wireless webcam

Install an iPhone-to-Windows webcam app and its official Windows companion/driver from the vendor's official source. Verify its current price, iOS/Windows support, and privacy policy before installing. Open the app on both devices and follow the vendor's connection instructions, often requiring the same Wi-Fi network. Confirm that Windows exposes the phone as a virtual webcam. Then edit `camera_index` in `config.json` and try indices 0, 1, or 2. The app cannot read an arbitrary phone stream URL and does not assume the phone is automatically camera 0.

## Configuration

Edit `config.json`:

- `camera_index`: OpenCV camera device index.
- `frame_width`, `frame_height`: requested resolution (640x480 is a good starting point).
- `smoothing`: 0.05 is responsive; higher values smooth more slowly, up to 1.0.
- `active_margin`: ignores the outer camera region when mapping the cursor.
- `scroll_speed`: maximum scroll amount per frame movement.
- `scroll_threshold`: minimum hand movement to scroll.
- `double_click_cooldown`: minimum seconds between double-click activations.
- `confidence_threshold`: MediaPipe detection/tracking confidence.
- `mirror_preview`: mirror the camera view.
- `show_landmarks`: show hand skeleton.

## Troubleshooting

- Camera unavailable: ensure Windows recognizes the webcam, close other camera apps, and try another `camera_index`.
- iPhone not found: ensure the vendor app/driver is installed and Windows exposes a virtual webcam.
- P key ignored: click the preview window to focus it.
- Poor recognition: improve front lighting and keep the palm visible/upright.
- Unexpected cursor movement: press P to pause or trigger PyAutoGUI's top-left fail-safe.

## Limitations

This is a prototype using simple finger-position heuristics. Sideways or rotated hands can be misclassified. Real-world camera and gesture testing requires a camera device; no hardware test is claimed here. Camera companion apps may have their own network behavior; this Python application processes frames locally.
