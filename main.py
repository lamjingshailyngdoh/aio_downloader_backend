from fastapi import FastAPI, Depends, HTTPException, Header
import os

app = FastAPI()

# Load API_KEY from environment variables
API_KEY = os.getenv("API_KEY", "default-secret")

# Function to verify API key in requests
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

@app.get("/protected-route")
async def protected_endpoint(auth: bool = Depends(verify_api_key)):
    return {"message": "Access granted!"}

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}
