import json
import os
import sys
from ultralytics import YOLO

ALLOWED_CLASSES = {
    "Back", "Beam", "Bullet", "Chain", "Confirm", "Dart", 
    "Drone", "Electro", "EliteAd", "ElitePick", "Field", "FireWheel", 
    "FlameMissle", "Laser", "Mortar", "StartButton", "Thunder", "Traction", "X"
}


class RogueDetector:

    def __init__(self, model_filename="best.pt", conf_threshold=0.25):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(script_dir, model_filename)
        self.conf_threshold = conf_threshold

        if not os.path.exists(self.model_path):
            print(f"[LỖI DETECT] Không tìm thấy file model tại: {self.model_path}")
            sys.exit(1)

        print(f"[DETECT] Đang tải Rogue YOLO model từ: {self.model_path}")
        self.model = YOLO(self.model_path)

    def process_frame(self, frame):
        """Chạy YOLO detect, tính tọa độ tâm chuẩn xác [cx, cy]"""
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        valid_detections = []
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                conf = float(box.conf[0])

                if class_name not in ALLOWED_CLASSES or conf < self.conf_threshold:
                    continue

                # Lấy tọa độ bounding box chuẩn (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Tính tâm chính xác của Bounding Box
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0

                valid_detections.append(
                    {
                        "class": class_name,
                        "confidence": round(conf, 2),
                        "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                        "center": [round(cx, 1), round(cy, 1)],
                    }
                )

        output_data = {
            "total_objects": len(valid_detections),
            "objects": valid_detections,
        }

        json_output = json.dumps(output_data, ensure_ascii=False, indent=2)
        return results[0], valid_detections, json_output