import math

import cv2
import mediapipe as mp


class GestureRecognizer:
    """Two-hand gesture recognizer. Right hand moves/scrolls; left hand clicks."""

    def __init__(self, confidence=0.55, show_landmarks=True):
        self.mp_hands = mp.solutions.hands
        self.show_landmarks = bool(show_landmarks)
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=float(confidence),
            min_tracking_confidence=0.60,
        )

    @staticmethod
    def _distance(a, b):
        return math.hypot(float(a.x) - float(b.x), float(a.y) - float(b.y))

    @classmethod
    def _extended(cls, landmarks, tip, pip):
        wrist = landmarks[0]
        tip_distance = cls._distance(landmarks[tip], wrist)
        pip_distance = cls._distance(landmarks[pip], wrist)
        return tip_distance > pip_distance * 1.10

    @classmethod
    def _classify(cls, landmarks):
        index = cls._extended(landmarks, 8, 6)
        middle = cls._extended(landmarks, 12, 10)
        ring = cls._extended(landmarks, 16, 14)
        pinky = cls._extended(landmarks, 20, 18)
        if index and middle and ring and pinky:
            return "OPEN"
        if index and middle and not ring and not pinky:
            return "TWO"
        if index and not middle and not ring and not pinky:
            return "ONE"
        return "NEUTRAL"

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        if not results.multi_hand_landmarks:
            return []

        items = []
        handedness_list = results.multi_handedness or []
        for i, hand in enumerate(results.multi_hand_landmarks):
            label = "Unknown"
            if i < len(handedness_list) and handedness_list[i].classification:
                label = handedness_list[i].classification[0].label
            lm = hand.landmark
            items.append({
                "hand": hand,
                "label": label,
                "gesture": self._classify(lm),
                "cursor": (float(lm[8].x), float(lm[8].y)),
                "scroll_y": float(lm[9].y),
            })
        return items

    def draw(self, frame, items):
        if not self.show_landmarks:
            return
        height, width = frame.shape[:2]
        # Draw a slim, low-clutter skeleton instead of MediaPipe's thick defaults.
        connections = self.mp_hands.HAND_CONNECTIONS
        for item in items:
            points = [
                (int(lm.x * width), int(lm.y * height))
                for lm in item["hand"].landmark
            ]
            for start, end in connections:
                cv2.line(frame, points[start], points[end], (180, 205, 90), 1, cv2.LINE_AA)
            for x, y in points:
                cv2.circle(frame, (x, y), 2, (80, 230, 255), -1, cv2.LINE_AA)
            label = item["label"]
            x, y = points[0]
            cv2.putText(frame, label, (x + 8, max(18, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 230, 255), 1, cv2.LINE_AA)

    def close(self):
        self.hands.close()
