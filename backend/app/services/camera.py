from app.services.detector import detect_objects
import cv2 
from app.services.alerts import should_trigger_alert, trigger_alert
from app.services.database import save_log

def start_camera():
    # On Windows, CAP_DSHOW often opens webcams more reliably.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam. Check if another app is using it.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results, detected_objects = detect_objects(frame)
        labels =[obj[0] for obj in detected_objects]
        if should_trigger_alert(labels):
            trigger_alert(labels)
        for obj, conf in detected_objects:
            save_log(obj, conf)

        annotated_frame = results[0].plot()
        
        cv2.imshow("AI Detection", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()