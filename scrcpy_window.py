import subprocess
import sys
import time
import cv2
import numpy as np
import pygetwindow as gw
from mss import mss


class ScrcpyWindow:

    def __init__(self, window_title="Pixel 6a", auto_start=True):
        self.window_title = window_title
        self.sct = mss()
        self.window = None

        if auto_start:
            self._ensure_scrcpy_running()

    def _ensure_scrcpy_running(self):
        """Kiểm tra cửa sổ scrcpy, nếu chưa có thì tự chạy scrcpy qua CMD"""
        windows = gw.getWindowsWithTitle(self.window_title)
        if not windows:
            print(
                f"[WINDOW] Chưa thấy cửa sổ '{self.window_title}'. Đang khởi chạy lệnh 'scrcpy'..."
            )
            try:
                subprocess.Popen(["scrcpy"], shell=True)
                time.sleep(3)
                windows = gw.getWindowsWithTitle(self.window_title)
            except Exception as e:
                print(f"[LỖI WINDOW] Không thể tự động chạy scrcpy: {e}")

        if windows:
            self.window = windows[0]
            print(f"[WINDOW] Đã kết nối với cửa sổ: {self.window.title}")
        else:
            print(f"[LỖI WINDOW] Không tìm thấy cửa sổ '{self.window_title}'!")
            sys.exit(1)

    def get_frame(self):
        """Lấy frame BGR từ cửa sổ Scrcpy"""
        if not self.window or self.window.isMinimized:
            return None

        bbox = {
            "top": max(0, self.window.top),
            "left": max(0, self.window.left),
            "width": self.window.width,
            "height": self.window.height,
        }

        if bbox["width"] <= 0 or bbox["height"] <= 0:
            return None

        sct_img = self.sct.grab(bbox)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame