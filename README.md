# ResumeMatch — Resume Analyzer & Job Matcher

ResumeMatch is a full-stack web application that helps job seekers compare their resumes against job descriptions. It identifies matching and missing skills, calculates a rule-based match score, and provides recommendations to improve resume alignment.

## Features

- **PDF Resume Upload:** Upload a resume in PDF format.
- **Resume Text Extraction:** Extract text from uploaded resumes.
- **Job Description Matching:** Compare resume content with target job requirements.
- **Match Score:** View a score calculated using the implemented matching logic.
- **Skill Analysis:** Identify matched and missing skills.
- **Recommendations:** Get suggestions to improve alignment with a target role.
- **Analysis History:** Save and review previous analyses.
- **Search History:** Search saved analyses.
- **Detailed Results:** View saved resume and job description details.
- **Download Reports:** Download analysis results as text files.
- **Delete Records:** Remove saved analyses.

## Technology Stack

### Frontend
- React
- JavaScript
- CSS
- Vite

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn

### Database and Processing
- SQLite
- SQLAlchemy
- pypdf

## How It Works

1. Upload a resume PDF.
2. Enter the target job description.
3. Run the analysis.
4. Review the match score, matched skills, missing skills, and recommendations.
5. Save and revisit previous analyses through the history section.
6. Download a report or delete a saved analysis when needed.

## Project Structure

```text
ResumeMatch/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── main.py
├── database.py
├── init_db.py
├── models.py
├── skill_matching.py
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Install the following before running the application:

- Python 3
- Node.js and npm
- Git (optional, for version control)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/ResumeMatch.git
cd ResumeMatch
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Set Up the Backend

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install fastapi uvicorn sqlalchemy pydantic pypdf python-multipart
```

Initialize the database if required by the project:

```powershell
python init_db.py
```

Start the backend server:

```powershell
python -m uvicorn main:app --reload
```

The API should be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Set Up the Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal, commonly `http://localhost:5173`.

## API Overview

The backend provides endpoints for resume analysis and saved analysis records.

Examples of implemented operations include:

- Submit a resume and job description for analysis.
- Retrieve a saved analysis by ID.
- Search saved analysis history.
- Delete a saved analysis.

For the exact available endpoints and request formats, run the backend and visit `/docs`.

## Matching Method

ResumeMatch currently uses **rule-based matching** to compare extracted resume text with job-description requirements. The score depends on the matching logic implemented in the application. It is intended as guidance and does not guarantee interview selection or recruitment success.

## Future Improvements

- Improve skill extraction and matching accuracy.
- Support additional resume file formats.
- Add visual analytics and downloadable PDF reports.
- Introduce user authentication and personalized history.
- Enhance recommendations for different job roles.

## Privacy and Security

- Do not commit personal resumes, private documents, environment files, or local database files.
- The `.gitignore` file excludes SQLite database files and other generated files.
- Review files before pushing changes to a public repository.

## Purpose

ResumeMatch was developed as a full-stack web development project to demonstrate frontend development, API integration, PDF text extraction, database operations, and rule-based resume matching.

## Author

Developed as a full-stack web development project using React, FastAPI, Python, and SQLite.
