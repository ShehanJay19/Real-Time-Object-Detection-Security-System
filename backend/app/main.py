from fastapi import FastAPI
from app.services.camera import start_camera
import threading

app= FastAPI()
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/start-camera")
def run_camera():
    thread=threading.Thread(target=start_camera)
    thread.start()
    return {"status": "Camera started"}