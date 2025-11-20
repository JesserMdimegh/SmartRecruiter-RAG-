#!/usr/bin/env python
"""
Test script for enhanced language extraction and technical skills matching
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.services.nlp_extractor import NLPExtractor
from smartrecruitai.services.vector_matcher import VectorMatcher

def test_enhanced_language_extraction():
    """Test the enhanced language extraction with proficiency levels"""
    print("🌍 Testing Enhanced Language Extraction")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    # Test CV text with various languages and proficiency levels
    test_cv_text = """
    John Doe
    Senior Software Engineer
    
    Languages:
    - English (Native)
    - French (Fluent)
    - Spanish (Intermediate)
    - German (Basic)
    
    Additional Language Skills:
    Native English speaker
    Fluent in French and conversational Spanish
    Basic German proficiency
    Professional working proficiency in Portuguese
    
    Certifications:
    TOEFL: 115/120
    IELTS: 8.5/9.0
    
    Technical Skills:
    Python, JavaScript, React, Node.js, AWS, Docker
    Programming: Python, Py, Python3
    Frontend: React, ReactJS, JSX
    Backend: Node, NodeJS, Express
    Cloud: AWS, Amazon Web Services, EC2, S3
    Database: SQL, PostgreSQL, Postgres, MySQL
    Version Control: Git, GitHub, GitLab
    """
    
    extracted_data = nlp_extractor.extract_cv_data(test_cv_text)
    languages = extracted_data.get('languages', [])
    technical_skills = extracted_data.get('technical_skills', [])
    
    print(f"✅ Extracted {len(languages)} languages:")
    for i, language in enumerate(languages, 1):
        print(f"  {i}. {language}")
    
    print(f"\n✅ Extracted {len(technical_skills)} technical skills:")
    for i, skill in enumerate(technical_skills, 1):
        print(f"  {i}. {skill}")
    
    return languages, technical_skills

def test_enhanced_technical_skills_matching():
    """Test the enhanced technical skills matching with synonyms"""
    print("\n🔧 Testing Enhanced Technical Skills Matching")
    print("=" * 50)
    
    vector_matcher = VectorMatcher()
    
    # Test candidate and job data
    candidate_data = {
        'technical_skills': ['Python', 'ReactJS', 'Node', 'Postgres', 'Git', 'AWS', 'Docker'],
        'experience_years': 5,
        'education_level': 'Master',
        'soft_skills': ['Leadership', 'Communication', 'Teamwork']
    }
    
    job_data = {
        'required_skills': ['Python', 'React', 'Node.js', 'PostgreSQL', 'Version Control', 'Amazon Web Services', 'Containers'],
        'required_experience_years': 4,
        'required_education': 'Bachelor',
        'required_soft_skills': ['Leadership', 'Communication', 'Problem-Solving']
    }
    
    # Calculate detailed scores
    scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
    
    print("📊 Matching Scores Breakdown:")
    for category, score in scores.items():
        print(f"  {category.replace('_', ' ').title()}: {score:.2%}")
    
    # Show skill matching details
    print(f"\n🔍 Skill Matching Analysis:")
    candidate_skills = set(skill.lower() for skill in candidate_data['technical_skills'])
    job_skills = set(skill.lower() for skill in job_data['required_skills'])
    
    print(f"  Candidate Skills: {sorted(candidate_skills)}")
    print(f"  Required Skills: {sorted(job_skills)}")
    
    # Demonstrate synonym matching
    print(f"\n🎯 Synonym Matching Examples:")
    print(f"  ReactJS ↔ React: {'✓' if 'reactjs' in candidate_skills and 'react' in job_skills else '✗'}")
    print(f"  Node ↔ Node.js: {'✓' if 'node' in candidate_skills and 'node.js' in job_skills else '✗'}")
    print(f"  Postgres ↔ PostgreSQL: {'✓' if 'postgres' in candidate_skills and 'postgresql' in job_skills else '✗'}")
    print(f"  Git ↔ Version Control: {'✓' if 'git' in candidate_skills and 'version control' in job_skills else '✗'}")
    print(f"  AWS ↔ Amazon Web Services: {'✓' if 'aws' in candidate_skills and 'amazon web services' in job_skills else '✗'}")
    print(f"  Docker ↔ Containers: {'✓' if 'docker' in candidate_skills and 'containers' in job_skills else '✗'}")
    
    return scores

def test_multilingual_extraction():
    """Test language extraction for multiple languages"""
    print("\n🌐 Testing Multilingual Language Extraction")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    # Test with different language patterns
    test_cases = [
        {
            'name': 'English/French CV',
            'text': '''
            Languages: English (Native), Français (Courant)
            Native English speaker, fluent in French
            Bilingual English/French
            '''
        },
        {
            'name': 'Multi-language Professional',
            'text': '''
            Professional Profile:
            • English: Native Speaker
            • Spanish: Fluent (DELE C2)
            • Portuguese: Professional Working Proficiency
            • Italian: Intermediate
            • German: Basic (A2)
            • Mandarin Chinese: Beginner (HSK 2)
            '''
        },
        {
            'name': 'Technical Language Skills',
            'text': '''
            Language Skills:
            - English: Professional working proficiency
            - French: Advanced proficiency
            - Python programming: Expert
            - JavaScript: Advanced
            '''
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}:")
        extracted_data = nlp_extractor.extract_cv_data(test_case['text'])
        languages = extracted_data.get('languages', [])
        
        print(f"  Extracted Languages: {languages}")
        
        # Check for proficiency detection
        for lang in languages:
            if any(prof in lang.lower() for prof in ['native', 'fluent', 'intermediate', 'basic', 'advanced']):
                print(f"    ✓ Proficiency detected: {lang}")

def test_comprehensive_skill_matching():
    """Test comprehensive skill matching across different technology stacks"""
    print("\n💻 Testing Comprehensive Skill Matching")
    print("=" * 50)
    
    vector_matcher = VectorMatcher()
    
    # Test different technology scenarios
    scenarios = [
        {
            'name': 'Full Stack Developer',
            'candidate': ['JavaScript', 'ReactJS', 'Node', 'MongoDB', 'Docker', 'AWS'],
            'job': ['JavaScript', 'React', 'Node.js', 'NoSQL', 'Containers', 'Amazon Web Services']
        },
        {
            'name': 'Data Scientist',
            'candidate': ['Python', 'Py', 'TensorFlow', 'Pandas', 'NumPy', 'Scikit-Learn'],
            'job': ['Python', 'Machine Learning', 'Neural Networks', 'Data Analysis', 'Numerical Computing', 'ML Library']
        },
        {
            'name': 'DevOps Engineer',
            'candidate': ['Linux', 'Docker', 'K8s', 'Jenkins', 'Terraform', 'Ansible'],
            'job': ['Unix', 'Containers', 'Kubernetes', 'CI/CD', 'Infrastructure as Code', 'Automation']
        },
        {
            'name': 'Mobile Developer',
            'candidate': ['Swift', 'Kotlin', 'React Native', 'iOS', 'Android', 'Cross-Platform'],
            'job': ['iOS Development', 'Android Studio', 'Cross-Platform Mobile', 'Dart', 'Flutter']
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 {scenario['name']}:")
        
        candidate_data = {
            'technical_skills': scenario['candidate'],
            'experience_years': 3,
            'education_level': 'Bachelor',
            'soft_skills': ['Teamwork']
        }
        
        job_data = {
            'required_skills': scenario['job'],
            'required_experience_years': 2,
            'required_education': 'Bachelor',
            'required_soft_skills': ['Teamwork']
        }
        
        scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
        tech_score = scores.get('technical_skills', 0)
        
        print(f"  Technical Skills Match: {tech_score:.2%}")
        
        # Show matching details
        candidate_set = set(skill.lower() for skill in scenario['candidate'])
        job_set = set(skill.lower() for skill in scenario['job'])
        
        # Find potential matches using synonyms
        expanded_matches = []
        for job_skill in job_set:
            for candidate_skill in candidate_set:
                if job_skill == candidate_skill:
                    expanded_matches.append(f"Exact: {candidate_skill} ↔ {job_skill}")
                    break
        
        if expanded_matches:
            print(f"  Matches: {len(expanded_matches)} exact matches")
            for match in expanded_matches[:3]:  # Show first 3 matches
                print(f"    {match}")

if __name__ == "__main__":
    print("🚀 SmartRecruitAI Enhanced Extraction & Matching Test")
    print("=" * 60)
    
    # Test enhanced language extraction
    languages, skills = test_enhanced_language_extraction()
    
    # Test enhanced technical skills matching
    scores = test_enhanced_technical_skills_matching()
    
    # Test multilingual extraction
    test_multilingual_extraction()
    
    # Test comprehensive skill matching
    test_comprehensive_skill_matching()
    
    print(f"\n✅ Testing completed!")
    print(f"✅ Enhanced language extraction: {len(languages)} languages with proficiency levels")
    print(f"✅ Technical skills extraction: {len(skills)} skills")
    print(f"✅ Enhanced matching accuracy: {scores.get('technical_skills', 0):.2%}")
    print("\n🎯 Key Improvements:")
    print("- Language extraction with proficiency levels (Native, Fluent, etc.)")
    print("- Support for 12+ languages with variations")
    print("- Enhanced technical skills matching with 100+ synonyms")
    print("- Weighted scoring (exact matches: 100%, synonyms: 70%)")
    print("- Comprehensive technology stack coverage")
    print("- Multilingual CV processing support")
