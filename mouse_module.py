import time

import numpy as np
import pyautogui


class MouseController:
    def __init__(self, smoothing=0.78, active_margin=0.16,
                 click_cooldown=0.45, scroll_speed=900, cursor_sensitivity=1.35):
        self.screen_w, self.screen_h = pyautogui.size()
        self.smoothing = float(np.clip(smoothing, 0.10, 1.0))
        self.active_margin = float(np.clip(active_margin, 0.0, 0.35))
        self.click_cooldown = max(0.15, float(click_cooldown))
        self.scroll_speed = max(100, int(scroll_speed))
        self.cursor_sensitivity = float(np.clip(cursor_sensitivity, 0.5, 3.0))
        self._cursor = None
        self._last_click = 0.0
        self._click_armed = True
        self._last_scroll_time = 0.0
        self._scroll_anchor = None
        self._scroll_velocity = 0.0
        self._scroll_residual = 0.0
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0

    def reset_position_filter(self):
        self._cursor = None

    def move_cursor(self, norm_x, norm_y):
        # A tight deadband absorbs tiny camera/hand tremors. Larger movements
        # get a higher follow factor, keeping the pointer responsive at speed.
        m = self.active_margin
        x = (float(norm_x) - m) / max(1e-6, 1.0 - 2.0 * m)
        y = (float(norm_y) - m) / max(1e-6, 1.0 - 2.0 * m)
        x = 0.5 + (x - 0.5) * self.cursor_sensitivity
        y = 0.5 + (y - 0.5) * self.cursor_sensitivity
        target = np.array([
            np.clip(x, 0.0, 1.0) * (self.screen_w - 1),
            np.clip(y, 0.0, 1.0) * (self.screen_h - 1),
        ], dtype=float)

        if self._cursor is None:
            self._cursor = target
        else:
            delta = target - self._cursor
            distance = float(np.linalg.norm(delta))
            if distance < 3.0:
                return
            speed_factor = min(1.0, distance / 65.0)
            alpha = float(np.clip(self.smoothing * (0.22 + 0.78 * speed_factor), 0.16, 0.96))
            self._cursor += alpha * delta
        pyautogui.moveTo(int(self._cursor[0]), int(self._cursor[1]), duration=0)

    def _perform_click(self, double=False):
        now = time.monotonic()
        if not self._click_armed or now - self._last_click < self.click_cooldown:
            return False
        if double:
            pyautogui.doubleClick(interval=0.12)
        else:
            pyautogui.click()
        self._last_click = now
        self._click_armed = False
        return True

    def click_once(self):
        return self._perform_click(double=False)

    def double_click_once(self):
        return self._perform_click(double=True)

    def reset_click_gesture(self):
        self._click_armed = True

    def reset_scroll_filter(self):
        self._scroll_anchor = None
        self._scroll_velocity = 0.0
        self._scroll_residual = 0.0

    def scroll_delta(self, anchor_y):
        # Smooth the anchor and accumulate fractional wheel movement so small
        # movements don't get lost and large movements don't create huge jumps.
        now = time.monotonic()
        y = float(anchor_y)
        if self._scroll_anchor is None:
            self._scroll_anchor = y
            return
        delta = self._scroll_anchor - y
        self._scroll_anchor = y
        self._scroll_velocity = 0.72 * self._scroll_velocity + 0.28 * delta
        if now - self._last_scroll_time < 0.016:
            self._scroll_residual += self._scroll_velocity * self.scroll_speed
            return
        self._scroll_residual += self._scroll_velocity * self.scroll_speed
        amount = int(np.clip(self._scroll_residual, -5, 5))
        if amount:
            pyautogui.scroll(amount)
            self._scroll_residual -= amount
            self._last_scroll_time = now
