"""
Script to fix the matching system by regenerating all embeddings
Run this AFTER installing sentence-transformers, numpy, and scipy
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.models import Candidate, JobOffer
from smartrecruitai.services.vector_matcher import VectorMatcher

def regenerate_candidate_embeddings():
    """Regenerate embeddings for all candidates"""
    print("\n" + "="*60)
    print("REGENERATING CANDIDATE EMBEDDINGS")
    print("="*60)
    
    candidates = Candidate.objects.all()
    print(f"\nTotal candidates: {candidates.count()}")
    
    vector_matcher = VectorMatcher()
    
    updated = 0
    skipped = 0
    errors = 0
    
    for candidate in candidates:
        try:
            # Check if embedding is mock (all 0.1)
            is_mock = False
            if candidate.embedding:
                if isinstance(candidate.embedding, list) and len(candidate.embedding) > 0:
                    if all(abs(v - 0.1) < 0.001 for v in candidate.embedding[:10]):
                        is_mock = True
            
            # Only regenerate if mock or missing
            if is_mock or not candidate.embedding or not candidate.cv_text:
                if candidate.cv_text:
                    print(f"\nRegenerating embedding for candidate {candidate.id}: {candidate.full_name}")
                    candidate.embedding = vector_matcher.generate_embedding(candidate.cv_text)
                    candidate.save()
                    updated += 1
                    print(f"  OK: Generated embedding (length: {len(candidate.embedding)})")
                else:
                    print(f"\nSkipping candidate {candidate.id}: {candidate.full_name} - No CV text")
                    skipped += 1
            else:
                print(f"\nSkipping candidate {candidate.id}: {candidate.full_name} - Already has real embedding")
        except Exception as e:
            print(f"\nERROR processing candidate {candidate.id}: {str(e)}")
            errors += 1
    
    print(f"\n--- Summary ---")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

def regenerate_job_embeddings():
    """Regenerate embeddings for all job offers"""
    print("\n" + "="*60)
    print("REGENERATING JOB OFFER EMBEDDINGS")
    print("="*60)
    
    job_offers = JobOffer.objects.all()
    print(f"\nTotal job offers: {job_offers.count()}")
    
    vector_matcher = VectorMatcher()
    
    updated = 0
    skipped = 0
    errors = 0
    
    for job in job_offers:
        try:
            # Check if embedding is mock (all 0.1)
            is_mock = False
            if job.embedding:
                if isinstance(job.embedding, list) and len(job.embedding) > 0:
                    if all(abs(v - 0.1) < 0.001 for v in job.embedding[:10]):
                        is_mock = True
            
            # Only regenerate if mock or missing
            if is_mock or not job.embedding:
                job_text = f"{job.description} {job.requirements}".strip()
                if job_text:
                    print(f"\nRegenerating embedding for job offer {job.id}: {job.title}")
                    job.embedding = vector_matcher.generate_embedding(job_text)
                    job.save()
                    updated += 1
                    print(f"  OK: Generated embedding (length: {len(job.embedding)})")
                else:
                    print(f"\nSkipping job offer {job.id}: {job.title} - No description/requirements")
                    skipped += 1
            else:
                print(f"\nSkipping job offer {job.id}: {job.title} - Already has real embedding")
        except Exception as e:
            print(f"\nERROR processing job offer {job.id}: {str(e)}")
            errors += 1
    
    print(f"\n--- Summary ---")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    all_ok = True
    
    try:
        from sentence_transformers import SentenceTransformer
        print("OK: sentence-transformers is installed")
    except ImportError:
        print("ERROR: sentence-transformers is NOT installed")
        print("  Install with: pip install sentence-transformers")
        all_ok = False
    
    try:
        import numpy as np
        print("OK: numpy is installed")
    except ImportError:
        print("ERROR: numpy is NOT installed")
        print("  Install with: pip install numpy")
        all_ok = False
    
    try:
        from scipy.spatial.distance import cosine
        print("OK: scipy is installed")
    except ImportError:
        print("ERROR: scipy is NOT installed")
        print("  Install with: pip install scipy")
        all_ok = False
    
    return all_ok

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SMARTRECRUITAI MATCHING SYSTEM FIX")
    print("="*60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n" + "="*60)
        print("ERROR: Required dependencies are missing!")
        print("Please install them first, then run this script again.")
        print("="*60)
        sys.exit(1)
    
    # Regenerate embeddings
    regenerate_candidate_embeddings()
    regenerate_job_embeddings()
    
    print("\n" + "="*60)
    print("FIX COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Test matching by going to http://localhost:8000/match-cv/")
    print("2. Create new job offers with required_skills populated")
    print("3. Upload new CVs - they will automatically get real embeddings")



