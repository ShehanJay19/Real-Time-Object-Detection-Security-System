import cv2 

def start_camera():
    # On Windows, CAP_DSHOW often opens webcams more reliably.
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam. Check if another app is using it.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()