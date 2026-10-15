import json
from pathlib import Path

import cv2

from camera_module import CameraManager
from gesture_module import GestureRecognizer
from mouse_module import MouseController

APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_CONFIG = {
    "camera_index": 0, "frame_width": 640, "frame_height": 480,
    "mirror_preview": True, "smoothing": 0.28, "active_margin": 0.08,
    "scroll_speed": 18, "scroll_threshold": 0.012,
    "double_click_cooldown": 0.8, "confidence_threshold": 0.65,
    "show_landmarks": True,
}


def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
        return DEFAULT_CONFIG.copy()
    try:
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("config must be a JSON object")
        return {**DEFAULT_CONFIG, **loaded}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"Could not read config.json: {exc}") from exc


def main():
    try:
        cfg = load_config()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print("Gesture Mouse — local hand-gesture controller")
    print("Starts PAUSED. Focus preview window: P pause/resume; Q or ESC quits.")
    print("Safety: move cursor to top-left corner to trigger PyAutoGUI fail-safe.")
    camera = CameraManager(cfg["camera_index"], cfg["frame_width"],
                           cfg["frame_height"], cfg["mirror_preview"])
    recognizer = None
    try:
        camera.start()
        recognizer = GestureRecognizer(cfg["confidence_threshold"], cfg["show_landmarks"])
        mouse = MouseController(cfg["smoothing"], cfg["active_margin"],
                                cfg["double_click_cooldown"], cfg["scroll_speed"])
    except Exception as exc:
        camera.release()
        if recognizer:
            recognizer.close()
        print(f"\n[ERROR] {exc}")
        print("For iPhone use, install and open a compatible Windows virtual-webcam app first.")
        return 1

    paused = True
    scroll_prev_y = None
    open_palm_frames = 0
    window = "Gesture Mouse Controller"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    try:
        while True:
            ok, frame = camera.read_frame()
            if not ok or frame is None:
                print("[ERROR] Camera frame lost; stopping for safety.")
                break
            h, w = frame.shape[:2]
            hand, gesture, data = recognizer.process_frame(frame)
            recognizer.draw(frame, hand)

            open_palm_frames = open_palm_frames + 1 if gesture == "PAUSE" else 0
            if not paused and open_palm_frames >= 5:
                paused = True
                scroll_prev_y = None
                print("[STATUS] Open palm detected: PAUSED")

            if not paused and data is not None:
                if gesture == "MOVE":
                    mouse.reset_click_gesture()
                    scroll_prev_y = None
                    (x, y), _ = data
                    mouse.move_cursor(x, y)
                elif gesture == "DOUBLE_CLICK":
                    scroll_prev_y = None
                    if mouse.double_click_once():
                        print("[ACTION] Double-click")
                elif gesture == "SCROLL":
                    mouse.reset_click_gesture()
                    _, anchor_y = data
                    if scroll_prev_y is not None:
                        delta = anchor_y - scroll_prev_y
                        if abs(delta) >= float(cfg["scroll_threshold"]):
                            mouse.scroll_delta(delta)
                    scroll_prev_y = anchor_y
                else:
                    mouse.reset_click_gesture()
                    scroll_prev_y = None
            else:
                if gesture != "DOUBLE_CLICK":
                    mouse.reset_click_gesture()
                scroll_prev_y = None

            status = "PAUSED" if paused else "ACTIVE"
            color = (0, 0, 255) if paused else (0, 200, 0)
            cv2.rectangle(frame, (0, 0), (w, 76), (25, 25, 25), -1)
            cv2.putText(frame, f"Status: {status}", (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
            cv2.putText(frame, f"Gesture: {gesture}", (12, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1)
            cv2.putText(frame, "P: Pause/Resume   Q/ESC: Quit", (12, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (230, 230, 230), 1)
            cv2.imshow(window, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("p"), ord("P")):
                paused = not paused
                open_palm_frames = 0
                scroll_prev_y = None
                mouse.reset_click_gesture()
                print(f"[STATUS] {'PAUSED' if paused else 'ACTIVE'}")
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as exc:
        print(f"\n[ERROR] Controller stopped safely: {exc}")
        return 1
    finally:
        camera.release()
        if recognizer:
            recognizer.close()
        cv2.destroyAllWindows()
        print("[INFO] Shutdown complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
