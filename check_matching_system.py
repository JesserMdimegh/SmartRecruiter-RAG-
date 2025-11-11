"""
Diagnostic script to check the matching system
Checks CV embeddings, job offer embeddings, and matching logic
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.models import Candidate, JobOffer, Match
from smartrecruitai.services.vector_matcher import VectorMatcher
from smartrecruitai.services.cv_parser import CVParser
import json

def check_candidates():
    """Check all candidates and their embeddings"""
    print("\n" + "="*60)
    print("CHECKING CANDIDATES")
    print("="*60)
    
    candidates = Candidate.objects.all()
    print(f"\nTotal candidates: {candidates.count()}")
    
    for candidate in candidates:
        print(f"\n--- Candidate ID: {candidate.id} ---")
        print(f"Name: {candidate.full_name}")
        print(f"Email: {candidate.email}")
        print(f"Status: {candidate.status}")
        print(f"Has CV text: {bool(candidate.cv_text)}")
        if candidate.cv_text:
            print(f"CV text length: {len(candidate.cv_text)} characters")
            print(f"CV text preview: {candidate.cv_text[:100]}...")
        
        print(f"Has embedding: {bool(candidate.embedding)}")
        if candidate.embedding:
            embedding = candidate.embedding
            if isinstance(embedding, list):
                print(f"Embedding type: list, length: {len(embedding)}")
                if len(embedding) > 0:
                    print(f"First few values: {embedding[:5]}")
                    # Check if it's a mock embedding (all 0.1)
                    if all(v == 0.1 for v in embedding):
                        print("WARNING: This appears to be a MOCK embedding (all 0.1)")
                    else:
                        print("OK: Embedding looks valid")
                else:
                    print("WARNING: Empty embedding list")
            else:
                print(f"WARNING: Embedding is not a list, type: {type(embedding)}")
        else:
            print("ERROR: NO EMBEDDING - This candidate cannot be matched!")
        
        print(f"Technical skills: {candidate.technical_skills}")
        print(f"Experience years: {candidate.total_experience_years}")

def check_job_offers():
    """Check all job offers and their embeddings"""
    print("\n" + "="*60)
    print("CHECKING JOB OFFERS")
    print("="*60)
    
    job_offers = JobOffer.objects.all()
    print(f"\nTotal job offers: {job_offers.count()}")
    
    for job in job_offers:
        print(f"\n--- Job Offer ID: {job.id} ---")
        print(f"Title: {job.title}")
        print(f"Status: {job.status}")
        print(f"Description length: {len(job.description)} characters")
        print(f"Requirements length: {len(job.requirements)} characters")
        
        print(f"Has embedding: {bool(job.embedding)}")
        if job.embedding:
            embedding = job.embedding
            if isinstance(embedding, list):
                print(f"Embedding type: list, length: {len(embedding)}")
                if len(embedding) > 0:
                    print(f"First few values: {embedding[:5]}")
                    # Check if it's a mock embedding
                    if all(v == 0.1 for v in embedding):
                        print("WARNING: This appears to be a MOCK embedding (all 0.1)")
                    else:
                        print("OK: Embedding looks valid")
                else:
                    print("WARNING: Empty embedding list")
            else:
                print(f"WARNING: Embedding is not a list, type: {type(embedding)}")
        else:
            print("ERROR: NO EMBEDDING - This job offer cannot be matched!")
        
        print(f"Required skills: {job.required_skills}")
        print(f"Required experience: {job.required_experience_years} years")

def check_vector_matcher():
    """Check if vector matcher is working properly"""
    print("\n" + "="*60)
    print("CHECKING VECTOR MATCHER")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
        print("OK: sentence-transformers is installed")
    except ImportError:
        print("ERROR: sentence-transformers is NOT installed - using mock embeddings")
        print("   Install with: pip install sentence-transformers")
    
    try:
        import numpy as np
        from scipy.spatial.distance import cosine
        print("OK: numpy and scipy are installed")
    except ImportError:
        print("ERROR: numpy/scipy are NOT installed - similarity calculation will be mock")
        print("   Install with: pip install numpy scipy")
    
    vector_matcher = VectorMatcher()
    
    # Test embedding generation
    test_text = "Python developer with 5 years experience in machine learning"
    print(f"\nTesting embedding generation with text: '{test_text}'")
    embedding = vector_matcher.generate_embedding(test_text)
    print(f"Generated embedding type: {type(embedding)}")
    if isinstance(embedding, list):
        print(f"Embedding length: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        if all(v == 0.1 for v in embedding):
            print("WARNING: Using mock embedding!")
        else:
            print("OK: Real embedding generated")
    
    # Test similarity calculation
    print(f"\nTesting similarity calculation...")
    text1 = "Python developer with machine learning experience"
    text2 = "Java developer with web development experience"
    text3 = "Python developer with machine learning and deep learning experience"
    
    emb1 = vector_matcher.generate_embedding(text1)
    emb2 = vector_matcher.generate_embedding(text2)
    emb3 = vector_matcher.generate_embedding(text3)
    
    sim_1_2 = vector_matcher.calculate_similarity(emb1, emb2)
    sim_1_3 = vector_matcher.calculate_similarity(emb1, emb3)
    
    print(f"Similarity (Python ML vs Java Web): {sim_1_2:.4f}")
    print(f"Similarity (Python ML vs Python ML+DL): {sim_1_3:.4f}")
    
    if sim_1_3 > sim_1_2:
        print("OK: Similarity calculation is working correctly")
    else:
        print("WARNING: Similarity calculation might not be working correctly")

def check_matches():
    """Check existing matches"""
    print("\n" + "="*60)
    print("CHECKING EXISTING MATCHES")
    print("="*60)
    
    matches = Match.objects.all()
    print(f"\nTotal matches: {matches.count()}")
    
    for match in matches[:10]:  # Show first 10
        print(f"\n--- Match ID: {match.id} ---")
        print(f"Candidate: {match.candidate.full_name} (ID: {match.candidate.id})")
        print(f"Job Offer: {match.job_offer.title} (ID: {match.job_offer.id})")
        print(f"Overall Score: {match.overall_score}%")
        print(f"Technical Skill Score: {match.technical_skill_score}%")
        print(f"Experience Score: {match.experience_score}%")
        print(f"Education Score: {match.education_score}%")
        print(f"Soft Skill Score: {match.soft_skill_score}%")

def test_manual_matching():
    """Test manual matching between a candidate and job offer"""
    print("\n" + "="*60)
    print("TESTING MANUAL MATCHING")
    print("="*60)
    
    candidates = Candidate.objects.filter(status='active')
    job_offers = JobOffer.objects.all()
    
    if not candidates.exists():
        print("ERROR: No active candidates found")
        return
    
    if not job_offers.exists():
        print("ERROR: No job offers found")
        return
    
    candidate = candidates.first()
    job_offer = job_offers.first()
    
    print(f"\nMatching:")
    print(f"  Candidate: {candidate.full_name} (ID: {candidate.id})")
    print(f"  Job Offer: {job_offer.title} (ID: {job_offer.id})")
    
    # Check embeddings
    if not candidate.embedding:
        print("\nWARNING: Candidate has no embedding, generating one...")
        if candidate.cv_text:
            vector_matcher = VectorMatcher()
            candidate.embedding = vector_matcher.generate_embedding(candidate.cv_text)
            candidate.save()
            print("OK: Generated candidate embedding")
        else:
            print("ERROR: Candidate has no CV text, cannot generate embedding")
            return
    
    if not job_offer.embedding:
        print("\nWARNING: Job offer has no embedding, generating one...")
        vector_matcher = VectorMatcher()
        job_text = f"{job_offer.description} {job_offer.requirements}"
        job_offer.embedding = vector_matcher.generate_embedding(job_text)
        job_offer.save()
        print("OK: Generated job offer embedding")
    
    # Calculate similarity
    vector_matcher = VectorMatcher()
    similarity = vector_matcher.calculate_similarity(
        candidate.embedding,
        job_offer.embedding
    )
    
    print(f"\nOK: Similarity calculated: {similarity:.4f} ({similarity*100:.2f}%)")
    
    # Calculate detailed scores
    candidate_data = {
        'technical_skills': candidate.technical_skills or [],
        'experience_years': candidate.total_experience_years or 0,
        'education_level': candidate.education_level or '',
        'soft_skills': candidate.soft_skills or [],
    }
    
    job_data = {
        'required_skills': job_offer.required_skills or [],
        'required_experience_years': job_offer.required_experience_years or 0,
        'required_education': job_offer.required_education or '',
    }
    
    detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
    
    print(f"\nDetailed Scores:")
    print(f"  Technical Skills: {detailed_scores.get('technical_skills', 0)*100:.2f}%")
    print(f"  Experience: {detailed_scores.get('experience', 0)*100:.2f}%")
    print(f"  Education: {detailed_scores.get('education', 0)*100:.2f}%")
    print(f"  Soft Skills: {detailed_scores.get('soft_skills', 0)*100:.2f}%")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SMARTRECRUITAI MATCHING SYSTEM DIAGNOSTICS")
    print("="*60)
    
    check_vector_matcher()
    check_candidates()
    check_job_offers()
    check_matches()
    test_manual_matching()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)

