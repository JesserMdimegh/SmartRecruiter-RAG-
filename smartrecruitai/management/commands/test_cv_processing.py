"""
Management command to test CV processing with sample data
Usage: python manage.py test_cv_processing
"""

from django.core.management.base import BaseCommand
from smartrecruitai.models import Candidate, CV
from smartrecruitai.services import NLPExtractor, VectorMatcher


class Command(BaseCommand):
    help = 'Test CV processing with sample data'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing CV processing...'))
        
        # Sample CV text
        sample_cv_text = """
        John Smith
        Data Scientist
        john.smith@email.com
        +1 (555) 123-4567
        San Francisco, CA

        PROFESSIONAL SUMMARY
        Experienced Data Scientist with 5+ years of experience in machine learning, deep learning, and data analysis. 
        Specialized in Python, TensorFlow, PyTorch, and natural language processing.

        TECHNICAL SKILLS
        - Programming Languages: Python, R, SQL, JavaScript
        - Machine Learning: TensorFlow, PyTorch, Scikit-learn, Keras
        - Data Analysis: Pandas, NumPy, Matplotlib, Seaborn
        - Databases: PostgreSQL, MongoDB, Redis
        - Cloud Platforms: AWS, Google Cloud Platform, Azure
        - Tools: Git, Docker, Kubernetes, Jupyter Notebooks

        EXPERIENCE
        Senior Data Scientist | TechCorp Inc. | 2020 - Present
        - Led development of ML models for recommendation systems
        - Implemented deep learning solutions using TensorFlow
        - Collaborated with engineering teams to deploy models in production
        - Mentored junior data scientists

        Data Scientist | StartupXYZ | 2018 - 2020
        - Built predictive models for customer churn analysis
        - Developed NLP pipelines for text classification
        - Created data visualization dashboards using Python

        EDUCATION
        Master of Science in Data Science | Stanford University | 2018
        Bachelor of Science in Computer Science | UC Berkeley | 2016

        CERTIFICATIONS
        - AWS Certified Machine Learning Specialty
        - Google Cloud Professional Data Engineer
        - Certified Analytics Professional (CAP)

        PROJECTS
        1. Customer Sentiment Analysis System
           - Built NLP model using BERT for sentiment classification
           - Achieved 92% accuracy on customer feedback data
           - Technologies: Python, TensorFlow, BERT, Flask

        2. Real-time Recommendation Engine
           - Developed collaborative filtering algorithm
           - Implemented real-time scoring system
           - Technologies: Python, Apache Spark, Redis, Docker

        LANGUAGES
        - English (Native)
        - Spanish (Conversational)
        - French (Basic)

        SOFT SKILLS
        - Leadership
        - Communication
        - Problem Solving
        - Team Collaboration
        - Project Management
        """
        
        try:
            # Create candidate
            candidate = Candidate.objects.create(
                full_name="John Smith",
                email="john.smith@email.com"
            )
            
            # Extract data using NLP
            nlp_extractor = NLPExtractor()
            extracted_data = nlp_extractor.extract_cv_data(sample_cv_text)
            
            # Update candidate with extracted data
            candidate.cv_text = sample_cv_text
            candidate.technical_skills = extracted_data.get('technical_skills', [])
            candidate.soft_skills = extracted_data.get('soft_skills', [])
            candidate.total_experience_years = extracted_data.get('experience_years', 0)
            candidate.education_level = str(extracted_data.get('education', []))
            candidate.save()
            
            # Generate embedding
            vector_matcher = VectorMatcher()
            candidate.embedding = vector_matcher.generate_embedding(sample_cv_text)
            candidate.save()
            
            # Create CV record
            cv = CV.objects.create(
                candidate=candidate,
                file_name="sample_cv.txt",
                file_type="txt",
                extraction_status='completed',
                extracted_data=extracted_data
            )
            
            self.stdout.write(self.style.SUCCESS('Created candidate: ' + candidate.full_name))
            self.stdout.write('  - Email: ' + candidate.email)
            self.stdout.write('  - Experience: ' + str(candidate.total_experience_years) + ' years')
            self.stdout.write('  - Technical Skills: ' + ', '.join(candidate.technical_skills[:5]))
            self.stdout.write('  - Soft Skills: ' + ', '.join(candidate.soft_skills[:3]))
            self.stdout.write('  - Embedding dimension: ' + str(len(candidate.embedding)))
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('CV processing test completed successfully!'))
            self.stdout.write('Candidate ID: ' + str(candidate.id))
            self.stdout.write('CV ID: ' + str(cv.id))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

