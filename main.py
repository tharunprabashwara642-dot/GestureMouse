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
    "cursor_sensitivity": 1.35, "scroll_speed": 900,
    "click_cooldown": 0.45, "confidence_threshold": 0.55,
    "show_landmarks": True, "gesture_confirm_frames": 2,
    "cursor_hand": "Right",
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

    cursor_hand = str(cfg["cursor_hand"]).capitalize()
    if cursor_hand not in ("Left", "Right"):
        cursor_hand = "Right"
    action_hand = "Left" if cursor_hand == "Right" else "Right"

    print("Gesture Mouse — two-hand controller")
    print(f"Cursor hand: {cursor_hand} | Click hand: {action_hand}")
    print(f"{cursor_hand} hand: index = move | index+middle = smooth scroll")
    print(f"{action_hand} hand: index = single click | index+middle = double-click")
    print("Starts PAUSED. Focus preview window: P pause/resume; Q or ESC quits.")
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
    open_palm_frames = 0
    candidates = {}
    candidate_counts = {}
    stable = {}
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
            items = recognizer.process_frame(frame)
            recognizer.draw(frame, items)

            for item in items:
                label = item["label"]
                gesture = item["gesture"]
                if label not in ("Left", "Right"):
                    continue
                if candidates.get(label) == gesture:
                    candidate_counts[label] = candidate_counts.get(label, 0) + 1
                else:
                    candidates[label] = gesture
                    candidate_counts[label] = 1
                if candidate_counts[label] >= confirm_frames:
                    stable[label] = gesture

            any_open_palm = any(item["gesture"] == "OPEN" for item in items)
            open_palm_frames = open_palm_frames + 1 if any_open_palm else 0
            if not paused and open_palm_frames >= 5:
                paused = True
                mouse.reset_scroll_filter()
                mouse.reset_position_filter()
                print("[STATUS] Open palm detected: PAUSED")

            current = {item["label"]: item for item in items if item["label"] in ("Left", "Right")}
            cursor_item = current.get(cursor_hand)
            action_item = current.get(action_hand)
            cursor_gesture = stable.get(cursor_hand, "NO HAND")
            action_gesture = stable.get(action_hand, "NO HAND")
            click_feedback = ""

            if not paused:
                if cursor_item is not None and cursor_gesture == "ONE":
                    mouse.reset_scroll_filter()
                    x, y = cursor_item["cursor"]
                    mouse.move_cursor(x, y)
                elif cursor_item is not None and cursor_gesture == "TWO":
                    mouse.scroll_delta(cursor_item["scroll_y"])
                else:
                    mouse.reset_scroll_filter()

                if action_item is not None and action_gesture == "ONE":
                    if mouse.click_once():
                        click_feedback = "SINGLE CLICK"
                elif action_item is not None and action_gesture == "TWO":
                    if mouse.double_click_once():
                        click_feedback = "DOUBLE CLICK"
                elif action_item is not None and action_gesture not in ("NO HAND",):
                    mouse.reset_click_gesture()

            status = "PAUSED" if paused else "ACTIVE"
            color = (0, 0, 255) if paused else (0, 200, 0)
            cv2.rectangle(frame, (0, 0), (w, 112), (25, 25, 25), -1)
            cv2.putText(frame, f"Status: {status}", (12, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"{cursor_hand} cursor: {cursor_gesture} | {action_hand} action: {action_gesture}",
                        (12, 49), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "Cursor hand: 1 finger=move, 2 fingers=scroll",
                        (12, 73), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1, cv2.LINE_AA)
            cv2.putText(frame, "Other hand: 1 finger=click, 2 fingers=double-click",
                        (12, 93), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1, cv2.LINE_AA)
            if click_feedback:
                cv2.putText(frame, click_feedback, (w - 190, 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "P: Pause/Resume   Q/ESC: Quit", (12, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1, cv2.LINE_AA)
            cv2.imshow(window, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("p"), ord("P")):
                paused = not paused
                open_palm_frames = 0
                candidates.clear()
                candidate_counts.clear()
                stable.clear()
                mouse.reset_click_gesture()
                mouse.reset_scroll_filter()
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
