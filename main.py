import re

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader

from database import SessionLocal, engine, Base
from models import Analysis


app = FastAPI(
    title="ResumeMatch — Resume Analyzer & Job Matcher",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)


# IT and non-IT skill dictionary
SKILLS = [
    # Programming
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "php", "ruby", "golang", "rust", "kotlin", "swift", "bash",
    "powershell", "programming", "data structures", "algorithms",
    "object oriented programming", "debugging", "rest api", "graphql",

    # Web development
    "html", "css", "react", "angular", "vue", "next.js", "node.js",
    "express.js", "django", "flask", "fastapi", "spring boot",
    "asp.net", "web development", "full stack", "frontend development",
    "backend development",

    # Databases and analytics
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "oracle",
    "sql server", "database management", "data analysis",
    "data analytics", "data cleaning", "data visualization",
    "excel", "advanced excel", "power bi", "tableau", "pandas",
    "numpy", "statistics", "reporting", "power query",

    # AI and data science
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "nlp", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "generative ai",
    "prompt engineering", "data science", "predictive analytics",

    # IT support
    "service desk", "help desk", "it support", "technical support",
    "desktop support", "customer support", "troubleshooting",
    "incident management", "problem management", "ticketing",
    "ticket management", "service request management", "password reset",
    "software installation", "hardware support", "printer support",
    "remote support", "user account management", "active directory",
    "group policy", "servicenow", "jira", "sla", "itil",
    "microsoft 365", "office 365", "microsoft office",

    # Operating systems and networking
    "windows", "windows server", "linux", "ubuntu", "macos",
    "networking", "computer networks", "tcp/ip", "dns", "dhcp",
    "vpn", "lan", "wan", "firewall", "router", "switching",
    "network troubleshooting", "wi-fi", "cybersecurity",
    "information security", "access control", "data backup",

    # Cloud, DevOps and testing
    "aws", "azure", "google cloud", "cloud computing", "docker",
    "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd",
    "linux administration", "manual testing", "automation testing",
    "software testing", "selenium", "pytest", "quality assurance",
    "test cases",

    # Electrical and electronics
    "electrical engineering", "electronics", "circuit design",
    "power systems", "electrical machines", "plc", "scada",
    "autocad", "matlab", "simulink", "embedded systems", "arduino",
    "microcontrollers", "iot", "robotics", "preventive maintenance",
    "calibration", "production planning", "process improvement",

    # Mechanical, civil and manufacturing
    "solidworks", "catia", "ansys", "revit", "civil engineering",
    "structural design", "construction management", "project planning",
    "manufacturing", "cad", "cam", "supply chain",
    "inventory management", "logistics", "warehouse management",
    "safety compliance",

    # Healthcare and pharmaceuticals
    "pharmacology", "pharmaceutics", "pharmaceutical analysis",
    "drug discovery", "clinical research", "clinical trials",
    "pharmacovigilance", "regulatory affairs",
    "good manufacturing practice", "gmp", "good laboratory practice",
    "glp", "quality control", "laboratory testing",
    "formulation development", "medical terminology", "patient care",
    "medical records", "healthcare administration",

    # Finance and banking
    "accounting", "bookkeeping", "financial analysis",
    "financial reporting", "budgeting", "forecasting",
    "accounts payable", "accounts receivable", "payroll",
    "taxation", "auditing", "banking operations", "risk management",
    "credit analysis", "reconciliation", "tally", "quickbooks",
    "financial modeling",

    # Sales, marketing and customer service
    "sales", "business development", "lead generation",
    "digital marketing", "seo", "social media marketing",
    "content marketing", "market research", "crm", "salesforce",
    "customer relationship management", "customer service",
    "client relationship management", "negotiation",
    "product demonstration", "customer retention",

    # HR and administration
    "human resources", "recruitment", "talent acquisition",
    "employee onboarding", "performance management", "administration",
    "office administration", "data entry", "documentation",
    "record keeping", "calendar management", "coordination",
    "vendor management", "operations management",

    # Professional skills
    "communication", "written communication", "verbal communication",
    "teamwork", "team collaboration", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability",
    "attention to detail", "multitasking", "decision making",
    "presentation skills", "organization", "conflict resolution",
    "interpersonal skills", "analytical skills", "customer handling",
    "training", "report writing", "english proficiency",
]


def contains_skill(text: str, skill: str) -> bool:
    """Check whether a complete skill term appears in the text."""
    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def split_skills(value: str) -> list:
    return [skill for skill in value.split(", ") if skill] if value else []


def create_recommendations(missing: list, score: float) -> list:
    recommendations = []

    if missing:
        recommendations.append(
            "Review these job requirements and develop relevant skills "
            "where appropriate: " + ", ".join(missing)
        )

    if score < 50:
        recommendations.append(
            "Tailor your resume to the job description and highlight "
            "relevant projects and experience you genuinely have."
        )
    elif score < 80:
        recommendations.append(
            "Strengthen the evidence for relevant skills by describing "
            "projects, responsibilities, and measurable results."
        )
    else:
        recommendations.append(
            "Review the job requirements and make sure your most relevant "
            "experience is easy to find."
        )

    recommendations.append(
        "Only list skills and experience that accurately reflect your abilities."
    )

    return recommendations


@app.get("/")
def home():
    return {
        "message": "Welcome to ResumeMatch!",
        "status": "running",
    }


# Analyze resume and save results
@app.post("/analyze")
def analyze_resume(data: AnalyzeRequest):
    resume = data.resume_text.strip()
    job = data.job_description.strip()

    if not resume:
        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty.",
        )

    if not job:
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    required = [
        skill for skill in SKILLS
        if contains_skill(job, skill)
    ]

    if not required:
        raise HTTPException(
            status_code=400,
            detail="No recognized skills found in the job description. "
                   "Please provide a more detailed job description.",
        )

    matched = [
        skill for skill in required
        if contains_skill(resume, skill)
    ]

    missing = [
        skill for skill in required
        if skill not in matched
    ]

    score = round(len(matched) / len(required) * 100, 2)
    recommendations = create_recommendations(missing, score)

    db = SessionLocal()
    try:
        analysis = Analysis(
            resume_text=resume,
            job_description=job,
            match_score=score,
            matched_skills=", ".join(matched),
            missing_skills=", ".join(missing),
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "id": analysis.id,
            "match_score": score,
            "total_required_skills": len(required),
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendations": recommendations,
            "message": "Analysis saved successfully!",
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save the analysis.",
        )
    finally:
        db.close()


# Search and view analysis history
@app.get("/analyses")
def get_analyses(search: str = ""):
    db = SessionLocal()
    try:
        query = db.query(Analysis)

        if search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                Analysis.resume_text.ilike(term)
                | Analysis.job_description.ilike(term)
            )

        analyses = query.order_by(Analysis.id.desc()).all()

        results = []
        for item in analyses:
            matched = split_skills(item.matched_skills)
            missing = split_skills(item.missing_skills)

            results.append({
                "id": item.id,
                "match_score": item.match_score,
                "matched_skills": matched,
                "missing_skills": missing,
                "recommendations": create_recommendations(
                    missing, item.match_score
                ),
            })

        return results

    finally:
        db.close()


# View one analysis by ID
@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int):
    db = SessionLocal()
    try:
        item = db.query(Analysis).filter(
            Analysis.id == analysis_id
        ).first()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found.",
            )

        matched = split_skills(item.matched_skills)
        missing = split_skills(item.missing_skills)

        return {
            "id": item.id,
            "resume_text": item.resume_text,
            "job_description": item.job_description,
            "match_score": item.match_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "recommendations": create_recommendations(
                missing, item.match_score
            ),
        }

    finally:
        db.close()


# Delete an analysis by ID
@app.delete("/analyses/{analysis_id}")
def delete_analysis(analysis_id: int):
    db = SessionLocal()
    try:
        item = db.query(Analysis).filter(
            Analysis.id == analysis_id
        ).first()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found.",
            )

        db.delete(item)
        db.commit()

        return {
            "message": "Analysis deleted successfully.",
            "id": analysis_id,
        }

    finally:
        db.close()


# Extract text from an uploaded PDF resume
@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    try:
        reader = PdfReader(file.file)

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in this PDF. "
                       "Scanned PDFs may require OCR.",
            )

        return {
            "filename": file.filename,
            "resume_text": text,
            "message": "PDF text extracted successfully.",
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please check the file.",
        )
    finally:
        file.file.close()
