# SmartRecruitAI - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Activate Virtual Environment
```bash
cd "D:\jesser\deep learning project"
envDL\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 4: Run the Application
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: FastAPI server (optional)
python fastapi_matching.py
```

### Step 5: Access the Application
- Django Admin: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/
- FastAPI: http://localhost:8001/docs

## 📖 Basic Usage

### 1. Create a Job Offer

Go to Django Admin or use API:
```bash
POST http://localhost:8000/api/job-offers/
{
  "title": "Data Scientist Senior",
  "description": "We are looking for an experienced data scientist...",
  "requirements": "5+ years of experience in machine learning...",
  "location": "Paris, France",
  "job_type": "full-time",
  "required_skills": ["Python", "TensorFlow", "Machine Learning"],
  "required_experience_years": 5
}
```

### 2. Process Job Requirements

```bash
POST http://localhost:8000/api/job-offers/1/process_requirements/
```

This will:
- Extract technical requirements using NLP
- Generate embeddings with Sentence-BERT
- Store extracted data

### 3. Upload a CV

```bash
POST http://localhost:8000/api/candidates/1/upload_cv/
Content-Type: multipart/form-data
file: cv.pdf
```

This will:
- Extract text from CV (PDF/DOCX)
- Parse with NLP to extract skills, experience, education
- Generate semantic embeddings
- Store in database

### 4. Find Matches

```bash
POST http://localhost:8000/api/job-offers/1/find_matches/
```

This will:
- Match all candidates to the job offer
- Calculate similarity scores
- Generate detailed explanations
- Identify strengths and gaps

### 5. Get Match Explanation

```bash
GET http://localhost:8000/api/matches/1/explanation/
```

### 6. Generate Email

```bash
POST http://localhost:8000/api/matches/1/generate_email/
```

## 🧪 Example Data

### Sample Candidate
```json
{
  "full_name": "Alice Dupont",
  "email": "alice@example.com",
  "technical_skills": ["Python", "TensorFlow", "Machine Learning"],
  "total_experience_years": 5.0,
  "education_level": "Master",
  "soft_skills": ["Leadership", "Communication"]
}
```

### Sample Job Offer
```json
{
  "title": "Data Scientist Senior",
  "description": "Leading ML team in NLP projects",
  "location": "Paris",
  "required_skills": ["Python", "TensorFlow", "Deep Learning"],
  "required_experience_years": 5
}
```

## 🔍 Management Commands

### Process all pending CVs
```bash
python manage.py process_cvs
```

### Process specific CV
```bash
python manage.py process_cvs --cv-id 123
```

### Match all candidates to all jobs
```bash
python manage.py match_all_jobs
```

### Match to specific job
```bash
python manage.py match_all_jobs --job-id 456
```

## 📊 API Endpoints

### Candidates
- `GET /api/candidates/` - List candidates
- `POST /api/candidates/` - Create candidate
- `GET /api/candidates/{id}/` - Get candidate
- `POST /api/candidates/{id}/upload_cv/` - Upload CV
- `GET /api/candidates/{id}/matches/` - Get matches

### Job Offers
- `GET /api/job-offers/` - List job offers
- `POST /api/job-offers/` - Create job offer
- `POST /api/job-offers/{id}/process_requirements/` - Extract requirements
- `POST /api/job-offers/{id}/find_matches/` - Find matching candidates

### Matches
- `GET /api/matches/` - List all matches
- `GET /api/matches/{id}/explanation/` - Get explanation
- `POST /api/matches/{id}/generate_summary/` - Generate summary
- `POST /api/matches/{id}/generate_email/` - Generate email

## 🤖 Advanced Features

### Conversational Assistant
```bash
POST /api/conversations/1/ask/
{
  "question": "Does this candidate have experience in NLP?"
}
```

### Batch Processing with Management Commands
```bash
# Process all CVs and match to all jobs
python manage.py process_cvs
python manage.py match_all_jobs
```

## 🔧 Configuration

Edit `CV_match/settings.py`:
- Elasticsearch settings
- S3 storage configuration
- Matching weights
- RAG model configuration

## ⚠️ Troubleshooting

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Error: spaCy model not found
```bash
python -m spacy download fr_core_news_sm
```

### Error: Database errors
```bash
python manage.py migrate
```

### Error: Elasticsearch connection
Make sure Elasticsearch is running on localhost:9200

## 📚 Next Steps

1. Upload sample CVs and job offers
2. Explore the Django admin interface
3. Test the API endpoints
4. Run matching and view results
5. Generate explanations and summaries

## 🎉 You're All Set!

Start exploring SmartRecruitAI and revolutionize your recruitment process!

For more information, see `README.md`

