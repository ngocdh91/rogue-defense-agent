import subprocess

class RogueController:

    def __init__(self, device_serial=None):
        self.device_serial = device_serial
        self.screen_width, self.screen_height = self._get_device_screen_size()
        print(f"[ADB CONTROLLER] Độ phân giải màn hình điện thoại: {self.screen_width}x{self.screen_height}")

    def _get_device_screen_size(self):
        """Lấy độ phân giải thực tế của thiết bị Android qua ADB command (wm size)."""
        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(["shell", "wm", "size"])

        try:
            output = subprocess.check_output(cmd).decode("utf-8")
            # Chuỗi trả về có dạng: "Physical size: 1080x2400"
            size_str = output.split(":")[-1].strip()
            width, height = map(int, size_str.split("x"))
            return width, height
        except Exception as e:
            print(f"[ADB CONTROLLER ⚠️] Không lấy được wm size: {e}. Mặc định 1080x2400.")
            return 1080, 2400

    def tap_scaled(self, cx, cy, frame_w, frame_h):
        """
        Quy đổi tọa độ tâm từ frame OpenCV sang tọa độ thực tế trên thiết bị và tap qua ADB.
        - (cx, cy): Tọa độ tâm trên frame
        - (frame_w, frame_h): Độ phân giải của frame thu từ Scrcpy
        """
        if frame_w == 0 or frame_h == 0:
            return

        # Tính tỷ lệ quy đổi
        real_x = int((cx / frame_w) * self.screen_width)
        real_y = int((cy / frame_h) * self.screen_height)

        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(["shell", "input", "tap", str(real_x), str(real_y)])

        try:
            subprocess.run(cmd, check=True)
            print(f"[ADB TAP] 🎯 Tọa độ Frame: ({int(cx)}, {int(cy)}) -> Tọa độ Thực ADB: ({real_x}, {real_y})")
        except Exception as e:
            print(f"[ADB LỖI] Tap thất bại: {e}")