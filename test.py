from pathlib import Path
from ultralytics import YOLO
import cv2

# Current folder where test.py is located
BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "best.pt"
IMAGE_PATH = BASE_DIR / "test.png"
OUTPUT_PATH = BASE_DIR / "result.png"

# Load YOLO model
model = YOLO(str(MODEL_PATH))

# Run detection
results = model.predict(
    source=str(IMAGE_PATH),
    conf=0.25,
    save=False
)

result = results[0]

# Draw detections
annotated_image = result.plot()

# Save result
cv2.imwrite(str(OUTPUT_PATH), annotated_image)

# Print detection results
print("\n=== Detection Results ===")

if result.boxes is None or len(result.boxes) == 0:
    print("No objects detected.")
else:
    names = model.names

    for box in result.boxes:
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = names[cls_id]
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        print(
            f"{class_name:25s} "
            f"confidence={confidence:.2f} "
            f"box=({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})"
        )

print(f"\nResult saved to: {OUTPUT_PATH}")