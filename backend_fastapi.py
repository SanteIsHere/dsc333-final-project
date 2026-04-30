import os
import cv2
import numpy as np
import sqlalchemy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import text
from dotenv import load_dotenv

# Load API keys and DB credentials from .env file
load_dotenv()

app = FastAPI()

# Enable CORS for Streamlit communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECTION 1: CLOUD SQL CONNECTION (MySQL) ---
connector = Connector()


def getconn():
    # Uses Application Data/Service Account credentials
    conn = connector.connect(
        os.getenv("INSTANCE_CONNECTION_NAME"),  # project:region:instance
        "pymysql",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME"),
        ip_type=IPTypes.PUBLIC,
    )
    return conn


# Create the SQLAlchemy Engine
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# --- SECTION 2: CAMERA LOGIC (Hardware Detection & Motion Blur) ---
try:
    # Attempt to load Raspberry Pi specific hardware drivers
    from picamera2 import Picamera2

    camera_hardware = "Raspberry Pi"
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
except (ImportError, RuntimeError):
    # Fallback to standard USB webcams for desktop testing
    camera_hardware = "Desktop"
    cap = cv2.VideoCapture(0)


def generate_motion_blur_frames():
    """Generator for streaming blurred video frames."""
    avg = None
    while True:
        # Capture frame based on detected hardware
        if camera_hardware == "Raspberry Pi":
            raw_frame = picam2.capture_array()
            # Convert RGB (Pi) to BGR (OpenCV) to prevent color swapping
            frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
        else:
            success, frame = cap.read()
            if not success:
                break

        # Motion Blur Math (teammate's logic)
        frame_float = frame.astype("float")
        if avg is None:
            avg = frame_float
        else:
            cv2.accumulateWeighted(frame_float, avg, 0.1)

        blurred_frame = cv2.convertScaleAbs(avg)

        # Encode for HTTP streaming
        _, buffer = cv2.imencode(".jpg", blurred_frame)
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


# --- SECTION 3: API ROUTES ---


@app.get("/camera")
async def camera_feed():
    """Streams the motion-blurred video."""
    return StreamingResponse(
        generate_motion_blur_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/records")
async def get_records():
    """Queries Detections (Event Layer) and Revenue (Aggregate Layer)."""
    try:
        # async def prevents I/O blocking of the camera stream
        with pool.connect() as db_conn:
            # Query 1: Raw detection logs
            detection_query = text(
                "SELECT id, timestamp, temperature, weather_condition FROM detections ORDER BY timestamp DESC LIMIT 10"
            )
            detections_result = db_conn.execute(detection_query)

            # Query 2: Daily business metrics
            revenue_query = text(
                "SELECT date, total_revenue FROM daily_revenue ORDER BY date DESC LIMIT 7"
            )
            revenue_result = db_conn.execute(revenue_query)

            return {
                "detections": [dict(row._mapping) for row in detections_result],
                "revenue": [dict(row._mapping) for row in revenue_result],
                "status": "success",
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    # Bound to 0.0.0.0 for external access on port 8080
    print(f"Hardware detected: {camera_hardware}")
    uvicorn.run(app, host="0.0.0.0", port=8080)
