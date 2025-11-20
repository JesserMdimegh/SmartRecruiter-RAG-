#!/usr/bin/env python
"""
Test script for the complete CV ranking workflow
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

def create_sample_data():
    """Create sample candidates and job offer for testing"""
    print("📝 Creating Sample Data")
    print("=" * 40)
    
    # Create sample candidates
    sample_candidates = [
        {
            'full_name': 'Alice Johnson',
            'email': 'alice@email.com',
            'current_position': 'Senior Software Engineer',
            'cv_text': '''
            Alice Johnson
            Senior Software Engineer with 6 years of experience
            
            Technical Skills: Python, Django, React, PostgreSQL, Docker, AWS
            Soft Skills: Leadership, communication, teamwork, problem-solving, 
                       critical thinking, time management, proactive, mentoring
            
            Experience: 6 years in web development, led team of 4 developers
            Education: Master's in Computer Science
            ''',
            'technical_skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker', 'AWS'],
            'soft_skills': ['Leadership', 'Communication', 'Teamwork', 'Problem-Solving', 
                           'Critical Thinking', 'Time Management', 'Proactive', 'Mentoring'],
            'total_experience_years': 6.0,
            'education_level': 'Master in Computer Science'
        },
        {
            'full_name': 'Bob Smith',
            'email': 'bob@email.com',
            'current_position': 'Full Stack Developer',
            'cv_text': '''
            Bob Smith
            Full Stack Developer with 4 years of experience
            
            Technical Skills: JavaScript, Node.js, React, MongoDB, Express
            Soft Skills: Communication, collaboration, adaptability, creativity,
                       fast learner, continuous learning, teamwork
            
            Experience: 4 years in full stack development
            Education: Bachelor's in Software Engineering
            ''',
            'technical_skills': ['JavaScript', 'Node.js', 'React', 'MongoDB', 'Express'],
            'soft_skills': ['Communication', 'Collaboration', 'Adaptability', 'Creativity',
                           'Fast Learner', 'Continuous Learning', 'Teamwork'],
            'total_experience_years': 4.0,
            'education_level': 'Bachelor in Software Engineering'
        },
        {
            'full_name': 'Carol Davis',
            'email': 'carol@email.com',
            'current_position': 'DevOps Engineer',
            'cv_text': '''
            Carol Davis
            DevOps Engineer with 5 years of experience
            
            Technical Skills: Kubernetes, Docker, Jenkins, AWS, Terraform, Ansible
            Soft Skills: Leadership, problem-solving, attention to detail, 
                       organization, planning, stress management, reliability
            
            Experience: 5 years in DevOps and cloud infrastructure
            Education: Master's in Information Technology
            ''',
            'technical_skills': ['Kubernetes', 'Docker', 'Jenkins', 'AWS', 'Terraform', 'Ansible'],
            'soft_skills': ['Leadership', 'Problem-Solving', 'Attention To Detail', 
                           'Organization', 'Planning', 'Stress Management', 'Reliability'],
            'total_experience_years': 5.0,
            'education_level': 'Master in Information Technology'
        }
    ]
    
    # Create sample job offer
    sample_job = {
        'title': 'Senior Full Stack Developer',
        'description': 'We are looking for a Senior Full Stack Developer to join our team.',
        'requirements': 'Experience with modern web frameworks, cloud technologies, and team leadership.',
        'location': 'Remote',
        'job_type': 'full-time',
        'required_skills': ['Python', 'JavaScript', 'React', 'AWS', 'Docker'],
        'required_experience_years': 4,
        'required_education': 'Bachelor'
    }
    
    # Create candidates in database
    created_candidates = []
    for cand_data in sample_candidates:
        candidate, created = Candidate.objects.get_or_create(
            email=cand_data['email'],
            defaults=cand_data
        )
        if created or not candidate.embedding:
            # Generate embedding
            vector_matcher = VectorMatcher()
            candidate.embedding = vector_matcher.generate_embedding(cand_data['cv_text'])
            candidate.save()
        created_candidates.append(candidate)
        print(f"✓ Created/Updated: {candidate.full_name}")
    
    # Create job offer in database
    job_offer, created = JobOffer.objects.get_or_create(
        title=sample_job['title'],
        defaults=sample_job
    )
    if created or not job_offer.embedding:
        # Generate embedding
        vector_matcher = VectorMatcher()
        job_text = f"{sample_job['description']} {sample_job['requirements']}"
        job_offer.embedding = vector_matcher.generate_embedding(job_text)
        job_offer.save()
    
    print(f"✓ Created/Updated Job Offer: {job_offer.title}")
    
    return created_candidates, job_offer

def demonstrate_ranking_api():
    """Demonstrate the ranking API functionality"""
    print("\n🏆 Demonstrating CV Ranking API")
    print("=" * 40)
    
    # Get sample data
    candidates = list(Candidate.objects.all()[:3])
    if len(candidates) < 3:
        print("❌ Need at least 3 candidates for demonstration")
        return
    
    job_offer = JobOffer.objects.first()
    if not job_offer:
        print("❌ No job offer found")
        return
    
    print(f"Job Offer: {job_offer.title}")
    print(f"Candidates to rank: {[c.full_name for c in candidates]}")
    
    # Initialize services
    vector_matcher = VectorMatcher()
    rag_engine = RAGEngine()
    
    # Required soft skills for the job
    required_soft_skills = ['leadership', 'communication', 'teamwork', 'problem-solving']
    
    print(f"\nRequired Soft Skills: {required_soft_skills}")
    
    # Simulate the ranking process
    ranked_results = []
    
    for candidate in candidates:
        print(f"\n--- Analyzing: {candidate.full_name} ---")
        
        # Calculate similarity
        if candidate.embedding and job_offer.embedding:
            similarity = vector_matcher.calculate_similarity(
                job_offer.embedding, candidate.embedding
            )
        else:
            similarity = 0.5  # Default similarity
        
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
        
        # Create result
        result = {
            'candidate': candidate.full_name,
            'overall_score': round(overall_percent, 2),
            'technical_score': round(detailed_scores.get('technical_skills', 0) * 100, 2),
            'soft_skill_score': round(detailed_scores.get('soft_skills', 0) * 100, 2),
            'experience_score': round(detailed_scores.get('experience', 0) * 100, 2),
            'education_score': round(detailed_scores.get('education', 0) * 100, 2),
            'soft_skills_matched': len(set(candidate_data['soft_skills']) & set(required_soft_skills)),
            'explanation': explanation[:150] + "..." if len(explanation) > 150 else explanation
        }
        
        ranked_results.append(result)
        print(f"Overall Score: {result['overall_score']}%")
        print(f"Technical: {result['technical_score']}% | Soft Skills: {result['soft_skill_score']}%")
        print(f"Soft Skills Matched: {result['soft_skills_matched']}/{len(required_soft_skills)}")
    
    # Sort results
    ranked_results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    print(f"\n🏆 FINAL RANKING:")
    print("=" * 40)
    for i, result in enumerate(ranked_results, 1):
        print(f"{i}. {result['candidate']} - {result['overall_score']}%")
        print(f"   Technical: {result['technical_score']}% | Soft Skills: {result['soft_skill_score']}%")
    
    return ranked_results

def show_template_usage():
    """Show how to use the new template"""
    print("\n🌐 Template Usage")
    print("=" * 40)
    print("Access the CV ranking interface at:")
    print("http://localhost:8000/rank-cvs/")
    print("\nFeatures:")
    print("✓ Interactive job offer selection")
    print("✓ Visual candidate selection with cards")
    print("✓ Soft skills requirement configuration")
    print("✓ Real-time ranking with detailed analysis")
    print("✓ Comprehensive scoring breakdown")
    print("✓ AI-generated explanations and recommendations")
    print("\nTemplate File: smartrecruitai/templates/cv_ranking.html")

if __name__ == "__main__":
    print("🚀 SmartRecruitAI CV Ranking System Test")
    print("=" * 60)
    
    # Create sample data
    candidates, job_offer = create_sample_data()
    
    # Demonstrate ranking
    results = demonstrate_ranking_api()
    
    # Show template usage
    show_template_usage()
    
    print(f"\n✅ Test completed successfully!")
    print(f"✅ Created {len(candidates)} sample candidates")
    print(f"✅ Created sample job offer: {job_offer.title}")
    print(f"✅ Ranked {len(results)} candidates with enhanced soft skills matching")
    print(f"\n🎯 Next Steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Visit: http://localhost:8000/rank-cvs/")
    print("3. Select job offer and candidates to rank")
    print("4. Configure soft skills requirements")
    print("5. View comprehensive ranking results!")
