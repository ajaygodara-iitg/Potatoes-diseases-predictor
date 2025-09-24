from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class FarmerResponse(Base):
    __tablename__ = "farmer_responses"

    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
