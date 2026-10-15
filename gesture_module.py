import math

import cv2
import mediapipe as mp


class GestureRecognizer:
    """One-hand gesture recognizer using palm-relative landmark distances."""

    def __init__(self, confidence=0.55, show_landmarks=True):
        # MediaPipe 0.10.21 exposes the legacy solutions API used here.
        self.mp_hands = mp.solutions.hands
        self.drawer = mp.solutions.drawing_utils
        self.styles = mp.solutions.drawing_styles
        self.show_landmarks = bool(show_landmarks)
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=float(confidence),
            min_tracking_confidence=0.55,
        )

    @staticmethod
    def _distance(a, b):
        return math.hypot(float(a.x) - float(b.x), float(a.y) - float(b.y))

    @classmethod
    def _extended(cls, landmarks, tip, pip):
        # Compare each fingertip to its middle joint relative to the wrist.
        # This works for more hand angles than a fixed "tip above joint" test.
        wrist = landmarks[0]
        tip_distance = cls._distance(landmarks[tip], wrist)
        pip_distance = cls._distance(landmarks[pip], wrist)
        return tip_distance > pip_distance * 1.16

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            return None, "NO HAND", None

        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark
        index = self._extended(lm, 8, 6)
        middle = self._extended(lm, 12, 10)
        ring = self._extended(lm, 16, 14)
        pinky = self._extended(lm, 20, 18)

        # Normalize pinch distance by palm width so the threshold scales with
        # distance from the camera.
        palm_width = max(self._distance(lm[5], lm[17]), 1e-4)
        pinch_ratio = self._distance(lm[4], lm[8]) / palm_width
        pinching = pinch_ratio < 0.38

        if index and middle and ring and pinky:
            gesture = "PAUSE"
        elif pinching:
            gesture = "CLICK"
        elif index and middle and not ring and not pinky:
            gesture = "SCROLL"
        elif index and not middle and not ring and not pinky:
            gesture = "MOVE"
        else:
            gesture = "NEUTRAL"

        # Use index fingertip for cursor position and middle MCP as a steadier
        # scroll anchor. Coordinates are normalized by MediaPipe to 0..1.
        data = ((float(lm[8].x), float(lm[8].y)), float(lm[9].y))
        return hand, gesture, data

    def draw(self, frame, hand):
        if self.show_landmarks and hand is not None:
            self.drawer.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS,
                self.styles.get_default_hand_landmarks_style(),
                self.styles.get_default_hand_connections_style(),
            )

    def close(self):
        self.hands.close()
