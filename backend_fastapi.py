import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import httpx
import os

# ---------------------------------------------------------
# 1. App Initialization & Configuration
# ---------------------------------------------------------
app = FastAPI(title="Lansing Building Products Analytics API")

# Enable CORS so Streamlit (running on a different port) can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your Streamlit IP
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
# 3. Camera Processing Logic (Teammate's Motion Blur)
# ---------------------------------------------------------
def generate_motion_blur_frames():
    """
    Captures video from the camera, applies a motion blur effect using
    accumulateWeighted, and yields the frames as a byte stream.
    """
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        cap.release()
        return

    avg_frame = np.float32(frame)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Apply motion blur logic
            cv2.accumulateWeighted(frame, avg_frame, 0.2)
            blurred_frame = cv2.convertScaleAbs(avg_frame)

            # Encode the processed frame as a JPEG
            ret, buffer = cv2.imencode(".jpg", blurred_frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()

            # Yield the output in the multipart format expected by streaming protocols
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
    finally:
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
