
from database import engine, Base
from models import Analysis

Base.metadata.create_all(bind=engine)

print("ResumeMatch database and tables created successfully!")
