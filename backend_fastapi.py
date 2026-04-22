from fastapi import FastAPI  # Define routes
from dotenv import load_dotenv  # Get API keys from environment
import uvicorn  # Web server
import os

# Instantiate the API backend
app: FastAPI = FastAPI()


############
# API keys #
############

load_dotenv()  # Retrieve API keys

OW_KEY = os.environ.get("OPENWEATHER_API_KEY")
CV_KEY = os.environ.get("VISION_API_KEY")
GENAI_KEY = os.environ.get("GENAI_API_KEY")
SQL_KEY = os.environ.get("CLOUD_SQL_KEY")


#####################
# Route definitions #
#####################


@app.get("/")
def root():
    """
    Define the index page route
    """
    return {"message": "Hello World!"}


@app.get("/camera")
def camera():
    """
    Route serving the live camera feed
    """
    pass


@app.get("/records")
def records():
    """
    Route to retrieve database records
    """
    pass


if __name__ == "__main__":
    # Start the app with uvicorn web server
    uvicorn.run(app, host="0.0.0.0", port=8080)
