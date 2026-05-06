# dsc333-final-project
Before running the application, provide the following variables in an environment file (`.env`)
  - DB_USER: String containing name of an authorized Cloud SQL instance user
  - DB_PASS: Password for the user
  - INSTANCE_CONNECTION_NAME: Name of the Google Cloud SQL instance
  - WEATHER_API_KEY: OpenWeather API key
  - PI_IPADDR: Local IP for Raspberry Pi 

Authenticate GCloud via GCloud CLI app: https://docs.cloud.google.com/sdk/docs/install-sdk


Steps to authenticate:
1. gcloud auth login (Get the CLI working).

2. gcloud config set project [PROJECT_ID] (Tell it which project to use).

3. gcloud auth application-default login (Let your Python code talk to GCP).

Ensure the following packages are installed (if running on Raspberry Pi):
```
sudo apt update && sudo apt install -y \
    libcamera-dev \
    libcap-dev \
    python3-picamera2 \
    python3-opencv \
    libopencv-dev \
    python3-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config
```

Create a virtual environment - with the `--system-site-packages` option if running on a Pi - and install the required packages.
