import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

# ---------------------------------------------------------
# Environment Detection (Deployment vs Local Desktop)
# ---------------------------------------------------------
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
    print("Hardware detected: Raspberry Pi. Using PiCamera2.")
    
    # Initialize PiCamera globally so it doesn't restart on every request
    picam2 = Picamera2()
    # Lower resolution speeds up accumulateWeighted matrix math
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Hardware detected: Desktop. Falling back to OpenCV VideoCapture.")

# ---------------------------------------------------------
# 1. App Initialization & Configuration
# ---------------------------------------------------------
app = FastAPI(title="Lansing Building Products Analytics API")

# Enable CORS so Streamlit (running on a different port) can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 2. API Keys Retrieval
# ---------------------------------------------------------
load_dotenv()  # Retrieve API keys from .env file

OW_KEY = os.environ.get("OPENWEATHER_API_KEY")
CV_KEY = os.environ.get("VISION_API_KEY")
GENAI_KEY = os.environ.get("GENAI_API_KEY")
SQL_KEY = os.environ.get("CLOUD_SQL_KEY")


# ---------------------------------------------------------
# 3. Camera Processing Logic (Dual-Purpose + Motion Blur)
# ---------------------------------------------------------
def generate_motion_blur_frames():
    """
    Captures video, applies a motion blur effect using accumulateWeighted, 
    and yields the frames as a byte stream. Adapts to hardware context.
    """
    cap = None
    
    # 1. Grab the initial frame based on the hardware environment
    if PICAMERA_AVAILABLE:
        try:
            raw_frame = picam2.capture_array()
            # Fix the PiCamera2 RGB vs OpenCV BGR color channel swap
            frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"PiCamera Error: {e}")
            return
    else:
        cap = cv2.VideoCapture(0)
        # Match the Pi's resolution for testing accuracy
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ret, frame = cap.read()
        if not ret:
            print("Desktop Camera Error: Could not read webcam.")
            if cap:
                cap.release()
            return

    avg_frame = np.float32(frame)

    # 2. Main processing loop
    try:
        while True:
            # Capture the next frame depending on hardware
            if PICAMERA_AVAILABLE:
                raw_frame = picam2.capture_array()
                frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
            else:
                success, frame = cap.read()
                if not success:
                    break

            # Apply motion blur logic
            cv2.accumulateWeighted(frame, avg_frame, 0.2)
            blurred_frame = cv2.convertScaleAbs(avg_frame)

            # Encode and yield as a JPEG
            ret, buffer = cv2.imencode(".jpg", blurred_frame)
            if not ret:
                continue

            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
    except Exception as e:
        print(f"Stream interrupted: {e}")
    finally:
        # Clean up desktop camera if we used it
        if not PICAMERA_AVAILABLE and cap:
            cap.release()


# ---------------------------------------------------------
# 4. Route Definitions
# ---------------------------------------------------------
@app.get("/")
@app.get("/index")
async def root():
    """
    Define the index page route. Provides high-level project stats.
    """
    return {
        "message": "Hello World!",
        "project_name": "Measuring Foot Traffic at Lansing Building Products",
        "system_status": "Operational",
        "active_sensors": ["Camera-01", "Database"],
    }


@app.get("/camera")
async def camera():
    """
    Route serving the live motion-blurred camera feed
    """
    return StreamingResponse(
        generate_motion_blur_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/records")
async def records():
    """
    Route to retrieve database records
    """
    # Placeholder for database query results until SQL is connected
    data = [
        {"id": 101, "item": "Person Detected", "time": "12:01:22"},
        {"id": 102, "item": "Motion Detected", "time": "12:05:45"},
    ]
    return {"results": data}


if __name__ == "__main__":
    # Start the app with uvicorn web server
    uvicorn.run(app, host="0.0.0.0", port=8080)
