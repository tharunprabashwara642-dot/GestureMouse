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
    "mirror_preview": True, "smoothing": 0.78, "active_margin": 0.16,
    "cursor_sensitivity": 1.25, "scroll_speed": 30,
    "scroll_threshold": 0.004, "click_cooldown": 0.45,
    "confidence_threshold": 0.55, "show_landmarks": True,
    "gesture_confirm_frames": 2,
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

    print("Gesture Mouse — responsive local hand-gesture controller")
    print("Starts PAUSED. Focus preview window: P pause/resume; Q or ESC quits.")
    print("Gestures: index = move | pinch thumb+index = click | index+middle = scroll")
    print("Safety: move cursor to top-left corner to trigger PyAutoGUI fail-safe.")
    camera = CameraManager(cfg["camera_index"], cfg["frame_width"],
                           cfg["frame_height"], cfg["mirror_preview"])
    recognizer = None
    try:
        camera.start()
        recognizer = GestureRecognizer(cfg["confidence_threshold"], cfg["show_landmarks"])
        mouse = MouseController(
            cfg["smoothing"], cfg["active_margin"], cfg["click_cooldown"],
            cfg["scroll_speed"], cfg["cursor_sensitivity"]
        )
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
    raw_candidate = None
    candidate_frames = 0
    stable_gesture = "NEUTRAL"
    confirm_frames = max(1, int(cfg["gesture_confirm_frames"]))
    window = "Gesture Mouse Controller"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    try:
        while True:
            ok, frame = camera.read_frame()
            if not ok or frame is None:
                print("[ERROR] Camera frame lost; stopping for safety.")
                break
            h, w = frame.shape[:2]
            hand, raw_gesture, data = recognizer.process_frame(frame)
            recognizer.draw(frame, hand)

            if raw_gesture == raw_candidate:
                candidate_frames += 1
            else:
                raw_candidate = raw_gesture
                candidate_frames = 1

            if raw_gesture == "NO HAND":
                stable_gesture = "NO HAND"
            elif candidate_frames >= confirm_frames:
                stable_gesture = raw_gesture

            open_palm_frames = open_palm_frames + 1 if raw_gesture == "PAUSE" else 0
            if not paused and open_palm_frames >= 5:
                paused = True
                scroll_prev_y = None
                mouse.reset_position_filter()
                print("[STATUS] Open palm detected: PAUSED")

            if not paused and data is not None:
                if stable_gesture == "MOVE":
                    mouse.reset_click_gesture()
                    scroll_prev_y = None
                    (x, y), _ = data
                    mouse.move_cursor(x, y)
                elif stable_gesture == "CLICK":
                    scroll_prev_y = None
                    if mouse.click_once():
                        cv2.putText(frame, "CLICK", (w - 110, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                elif stable_gesture == "SCROLL":
                    mouse.reset_click_gesture()
                    _, anchor_y = data
                    if scroll_prev_y is not None:
                        delta = anchor_y - scroll_prev_y
                        mouse.scroll_delta(delta, float(cfg["scroll_threshold"]))
                    scroll_prev_y = anchor_y
                else:
                    mouse.reset_click_gesture()
                    scroll_prev_y = None
            else:
                if stable_gesture != "CLICK":
                    mouse.reset_click_gesture()
                scroll_prev_y = None

            status = "PAUSED" if paused else "ACTIVE"
            color = (0, 0, 255) if paused else (0, 200, 0)
            cv2.rectangle(frame, (0, 0), (w, 94), (25, 25, 25), -1)
            cv2.putText(frame, f"Status: {status}", (12, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.62, color, 2)
            cv2.putText(frame, f"Gesture: {stable_gesture}", (12, 51),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(frame, "Index: move | Pinch: click | Index+middle: scroll",
                        (12, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (220, 220, 220), 1)
            cv2.putText(frame, "P: Pause/Resume   Q/ESC: Quit", (12, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (230, 230, 230), 1)
            cv2.imshow(window, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("p"), ord("P")):
                paused = not paused
                open_palm_frames = 0
                scroll_prev_y = None
                raw_candidate = None
                candidate_frames = 0
                stable_gesture = "NEUTRAL"
                mouse.reset_click_gesture()
                mouse.reset_position_filter()
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
