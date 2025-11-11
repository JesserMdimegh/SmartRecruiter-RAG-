"""
Management command to create sample job offer and test matching
Usage: python manage.py test_job_matching
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from smartrecruitai.models import Recruiter, JobOffer, Match
from smartrecruitai.services import VectorMatcher, RAGEngine


class Command(BaseCommand):
    help = 'Create sample job offer and test matching'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample job offer and testing matching...'))
        
        try:
            # Get or create a user and recruiter
            user, created = User.objects.get_or_create(
                username='test_recruiter',
                defaults={'email': 'recruiter@test.com'}
            )
            
            recruiter, created = Recruiter.objects.get_or_create(
                user=user,
                defaults={'company_name': 'TechCorp Inc.', 'phone_number': '+1-555-0123'}
            )
            
            # Create sample job offer
            job_offer = JobOffer.objects.create(
                recruiter=recruiter,
                title='Senior Data Scientist',
                description='''
                We are looking for an experienced Senior Data Scientist to join our team.
                You will be responsible for developing machine learning models, analyzing large datasets,
                and working with cross-functional teams to deliver data-driven solutions.
                
                Key responsibilities:
                - Develop and implement machine learning models
                - Analyze large datasets to extract insights
                - Collaborate with engineering teams to deploy models
                - Mentor junior data scientists
                - Present findings to stakeholders
                ''',
                requirements='''
                Required qualifications:
                - 5+ years of experience in data science or machine learning
                - Strong programming skills in Python
                - Experience with machine learning frameworks (TensorFlow, PyTorch)
                - Knowledge of statistical analysis and data visualization
                - Experience with cloud platforms (AWS, GCP, Azure)
                - Strong communication and leadership skills
                ''',
                location='San Francisco, CA',
                job_type='full-time',
                remote_allowed=True,
                salary_min=120000,
                salary_max=180000,
                currency='USD',
                required_skills=['Python', 'TensorFlow', 'Machine Learning', 'Data Science'],
                required_experience_years=5,
                required_education='Master degree in Data Science or related field',
                status='open'
            )
            
            # Process job requirements
            from smartrecruitai.services import NLPExtractor
            nlp_extractor = NLPExtractor()
            job_text = f"{job_offer.description} {job_offer.requirements}"
            extracted_requirements = nlp_extractor.extract_job_requirements(job_text)
            
            job_offer.extracted_requirements = extracted_requirements
            job_offer.required_skills = extracted_requirements.get('required_skills', [])
            job_offer.required_experience_years = extracted_requirements.get('required_experience_years', 0)
            job_offer.save()
            
            # Generate embedding
            vector_matcher = VectorMatcher()
            job_offer.embedding = vector_matcher.generate_embedding(job_text)
            job_offer.save()
            
            self.stdout.write(self.style.SUCCESS('Created job offer: ' + job_offer.title))
            self.stdout.write('  - Company: ' + recruiter.company_name)
            self.stdout.write('  - Location: ' + job_offer.location)
            self.stdout.write('  - Required Skills: ' + ', '.join(job_offer.required_skills))
            self.stdout.write('  - Required Experience: ' + str(job_offer.required_experience_years) + ' years')
            
            # Test matching with existing candidates
            from smartrecruitai.models import Candidate
            candidates = Candidate.objects.filter(status='active')
            
            if candidates.exists():
                self.stdout.write('')
                self.stdout.write('Testing matching with existing candidates...')
                
                for candidate in candidates:
                    if candidate.embedding and job_offer.embedding:
                        # Calculate similarity
                        similarity = vector_matcher.calculate_similarity(
                            job_offer.embedding,
                            candidate.embedding
                        )
                        
                        # Calculate detailed scores
                        candidate_data = {
                            'technical_skills': candidate.technical_skills,
                            'experience_years': candidate.total_experience_years,
                            'education_level': candidate.education_level,
                            'soft_skills': candidate.soft_skills,
                        }
                        
                        job_data = {
                            'required_skills': job_offer.required_skills,
                            'required_experience_years': job_offer.required_experience_years,
                            'required_education': job_offer.required_education,
                        }
                        
                        detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
                        
                        # Create match
                        match, created = Match.objects.get_or_create(
                            candidate=candidate,
                            job_offer=job_offer
                        )
                        
                        match.overall_score = similarity * 100
                        match.technical_skill_score = detailed_scores.get('technical_skills', 0) * 100
                        match.experience_score = detailed_scores.get('experience', 0) * 100
                        match.education_score = detailed_scores.get('education', 0) * 100
                        match.soft_skill_score = detailed_scores.get('soft_skills', 0) * 100
                        
                        # Generate explanation
                        rag_engine = RAGEngine()
                        explanation = rag_engine.explain_match(candidate_data, job_data, detailed_scores)
                        match.match_explanation = explanation
                        
                        # Extract strengths and gaps
                        analysis = vector_matcher.generate_matching_explanation(
                            candidate_data, job_data, detailed_scores
                        )
                        match.strengths = analysis.get('strengths', [])
                        match.gaps = analysis.get('gaps', [])
                        match.recommendations = analysis.get('recommendations', [])
                        
                        match.save()
                        
                        self.stdout.write('')
                        self.stdout.write('Match: ' + candidate.full_name + ' -> ' + job_offer.title)
                        self.stdout.write('  - Overall Score: ' + str(round(match.overall_score, 1)) + '%')
                        self.stdout.write('  - Technical Skills: ' + str(round(match.technical_skill_score, 1)) + '%')
                        self.stdout.write('  - Experience: ' + str(round(match.experience_score, 1)) + '%')
                        self.stdout.write('  - Education: ' + str(round(match.education_score, 1)) + '%')
                        self.stdout.write('  - Soft Skills: ' + str(round(match.soft_skill_score, 1)) + '%')
                        
                        if match.strengths:
                            self.stdout.write('  - Strengths: ' + ', '.join(match.strengths[:3]))
                        if match.gaps:
                            self.stdout.write('  - Gaps: ' + ', '.join(match.gaps[:3]))
                        if match.recommendations:
                            self.stdout.write('  - Recommendation: ' + match.recommendations[0])
            else:
                self.stdout.write('No candidates found. Run test_cv_processing first.')
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Job matching test completed!'))
            self.stdout.write('Job Offer ID: ' + str(job_offer.id))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error: ' + str(e)))

