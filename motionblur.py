from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import cv2
import time
import datetime
import json
import os

app = FastAPI()

# Open default webcam
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Load the pre-trained Haar Cascade for face detection
# If this path doesn't work, you may need to provide the full path to the xml file
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variables for motion detection
prev_frame = None
last_recorded_time = 0
RECORD_COOLDOWN = 2 

def get_frame():
    success, frame = camera.read()
    if not success:
        return None
    return frame

def apply_privacy_blur(frame):
    """Detects faces and applies a heavy blur to those regions."""
    gray_for_detect = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detectMultiScale: scaleFactor and minNeighbors balance speed vs accuracy
    faces = face_cascade.detectMultiScale(gray_for_detect, 1.1, 4)
    
    for (x, y, w, h) in faces:
        # Extract the face region
        roi = frame[y:y+h, x:x+w]
        # Apply a heavy Gaussian Blur
        roi = cv2.GaussianBlur(roi, (99, 99), 30)
        # Put the blurred face back into the main frame
        frame[y:y+h, x:x+w] = roi
    return frame

def generate_frames():
    global prev_frame, last_recorded_time
    while True:
        frame = get_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        #  Privacy Blur 
        
        frame = apply_privacy_blur(frame)

        # --- STEP 2: Motion Detection Logic ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_frame is None:
            prev_frame = gray
            continue

        frame_delta = cv2.absdiff(prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:
                motion_detected = True
                if area > max_area:
                    max_area = area

        current_time = time.time()
        if motion_detected and (current_time - last_recorded_time > RECORD_COOLDOWN):
            last_recorded_time = current_time
            now = datetime.datetime.now()
            file_name = f"motion_{now.strftime('%Y%m%d_%H%M%S')}.jpg"

            motion_data = {
                "event": "motion_detected",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "file_name": file_name,
                "stats": {"magnitude": int(max_area)}
            }
            
            # Save blurred frame and print JSON for MySQL
            cv2.imwrite(file_name, frame)
            print(json.dumps(motion_data))

        prev_frame = gray

        # --- STEP 3: Encode for Web ---
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )

# ... (Keep index, video, and snapshot endpoints the same) ...

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head><title>Secure Pi Stream</title></head>
        <body style="background:#222; color:white; text-align:center;">
            <h1>Motion Detection + Privacy Blur</h1>
            <img src="/video" width="800" />
        </body>
    </html>
    """

@app.get("/video")
def video():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/snapshot")
def snapshot():
    frame = get_frame()
    if frame is None: raise HTTPException(status_code=500)
    # Apply blur to snapshot too
    frame = apply_privacy_blur(frame)
    ok, buffer = cv2.imencode(".jpg", frame)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")
