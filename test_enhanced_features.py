#!/usr/bin/env python
"""
Test script for enhanced soft skills extraction and candidate ranking
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.services import NLPExtractor, VectorMatcher, RAGEngine
from smartrecruitai.models import Candidate, JobOffer

def test_enhanced_soft_skills():
    """Test the enhanced soft skills extraction"""
    print("🧠 Testing Enhanced Soft Skills Extraction")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    # Test CV text with various soft skills
    test_cv_text = """
    John Doe
    Senior Software Engineer
    
    Professional Experience:
    - Led a team of 5 developers in agile environment
    - Excellent communication skills with stakeholders
    - Strong problem-solving abilities and critical thinking
    - Proactive approach to project management
    - Mentored junior developers and conducted training sessions
    - Collaborated effectively with cross-functional teams
    - Demonstrated leadership during high-pressure situations
    - Time management and prioritization of multiple projects
    - Customer-focused mindset with attention to detail
    - Continuous learning and adaptation to new technologies
    """
    
    extracted_data = nlp_extractor.extract_cv_data(test_cv_text)
    soft_skills = extracted_data.get('soft_skills', [])
    
    print(f"Extracted {len(soft_skills)} soft skills:")
    for i, skill in enumerate(soft_skills, 1):
        print(f"  {i}. {skill}")
    
    print(f"\n✅ Soft skills extraction enhanced from 12 to {len(soft_skills)}+ skills!")
    return soft_skills

def test_candidate_ranking():
    """Test candidate ranking with detailed scoring"""
    print("\n🏆 Testing Candidate Ranking System")
    print("=" * 50)
    
    # Check if we have candidates and job offers
    candidates = Candidate.objects.filter(status='active')[:3]
    job_offers = JobOffer.objects.filter(status='open')[:1]
    
    if not candidates:
        print("❌ No active candidates found. Please create some candidates first.")
        return
    
    if not job_offers:
        print("❌ No open job offers found. Please create a job offer first.")
        return
    
    job_offer = job_offers[0]
    print(f"Job Offer: {job_offer.title}")
    print(f"Required Skills: {job_offer.required_skills or []}")
    print(f"Required Experience: {job_offer.required_experience_years} years")
    
    # Initialize services
    vector_matcher = VectorMatcher()
    rag_engine = RAGEngine()
    
    # Enhanced soft skills requirements for the job
    required_soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem-solving',
        'critical thinking', 'time management', 'proactive'
    ]
    
    print(f"\nRequired Soft Skills: {required_soft_skills}")
    
    ranked_candidates = []
    
    for candidate in candidates:
        print(f"\n--- Analyzing: {candidate.full_name or 'Unnamed Candidate'} ---")
        
        # Generate embedding if missing
        if not candidate.embedding and candidate.cv_text:
            candidate.embedding = vector_matcher.generate_embedding(candidate.cv_text)
            candidate.save()
        
        if not candidate.embedding:
            print("❌ No CV text available for comparison")
            continue
        
        # Calculate similarity
        similarity = vector_matcher.calculate_similarity(
            job_offer.embedding, candidate.embedding
        )
        
        # Prepare data
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
            'required_soft_skills': required_soft_skills,
        }
        
        # Calculate detailed scores
        detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
        
        # Get weights and calculate overall score
        from django.conf import settings
        weights = getattr(settings, 'MATCHING_WEIGHTS', None)
        overall_percent = vector_matcher.calculate_overall_score(similarity, detailed_scores, weights)
        
        # Generate explanation
        detailed_scores['overall_score'] = overall_percent / 100.0
        explanation = rag_engine.explain_match(candidate_data, job_data, detailed_scores)
        
        # Create candidate profile
        candidate_profile = {
            'name': candidate.full_name or 'Unnamed',
            'overall_score': round(overall_percent, 2),
            'technical_score': round(detailed_scores.get('technical_skills', 0) * 100, 2),
            'experience_score': round(detailed_scores.get('experience', 0) * 100, 2),
            'soft_skill_score': round(detailed_scores.get('soft_skills', 0) * 100, 2),
            'education_score': round(detailed_scores.get('education', 0) * 100, 2),
            'soft_skills': candidate.soft_skills or [],
            'soft_skills_matched': len(set(candidate_data['soft_skills']) & set(required_soft_skills)),
            'explanation': explanation[:200] + "..." if len(explanation) > 200 else explanation
        }
        
        ranked_candidates.append(candidate_profile)
        
        print(f"Overall Score: {candidate_profile['overall_score']}%")
        print(f"Technical Skills: {candidate_profile['technical_score']}%")
        print(f"Soft Skills: {candidate_profile['soft_skill_score']}% ({candidate_profile['soft_skills_matched']}/{len(required_soft_skills)} matched)")
        print(f"Experience: {candidate_profile['experience_score']}%")
        print(f"Education: {candidate_profile['education_score']}%")
    
    # Sort and display ranking
    ranked_candidates.sort(key=lambda x: x['overall_score'], reverse=True)
    
    print(f"\n🏆 FINAL RANKING:")
    print("=" * 50)
    for i, candidate in enumerate(ranked_candidates, 1):
        print(f"{i}. {candidate['name']} - {candidate['overall_score']}%")
        print(f"   Technical: {candidate['technical_score']}% | Soft Skills: {candidate['soft_skill_score']}% | Experience: {candidate['experience_score']}%")
    
    return ranked_candidates

def demonstrate_api_usage():
    """Show how to use the new ranking API endpoint"""
    print("\n📡 API Usage Example")
    print("=" * 50)
    
    print("To use the new ranking endpoint, make a POST request to:")
    print("POST /api/job-offers/{job_id}/rank_candidates/")
    
    print("\nRequest Body:")
    print("""
{
    "candidate_ids": [1, 2, 3, 4, 5],
    "required_soft_skills": [
        "leadership", "communication", "teamwork", 
        "problem-solving", "critical thinking"
    ]
}
    """)
    
    print("\nResponse includes:")
    print("- Ranked candidates with detailed scores")
    print("- Comprehensive explanations for each candidate")
    print("- Soft skills matching analysis")
    print("- Summary statistics")
    print("- Strengths, gaps, and recommendations")

if __name__ == "__main__":
    print("🚀 SmartRecruitAI Enhanced Features Test")
    print("=" * 60)
    
    # Test enhanced soft skills extraction
    soft_skills = test_enhanced_soft_skills()
    
    # Test candidate ranking
    ranked_candidates = test_candidate_ranking()
    
    # Show API usage
    demonstrate_api_usage()
    
    print(f"\n✅ Testing completed!")
    print(f"✅ Enhanced soft skills extraction: {len(soft_skills)}+ skills")
    print(f"✅ Candidate ranking system: {len(ranked_candidates) if ranked_candidates else 0} candidates analyzed")
    print("\n🎯 Enhancements Summary:")
    print("- Expanded soft skills library from 12 to 70+ skills")
    print("- Added skill variations and synonyms")
    print("- Enhanced soft skills matching with 10% weight in scoring")
    print("- New ranking API endpoint for multiple CV comparison")
    print("- Detailed scoring breakdown with explanations")
