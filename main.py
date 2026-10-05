import cv2
import time
from detector import RogueDetector
from scrcpy_window import ScrcpyWindow
from controller import RogueController
from agent import RogueAgent

# Các nút hệ thống tự động tap ngay khi thấy
AUTO_TAP_BUTTONS = {"StartButton", "Back", "Confirm"}

# Các thẻ kỹ năng thường gửi sang Ollama
REGULAR_SKILLS = {
    "Beam", "Bullet", "Dart", "Drone", "Electro", 
    "EliteAd", "Field", "FireWheel", "FlameMissle", 
    "Laser", "Mortar", "Thunder", "Traction"
}


class RogueAgentApp:

    def __init__(self):
        # 1. Khởi tạo Scrcpy Window Handler
        self.window_handler = ScrcpyWindow(
            window_title="Pixel 6a", auto_start=True
        )

        # 2. Khởi tạo YOLO Detector
        self.detector = RogueDetector(
            model_filename="best.pt", conf_threshold=0.25
        )

        # 3. Khởi tạo ADB Controller
        self.controller = RogueController()

        # 4. Khởi tạo Rogue AI Agent (Ollama)
        self.agent = RogueAgent(model_name="qwen2.5-coder")

        self.last_action_time = 0
        self.action_cooldown = 1.0  # Khoảng thời gian nghỉ giữa các lần tap chung (giây)

    def draw_detections(self, frame, valid_detections):
        """Vẽ bounding box và label lên frame hiển thị (Bỏ qua class X)."""
        for obj in valid_detections:
            class_name = obj["class"]
            
            # Bỏ qua không vẽ class X
            if class_name == "X":
                continue

            x1, y1, x2, y2 = map(int, obj["bbox"])
            cx, cy = map(int, obj["center"])
            conf = obj["confidence"]

            color = (0, 255, 0) if class_name in AUTO_TAP_BUTTONS else (255, 165, 0)

            # Bounding box & Center point
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            # Label
            label = f"{class_name} {conf:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        return frame

    def run(self):
        print("[MAIN] Rogue Agent đang vận hành... Nhấn 'q' để thoát.\n")

        try:
            while True:
                # Frame gốc từ Scrcpy
                frame = self.window_handler.get_frame()
                if frame is None:
                    continue

                frame_h, frame_w = frame.shape[:2]

                # Detect đối tượng bằng YOLO
                _, valid_detections, _ = self.detector.process_frame(frame)

                # BỎ QUA CLASS "X" HOÀN TOÀN TRONG LUỒNG XỬ LÝ
                valid_detections = [obj for obj in valid_detections if obj["class"] != "X"]

                current_time = time.time()

                if current_time - self.last_action_time >= self.action_cooldown and valid_detections:
                    
                    # -------------------------------------------------------------
                    # BƯỚC 1: Ưu tiên Nút hệ thống (StartButton, Back, Confirm)
                    # -------------------------------------------------------------
                    auto_buttons = [obj for obj in valid_detections if obj["class"] in AUTO_TAP_BUTTONS]

                    if auto_buttons:
                        target = auto_buttons[0]
                        cx, cy = target["center"]
                        print(f"[ACTION] 🎯 Tap nút hệ thống: '{target['class']}' tại ({cx}, {cy})")
                        
                        self.controller.tap_scaled(cx, cy, frame_w, frame_h)
                        self.last_action_time = time.time()

                    else:
                        # -------------------------------------------------------------
                        # BƯỚC 2: Ưu tiên chọn ElitePick nếu xuất hiện
                        # -------------------------------------------------------------
                        elite_picks = [obj for obj in valid_detections if obj["class"] == "ElitePick"]

                        if elite_picks:
                            target = elite_picks[0]
                            cx, cy = target["center"]
                            print(f"[ACTION] ⭐ Phát hiện ElitePick -> Tap tại ({cx}, {cy})")
                            
                            # Thực hiện tap ElitePick
                            self.controller.tap_scaled(cx, cy, frame_w, frame_h)
                            
                            # 🛑 ÉP CHƯƠNG TRÌNH PAUSE ĐÚNG 1 GIÂY NGAY LẬP TỨC
                            print("[ACTION ⏸️] Đang tạm dừng 1 giây sau khi bấm ElitePick...")
                            time.sleep(1.0)
                            
                            # Cập nhật mốc thời gian hành động mới nhất sau khi đã ngủ xong 1 giây
                            self.last_action_time = time.time()

                        # -------------------------------------------------------------
                        # BƯỚC 3: Chọn kỹ năng thường (Chỉ khi ĐỦ ĐÚNG 3 kỹ năng)
                        # -------------------------------------------------------------
                        else:
                            detected_skills = [obj for obj in valid_detections if obj["class"] in REGULAR_SKILLS]

                            if len(detected_skills) == 3:
                                # Sắp xếp thẻ theo tọa độ Y từ trên xuống dưới
                                detected_skills = sorted(detected_skills, key=lambda s: s["center"][1])

                                # Gán thuộc tính 'index' (0, 1, 2) khớp với thứ tự hiển thị
                                for idx, item in enumerate(detected_skills):
                                    item["index"] = idx

                                skill_names = [s["class"] for s in detected_skills]
                                print(f"[ACTION] 🃏 Phát hiện 3 kỹ năng: {skill_names}")
                                
                                # Gửi danh sách đã gắn index sang Agent
                                chosen_skill = self.agent.choose_skill(detected_skills)
                                
                                if chosen_skill:
                                    cx, cy = chosen_skill["center"]
                                    chosen_idx = chosen_skill.get("index", -1)
                                    print(f"[ACTION] 🤖 Tap thẻ '{chosen_skill['class']}' (Index {chosen_idx}) tại tọa độ ({cx}, {cy})")
                                    
                                    self.controller.tap_scaled(cx, cy, frame_w, frame_h)
                                    self.last_action_time = time.time()
                            
                            elif len(detected_skills) > 0:
                                print(f"[WAIT] Đã thấy {len(detected_skills)}/3 kỹ năng thường. Đang chờ đủ 3...")

                # Hiển thị GUI xem trực tiếp
                display_frame = self.draw_detections(frame.copy(), valid_detections)
                cv2.imshow("Rogue Agent Auto Player", display_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    app = RogueAgentApp()
    app.run()