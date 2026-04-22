from fastapi import FastAPI
import uvicorn


# Instantiate the API backend
app: FastAPI = FastAPI()

# Route definitions


@app.get("/")
def root():
    """
    Define the index page route
    """
    return {"message": "Hello World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
