from ultralytics import YOLO

model = YOLO("yolov8m.pt")

def detect_objects(frame):
    results = model(frame)
    return results