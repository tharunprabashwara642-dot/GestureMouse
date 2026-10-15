# Gesture Mouse — Windows 10/11

A lightweight, local two-hand gesture mouse using OpenCV, MediaPipe, and PyAutoGUI. Camera frames are processed locally; no cloud AI or language model is used.

## Two-hand controls

By default, the **right hand controls the cursor** and the **left hand performs clicks**. Keep both hands visible for the intended two-hand workflow.

- **Cursor hand — index finger only:** move the pointer.
- **Cursor hand — index + middle fingers:** scroll. Move that hand vertically for smooth, continuous scrolling.
- **Other hand — index finger only:** one left-click. Keep the pose briefly; it clicks once, not repeatedly.
- **Other hand — index + middle fingers:** one double-click.
- **Open palm:** pause the controller when active.
- **P:** pause/resume (preview window must have focus).
- **Q or Esc:** quit.
- The app starts paused. PyAutoGUI fail-safe stays enabled; move the pointer to the top-left corner to trigger it.

If you are left-handed, change `cursor_hand` to `"Left"` in `config.json`; the other hand automatically becomes the click hand.

## Install

Requirements: 64-bit Python 3.12 recommended, Windows 10/11, and a webcam.

Open PowerShell in the extracted project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\run.bat
```

The setup pins MediaPipe 0.10.21 because this project uses the `mp.solutions.hands` API.

## Tuning

Close the app before editing `config.json`; restart after saving.

- `cursor_hand`: `"Right"` or `"Left"`; which hand moves the pointer.
- `cursor_sensitivity`: cursor reach/sensitivity; default 1.35. Increase carefully if needed.
- `smoothing`: follow responsiveness. The controller uses a small movement deadband and follows larger movements faster to reduce hand tremor without making fast movement feel sluggish.
- `active_margin`: camera border ignored during mapping. A larger value makes the pointer reach screen edges with less hand travel.
- `scroll_speed`: scroll response; default 900. Increase in small steps if it feels slow, or decrease if it moves too far.
- `gesture_confirm_frames`: frames required to confirm a gesture; 2 is responsive while filtering brief misclassifications.
- `show_landmarks`: show/hide the thin hand skeleton.
- `confidence_threshold`: hand detection confidence threshold.

## Troubleshooting

- **Wrong hand role:** set `cursor_hand` to `"Left"` or `"Right"` in `config.json`.
- **One hand is not detected:** ensure both hands are fully visible, well lit, and not overlapping.
- **Cursor trembles:** improve lighting and keep the index fingertip visible; the movement deadband filters very small changes, but camera blur can still cause jitter.
- **Scrolling is too fast/slow:** adjust `scroll_speed` in `config.json`.
- **P key ignored:** click the preview window to focus it.
- **Camera unavailable:** close other camera apps and check Windows camera privacy permissions.

## Limitations

This is a practical prototype, not a certified accessibility device. Handedness labels and finger poses can be misclassified by lighting, camera angle, overlapping fingers, or unusual hand orientation. The code changes can be checked statically, but actual webcam/gesture behavior must be verified on the target PC.
