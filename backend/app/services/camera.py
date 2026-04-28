from app.services.detector import detect_objects
import cv2 
from app.services.alerts import trigger_alert

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
        
        trigger_alert(detected_objects)
        annotated_frame = results[0].plot()
        
        cv2.imshow("AI Detection", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()