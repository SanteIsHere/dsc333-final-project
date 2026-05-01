import os
import cv2
import time
import httpx
import datetime
import threading
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud.sql.connector import Connector
import sqlalchemy
from dotenv import load_dotenv

# Load environment variables (DB_USER, DB_PASS, INSTANCE_CONNECTION_NAME, WEATHER_API_KEY)
load_dotenv()

app = FastAPI()

# Enable CORS for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Cloud SQL Setup ---
connector = Connector()

def getconn():
    return connector.connect(
        os.getenv("INSTANCE_CONNECTION_NAME"),
        "pymysql",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db="lansing_data"
    )

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# --- 2. Hardware-Agnostic Camera Setup ---
try:
    from picamera2 import Picamera2
    camera = Picamera2()
    # Moderate resolution to ensure smooth frame rate during float math
    camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
    camera.start()
    USE_PICAMERA = True
    print("Hardware detected: Raspberry Pi. Using PiCamera2.")
except ModuleNotFoundError:
    camera = cv2.VideoCapture(0)
    USE_PICAMERA = False
    print("Hardware detected: Desktop. Falling back to OpenCV VideoCapture.")


# --- 3. Synchronous Database Writing Logic ---
def fetch_weather_data():
    """Fetches current weather synchronously so it can run in a background thread."""
    api_key = os.getenv("WEATHER_API_KEY")
    # Example coordinates for Lansing area
    url = f"https://api.openweathermap.org/data/2.5/weather?lat=42.7325&lon=-84.5555&appid={api_key}&units=imperial"
    
    try:
        response = httpx.get(url)
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "condition": data["weather"][0]["description"]
        }
    except Exception as e:
        print(f"Weather API failed: {e}")
        return {"temp": 0.0, "condition": "Unknown"}

def log_motion_detection():
    """The Event Layer: Fetches weather and securely writes to Cloud SQL."""
    current_weather = fetch_weather_data()
    
    try:
        with pool.connect() as db_conn:
            insert_query = sqlalchemy.text("""
                INSERT INTO detections (timestamp, temperature, weather_condition)
                VALUES (:timestamp, :temp, :condition)
            """)
            
            db_conn.execute(insert_query, {
                "timestamp": datetime.datetime.now(),
                "temp": current_weather['temp'],
                "condition": current_weather['condition']
            })
            db_conn.commit()
            print("Motion detection logged securely to Cloud SQL.")
    except Exception as e:
        print(f"Database write failed: {e}")


# --- 4. Motion Blur Generator with Time-Based Cooldown ---
def generate_motion_blur_frames():
    avg = None
    last_detection_time = 0.0
    COOLDOWN_SECONDS = 60.0  # Wait 60 seconds before logging another person
    
    while True:
        if USE_PICAMERA:
            # Capture array and convert RGB to BGR for OpenCV
            raw_frame = camera.capture_array()
            frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
        else:
            success, frame = camera.read()
            if not success:
                break
                
        # Motion blur logic
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if avg is None:
            avg = gray.copy().astype("float")
            continue
            
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        
        # Simple threshold to trigger the database write (Adjust value as needed)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_detected = cv2.countNonZero(thresh) > 5000 
        
        # Time-Based Cooldown Logic
        current_time = time.time()
        if motion_detected and (current_time - last_detection_time) > COOLDOWN_SECONDS:
            # FIRE AND FORGET: Start the DB write in an isolated thread immediately
            threading.Thread(target=log_motion_detection).start()
            
            last_detection_time = current_time
            print(f"Motion detected! Cooldown activated for {COOLDOWN_SECONDS} seconds.")
        
        # --- PRIVACY BLUR COMPOSITING ---
        
        # 1. Dilate (expand) the threshold mask slightly so the blur fully covers the person's edges
        mask = cv2.dilate(thresh, None, iterations=5)
        
        # 2. Create a completely out-of-focus version of the live color frame
        blurred_live_frame = cv2.GaussianBlur(frame, (99, 99), 0)
        
        # 3. Paste the blurred pixels onto the clear frame ONLY where motion is detected
        frame[mask > 0] = blurred_live_frame[mask > 0]
        
        # Encode the newly composited color frame to MJPEG format for Streamlit
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- 5. API Routes ---
@app.get("/camera")
async def video_stream():
    """Streams the motion blur generator securely, without blocking backend requests"""
    return StreamingResponse(generate_motion_blur_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/records")
async def get_records():
    """Fetches records securely from the Cloud SQL database"""
    with pool.connect() as db_conn:
        query = sqlalchemy.text("""
            SELECT id, timestamp, temperature, weather_condition 
            FROM detections 
            ORDER BY timestamp DESC LIMIT 50
        """)
        result = db_conn.execute(query).fetchall()
        
    if not result:
        return [{"id": "N/A", "timestamp": "No Data", "temperature": "N/A", "weather_condition": "N/A"}]
        
    return [row._mapping for row in result]
