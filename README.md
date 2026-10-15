# Gesture Mouse — Windows 10/11

A lightweight local hand-gesture mouse controller using OpenCV, MediaPipe, and PyAutoGUI. It does not use an LLM, Ollama, cloud AI APIs, or cloud video processing.

## Gestures

- **Index finger only:** move the cursor.
- **Pinch thumb + index fingertip:** single left-click. Hold the pinch to trigger one click; release before clicking again.
- **Index + middle fingers extended:** scroll. Move the hand up/down to scroll; keep ring and pinky curled.
- **Open palm:** pause when control is active.
- **P:** pause/resume (preview window must have focus).
- **Q or Esc:** quit.
- Starts paused. PyAutoGUI fail-safe remains enabled; move cursor to the top-left screen corner to trigger it.

Gesture recognition uses palm-relative landmark distances and short confirmation to reduce accidental gesture switching. It works best with a well-lit, visible palm facing generally toward the camera. Finger poses can still be misclassified when fingers overlap or the hand is strongly rotated.

## Requirements

- Windows 10/11, 64-bit Python 3.12 recommended.
- A webcam, or an iPhone camera exposed to Windows as a virtual webcam.
- Internet for initial dependency installation only.

## Install

Open PowerShell in this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

The setup pins MediaPipe 0.10.21 because this app uses its `mp.solutions.hands` API. It creates `.venv` and installs dependencies. No language model is installed.

## Run

```powershell
.\run.bat
```

When the preview opens, focus its window and press **P** to activate control. Test in a harmless window first. Press P to pause and Q/Esc to quit.

## Configuration

Edit `config.json` and restart the app after changes:

- `camera_index`: OpenCV camera device index.
- `frame_width`, `frame_height`: requested resolution (640x480 is a good starting point).
- `smoothing`: cursor follow factor from 0.10 to 1.0. Higher values respond faster; lower values smooth more but add lag.
- `active_margin`: camera border to ignore when mapping the cursor. Higher values let a smaller central hand movement reach screen edges.
- `cursor_sensitivity`: expands cursor movement around screen centre; default 1.25. Increase carefully if it feels too fast.
- `scroll_speed`: maximum wheel amount per update.
- `scroll_threshold`: minimum normalized vertical movement needed to scroll.
- `click_cooldown`: minimum seconds between click activations.
- `gesture_confirm_frames`: frames required to confirm a changed gesture; lower is faster, higher is more stable.
- `confidence_threshold`: MediaPipe hand detection confidence.
- `mirror_preview`: mirror the camera view.
- `show_landmarks`: show hand skeleton.

## iPhone as a wireless webcam

Install an iPhone-to-Windows webcam app and its official Windows companion/driver from the vendor's official source. Verify its current price, iOS/Windows support, and privacy policy before installing. Open the app on both devices and follow the vendor's connection instructions, often requiring the same Wi-Fi network. Confirm that Windows exposes the phone as a virtual webcam. Then edit `camera_index` in `config.json` and try indices 0, 1, or 2. The app cannot read an arbitrary phone stream URL and does not assume the phone is automatically camera 0.

## Troubleshooting

- Camera unavailable: ensure Windows recognizes the webcam, close other camera apps, and try another `camera_index`.
- iPhone not found: ensure the vendor app/driver is installed and Windows exposes a virtual webcam.
- P key ignored: click the preview window to focus it.
- Poor recognition: improve front lighting, keep the full hand visible, and avoid fingers overlapping.
- Cursor too slow: raise `smoothing` closer to 1.0 or raise `cursor_sensitivity` slightly.
- Cursor cannot reach screen edges: raise `active_margin` in small steps, e.g. 0.18.
- Unexpected cursor movement: press P to pause or trigger PyAutoGUI's top-left fail-safe.

## Limitations

This is a local prototype, not a full accessibility-certified pointer. Simple hand landmarks can still be misclassified by poor lighting, camera blur, and unusual hand angles. Real-world camera and gesture testing requires a camera device; no hardware test is claimed here. Camera companion apps may have their own network behavior; this Python application processes frames locally.
