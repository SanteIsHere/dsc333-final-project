# dsc333-final-project
Before running the application, provide the following variables in an environment file (`.env`)
  - DB_USER: String containing name of an authorized Cloud SQL instance user
  - DB_PASS: Password for the user
  - INSTANCE_CONNECTION_NAME: Name of the Google Cloud SQL instance
  - WEATHER_API_KEY: OpenWeather API key

Also make sure to download JSON credentials for the Cloud SQL API, export path of credentials to environment variable "GOOGLE_APPLICATION_CREDENTIALS".
