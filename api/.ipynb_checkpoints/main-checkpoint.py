from fastapi import FastAPI, File, UploadFile
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image

app = FastAPI()

@app.get("/ping")
async def ping():
    return "message": "Hello, I am alive"

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
    ):
    bytes = await file.read()
    
    pass

    #return {"message": "Predict working"}

if __name__ == "__main__":
    uvicorn.run(app, debug = True, host="localhost", port=8000)
