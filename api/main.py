from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import os
from dotenv import load_dotenv
import google.generativeai as genai
import markdown

# ----------------------------
# 1. Load Environment Variables & Configure Gemini
# ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or "AIzaSyDjvioK6SsJt-enjQAB5GXHvrNDFYHM0hj")

# ----------------------------
# 2. Initialize FastAPI App
# ----------------------------
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 3. Load TensorFlow Model
# ----------------------------
MODEL = tf.keras.models.load_model(r"C:\Users\godar\Downloads\Potato_disease_chat_bot\model\1.keras")
CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

# ----------------------------
# 4. Utility Functions
# ----------------------------
def read_file_as_image(data) -> np.ndarray:
    # Force RGB (avoids RGBA errors)
    image = Image.open(BytesIO(data)).convert("RGB")
    return np.array(image)


# ----------------------------
# 5. Gemini Analysis (Analysis Only)
# ----------------------------
async def get_gemini_analysis_only(disease_name: str):
    """
    Generates detailed analysis (causes, symptoms, treatments, preventive measures)
    without follow-up questions.
    """
    prompt = (
        f"You are an agricultural expert. Provide a detailed analysis of the potato disease '{disease_name}'. "
        f"Include causes, symptoms, treatments, and preventive measures. "
        f"Do NOT include follow-up questions in the response."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw_text = response.text or "No analysis available."

    return markdown.markdown(raw_text)

# ----------------------------
# 6. Gemini Follow-up Question (One at a Time)
# ----------------------------
class QuestionRequest(BaseModel):
    disease_name: str
    previous_answers: list[str]

@app.post("/next-question")
async def next_question(req: QuestionRequest):
    """
    Generate one new follow-up question based on previous farmer answers.
    """
    answers_text = "\n".join(
        [f"Answer {i+1}: {a}" for i, a in enumerate(req.previous_answers)]
    )

    prompt = (
        f"You are an agricultural expert helping a farmer diagnose '{req.disease_name}'.\n\n"
        f"Farmer's previous answers:\n{answers_text}\n\n"
        f"Ask ONE follow-up question that helps diagnose or advise better. "
        f"Do not repeat previous questions. Keep it short and specific."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    question = response.text.strip()

    return {"question": question}

# ----------------------------
# 7. Prediction Endpoint
# ----------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Classify uploaded potato leaf image and provide detailed analysis (no questions).
    """
    # 1. Read and preprocess image
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)

    # 2. Predict class
    predictions = MODEL.predict(img_batch)
    index = np.argmax(predictions[0])
    predicted_class = CLASS_NAMES[index]
    confidence = np.max(predictions[0])

    # 3. Get analysis (no questions)
    analysis_html = await get_gemini_analysis_only(predicted_class)

    return {
        "class": predicted_class,
        "confidence": float(confidence),
        "analysis_html": analysis_html
    }

# ----------------------------
# 8. Farmer Response Recording
# ----------------------------
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, FarmerResponse

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Save farmer response to DB
@app.post("/farmer-response")
async def record_farmer_response(
    response_text: str = Form(...),
    disease_name: str = Form("Unknown"),
    question_text: str = Form(""),
    db: Session = Depends(get_db)
):
    new_response = FarmerResponse(
        disease_name=disease_name,
        question=question_text,
        answer=response_text
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    return {"status": "success", "message": "Response saved to DB", "id": new_response.id}

# 9. NEW: View all responses (debug)
# ----------------------------
@app.get("/responses")
def view_responses(db: Session = Depends(get_db)):
    """
    Simple endpoint to view all farmer responses (for debugging only).
    """
    responses = db.query(FarmerResponse).all()
    return [
        {
            "id": r.id,
            "disease_name": r.disease_name,
            "question": r.question,
            "answer": r.answer,
            "timestamp": r.timestamp
        }
        for r in responses
    ]

class SummaryRequest(BaseModel):
    disease_name: str
    previous_answers: list[str]

@app.post("/summary")
async def summary(req: SummaryRequest):
    """
    Generate final summary/recommendations using all farmer responses.
    """
    answers_text = "\n".join([f"{i+1}. {a}" for i, a in enumerate(req.previous_answers, 1)])

    prompt = (
        f"You are an agricultural expert. Based on the following farmer responses about the disease '{req.disease_name}':\n"
        f"{answers_text}\n\n"
        f"Provide a concise summary of the farmer's situation and specific actionable recommendations for managing this disease."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw_text = response.text or "No recommendations available."

    return {"summary_html": markdown.markdown(raw_text)}

# ----------------------------
# 9. Health Check Endpoint
# ----------------------------
@app.get("/ping")
async def ping():
    return "I am alive"

# ----------------------------
# 10. Run Server
# ----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
