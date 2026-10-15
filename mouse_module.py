import time
import numpy as np
import pyautogui


class MouseController:
    def __init__(self, smoothing=0.28, active_margin=0.08,
                 double_click_cooldown=0.8, scroll_speed=18):
        self.screen_w, self.screen_h = pyautogui.size()
        self.smoothing = float(np.clip(smoothing, 0.05, 1.0))
        self.active_margin = float(np.clip(active_margin, 0.0, 0.25))
        self.double_click_cooldown = max(0.2, float(double_click_cooldown))
        self.scroll_speed = max(1, int(scroll_speed))
        self._cursor = None
        self._last_click = 0.0
        self._click_armed = True
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.005

    def move_cursor(self, norm_x, norm_y):
        m = self.active_margin
        x = (float(norm_x) - m) / max(1e-6, 1.0 - 2.0 * m)
        y = (float(norm_y) - m) / max(1e-6, 1.0 - 2.0 * m)
        target = np.array([
            np.clip(x, 0.0, 1.0) * (self.screen_w - 1),
            np.clip(y, 0.0, 1.0) * (self.screen_h - 1),
        ])
        if self._cursor is None:
            self._cursor = target
        else:
            self._cursor += self.smoothing * (target - self._cursor)
        pyautogui.moveTo(int(self._cursor[0]), int(self._cursor[1]), duration=0)

    def double_click_once(self):
        now = time.monotonic()
        if self._click_armed and now - self._last_click >= self.double_click_cooldown:
            pyautogui.doubleClick(interval=0.08)
            self._last_click = now
            self._click_armed = False
            return True
        return False

    def reset_click_gesture(self):
        self._click_armed = True

    def scroll_delta(self, delta_y):
        amount = int(np.clip(-delta_y * self.scroll_speed * 900,
                             -self.scroll_speed, self.scroll_speed))
        if amount:
            pyautogui.scroll(amount)
