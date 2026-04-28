from ultralytics import YOLO

model = YOLO("yolov8m.pt")

def detect_objects(frame):
    results = model(frame)
    
    detected = []
    
    for r in results:
        for box in r.boxes:
            cls =int(box.cls[0])
            label = model.names[cls]
            confidence = float(box.conf[0])
            detected.append((label, confidence))
    return results, detected