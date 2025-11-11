"""
FastAPI application for SmartRecruitAI Matching Engine
Provides high-performance API for matching operations
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys

# Add Django project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.services import NLPExtractor, VectorMatcher, RAGEngine, CVParser
from smartrecruitai.models import Candidate, JobOffer, Match

app = FastAPI(
    title="SmartRecruitAI Matching Engine",
    description="High-performance API for CV-Job matching with Deep Learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class CandidateInput(BaseModel):
    full_name: str
    email: str
    cv_text: str
    technical_skills: List[str] = []
    experience_years: float = 0.0


class JobOfferInput(BaseModel):
    title: str
    description: str
    requirements: str
    location: str


class MatchingRequest(BaseModel):
    candidate_id: Optional[int] = None
    job_offer_id: Optional[int] = None
    candidate_text: Optional[str] = None
    job_text: Optional[str] = None


class MatchResult(BaseModel):
    score: float
    explanation: str
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]


@app.get("/")
async def root():
    """API Health check"""
    return {
        "message": "SmartRecruitAI Matching Engine",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/match")
async def match_candidate_to_job(request: MatchingRequest) -> MatchResult:
    """
    Match a candidate to a job offer
    
    Args:
        request: Matching request with candidate and job identifiers or texts
        
    Returns:
        MatchResult with score and explanations
    """
    vector_matcher = VectorMatcher()
    
    # Get candidate
    if request.candidate_id:
        candidate = Candidate.objects.get(pk=request.candidate_id)
        candidate_text = candidate.cv_text
        candidate_data = {
            'technical_skills': candidate.technical_skills,
            'experience_years': candidate.total_experience_years,
            'education_level': candidate.education_level,
            'soft_skills': candidate.soft_skills,
        }
    else:
        candidate_text = request.candidate_text
        candidate_data = {'technical_skills': []}
    
    # Get job offer
    if request.job_offer_id:
        job_offer = JobOffer.objects.get(pk=request.job_offer_id)
        job_text = f"{job_offer.description} {job_offer.requirements}"
        job_data = {
            'required_skills': job_offer.required_skills,
            'required_experience_years': job_offer.required_experience_years,
        }
    else:
        job_text = request.job_text
        job_data = {'required_skills': []}
    
    # Calculate similarity
    similarity = vector_matcher.match_candidate_to_job(candidate_text, job_text)
    
    # Calculate detailed scores
    detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
    
    # Generate explanation
    rag_engine = RAGEngine()
    explanation = rag_engine.explain_match(candidate_data, job_data, detailed_scores)
    
    # Get strengths and gaps
    analysis = vector_matcher.generate_matching_explanation(candidate_data, job_data, detailed_scores)
    
    return MatchResult(
        score=similarity,
        explanation=explanation,
        strengths=analysis.get('strengths', []),
        gaps=analysis.get('gaps', []),
        recommendations=analysis.get('recommendations', [])
    )


@app.post("/api/extract-cv")
async def extract_cv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract information from a CV file
    
    Args:
        file: CV file (PDF or DOCX)
        
    Returns:
        Extracted CV data
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Parse CV
        cv_parser = CVParser()
        parsed_data = cv_parser.parse_file(temp_path)
        
        # Extract structured data
        nlp_extractor = NLPExtractor()
        extracted_data = nlp_extractor.extract_cv_data(parsed_data['text'])
        
        # Generate embedding
        vector_matcher = VectorMatcher()
        embedding = vector_matcher.generate_embedding(parsed_data['text'])
        
        # Clean up
        os.remove(temp_path)
        
        return {
            'text': parsed_data['text'],
            'extracted_data': extracted_data,
            'embedding': embedding
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-job")
async def extract_job(job_input: JobOfferInput) -> Dict[str, Any]:
    """
    Extract requirements from a job description
    
    Args:
        job_input: Job offer information
        
    Returns:
        Extracted job requirements
    """
    nlp_extractor = NLPExtractor()
    extracted_data = nlp_extractor.extract_job_requirements(
        f"{job_input.description} {job_input.requirements}"
    )
    
    return {
        'extracted_requirements': extracted_data
    }


@app.post("/api/generate-embedding")
async def generate_embedding(text: str) -> Dict[str, Any]:
    """
    Generate embedding vector for a text
    
    Args:
        text: Input text
        
    Returns:
        Embedding vector
    """
    vector_matcher = VectorMatcher()
    embedding = vector_matcher.generate_embedding(text)
    
    return {
        'embedding': embedding,
        'dimension': len(embedding)
    }


@app.post("/api/answer-question")
async def answer_question(question: str, candidate_id: int) -> Dict[str, Any]:
    """
    Answer questions about a candidate using RAG
    
    Args:
        question: Question in natural language
        candidate_id: Candidate ID
        
    Returns:
        Answer to the question
    """
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
        
        candidate_data = {
            'technical_skills': candidate.technical_skills,
            'experience_years': candidate.total_experience_years,
            'education_level': candidate.education_level,
            'soft_skills': candidate.soft_skills,
            'availability': candidate.availability,
        }
        
        rag_engine = RAGEngine()
        answer = rag_engine.answer_question(question, candidate_data)
        
        return {
            'question': question,
            'answer': answer,
            'candidate': candidate.full_name
        }
    
    except Candidate.DoesNotExist:
        raise HTTPException(status_code=404, detail="Candidate not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

