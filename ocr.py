import cv2
import pytesseract

class SkillOCR:
    def __init__(self, tesseract_cmd=None):
        """
        Khởi tạo OCR Engine.
        Nếu dùng Windows, bạn có thể truyền đường dẫn tesseract.exe:
        tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text_from_skill(self, frame, skill_object):
        """
        Cắt vùng ảnh dựa vào Bounding Box của Skill và chạy OCR.
        - Chiều cao: Bằng chiều cao của bound detect box (y1 -> y2)
        - Chiều dài: Bắt đầu từ x2 (cạnh phải box) tới hết màn hình (x_max)
        
        Trả về dict: {
            "class": <tên_class_skill>,
            "text": <nội_dung_ocr_được>
        }
        """
        frame_h, frame_w = frame.shape[:2]
        x1, y1, x2, y2 = map(int, skill_object["bbox"])
        class_name = skill_object["class"]

        # Cắt vùng ảnh từ cạnh phải box (x2) đến hết chiều dài màn hình (frame_w)
        crop_x1 = max(0, min(x2, frame_w - 1))
        crop_x2 = frame_w
        crop_y1 = max(0, min(y1, frame_h - 1))
        crop_y2 = max(0, min(y2, frame_h))

        # Kiểm tra nếu vùng crop hợp lệ
        if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
            return {"class": class_name, "text": ""}

        # Cắt Crop ROI
        roi = frame[crop_y1:crop_y2, crop_x1:crop_x2]

        # Tiền xử lý ảnh đơn giản để tăng độ chính xác OCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Binarization / Thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Chạy OCR lấy văn bản (ngôn ngữ Tiếng Anh + Tiếng Việt nếu cần, mặc định eng)
        try:
            text = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6').strip()
        except Exception as e:
            # Fallback nếu tesseract lỗi/chưa setup ngôn ngữ
            text = pytesseract.image_to_string(gray, config='--psm 6').strip()

        # Dọn dẹp khoảng trắng dư thừa
        clean_text = " ".join(text.split())

        return {
            "class": class_name,
            "text": clean_text
        }

    def process_all_skills(self, frame, skill_objects):
        """Hàm hỗ trợ OCR toàn bộ danh sách các skill được detect."""
        results = []
        for skill in skill_objects:
            res = self.extract_text_from_skill(frame, skill)
            results.append(res)
            print(f"[OCR] 📝 Skill: '{res['class']}' | Nội dung OCR: \"{res['text']}\"")
        return results