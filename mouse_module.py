import time

import numpy as np
import pyautogui


class MouseController:
    def __init__(self, smoothing=0.78, active_margin=0.16,
                 click_cooldown=0.45, scroll_speed=30, cursor_sensitivity=1.25):
        self.screen_w, self.screen_h = pyautogui.size()
        # Higher alpha follows the hand more closely; lower values smooth more.
        self.smoothing = float(np.clip(smoothing, 0.10, 1.0))
        self.active_margin = float(np.clip(active_margin, 0.0, 0.35))
        self.click_cooldown = max(0.15, float(click_cooldown))
        self.scroll_speed = max(1, int(scroll_speed))
        self.cursor_sensitivity = float(np.clip(cursor_sensitivity, 0.5, 3.0))
        self._cursor = None
        self._last_click = 0.0
        self._click_armed = True
        self._last_scroll_time = 0.0
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0

    def reset_position_filter(self):
        self._cursor = None

    def move_cursor(self, norm_x, norm_y):
        # Map a smaller central camera area to the full monitor so the user can
        # reach screen edges without moving their hand to the camera's edges.
        m = self.active_margin
        x = (float(norm_x) - m) / max(1e-6, 1.0 - 2.0 * m)
        y = (float(norm_y) - m) / max(1e-6, 1.0 - 2.0 * m)
        # Sensitivity expands motion around the centre; clamp at screen edges.
        x = 0.5 + (x - 0.5) * self.cursor_sensitivity
        y = 0.5 + (y - 0.5) * self.cursor_sensitivity
        target = np.array([
            np.clip(x, 0.0, 1.0) * (self.screen_w - 1),
            np.clip(y, 0.0, 1.0) * (self.screen_h - 1),
        ], dtype=float)
        if self._cursor is None:
            self._cursor = target
        else:
            self._cursor += self.smoothing * (target - self._cursor)
        pyautogui.moveTo(int(self._cursor[0]), int(self._cursor[1]), duration=0)

    def click_once(self):
        now = time.monotonic()
        if self._click_armed and now - self._last_click >= self.click_cooldown:
            pyautogui.click()
            self._last_click = now
            self._click_armed = False
            return True
        return False

    def reset_click_gesture(self):
        self._click_armed = True

    def scroll_delta(self, delta_y, threshold=0.004):
        # Scroll only after a meaningful vertical hand movement. Scale the
        # amount gradually rather than issuing a full-speed wheel event per
        # frame, which can make pages jump.
        now = time.monotonic()
        if now - self._last_scroll_time < 0.012 or abs(delta_y) < threshold:
            return
        amount = int(np.clip(-delta_y * self.scroll_speed * 420,
                             -self.scroll_speed, self.scroll_speed))
        if amount:
            pyautogui.scroll(amount)
            self._last_scroll_time = now
