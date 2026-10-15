import cv2
import mediapipe as mp


class GestureRecognizer:
    def __init__(self, confidence=0.65, show_landmarks=True):
        self.mp_hands = mp.solutions.hands
        self.drawer = mp.solutions.drawing_utils
        self.styles = mp.solutions.drawing_styles
        self.show_landmarks = bool(show_landmarks)
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=float(confidence),
            min_tracking_confidence=float(confidence),
        )

    @staticmethod
    def _extended(landmarks, tip, pip):
        return landmarks[tip].y < landmarks[pip].y - 0.015

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
        if index and middle and ring and pinky:
            gesture = "PAUSE"
        elif index and middle and ring and not pinky:
            gesture = "SCROLL"
        elif index and middle and not ring and not pinky:
            gesture = "DOUBLE_CLICK"
        elif index and not middle and not ring and not pinky:
            gesture = "MOVE"
        else:
            gesture = "NEUTRAL"
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
