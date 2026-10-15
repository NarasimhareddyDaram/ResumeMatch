
from sqlalchemy import Column, Integer, Float, String, Text
from database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_text = Column(Text, nullable=False)
    job_description = Column(Text, nullable=False)
    match_score = Column(Float, nullable=False)
    matched_skills = Column(String, nullable=False)
    missing_skills = Column(String, nullable=False)
