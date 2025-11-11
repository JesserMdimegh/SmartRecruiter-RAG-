"""
Management command to process CV files
Usage: python manage.py process_cvs
"""

from django.core.management.base import BaseCommand
from smartrecruitai.models import CV, Candidate
from smartrecruitai.services import CVParser, NLPExtractor, VectorMatcher


class Command(BaseCommand):
    help = 'Process pending CV files and extract information'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cv-id',
            type=int,
            help='Process a specific CV by ID',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CV processing...'))
        
        # Get CVs to process
        if options['cv_id']:
            cvs = CV.objects.filter(pk=options['cv_id'])
        else:
            cvs = CV.objects.filter(extraction_status='pending')
        
        total = cvs.count()
        self.stdout.write(f'Found {total} CVs to process')
        
        # Initialize services
        cv_parser = CVParser()
        nlp_extractor = NLPExtractor()
        vector_matcher = VectorMatcher()
        
        processed = 0
        failed = 0
        
        for cv in cvs:
            try:
                self.stdout.write(f'Processing CV: {cv.file_name}')
                
                # Update status
                cv.extraction_status = 'processing'
                cv.save()
                
                # Parse CV file
                parsed_data = cv_parser.parse_file(cv.file_path)
                cv_text = parsed_data['text']
                
                # Extract structured data
                extracted_data = nlp_extractor.extract_cv_data(cv_text)
                
                # Update candidate with extracted data
                candidate = cv.candidate
                candidate.cv_text = cv_text
                candidate.technical_skills = extracted_data.get('technical_skills', [])
                candidate.soft_skills = extracted_data.get('soft_skills', [])
                candidate.total_experience_years = extracted_data.get('experience_years', 0)
                candidate.save()
                
                # Generate embedding
                embedding = vector_matcher.generate_embedding(cv_text)
                candidate.embedding = embedding
                candidate.save()
                
                # Update CV record
                cv.extracted_data = extracted_data
                cv.extraction_status = 'completed'
                cv.save()
                
                processed += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Processed: {cv.file_name}'))
                
            except Exception as e:
                cv.extraction_status = 'failed'
                cv.extraction_error = str(e)
                cv.save()
                
                failed += 1
                self.stdout.write(self.style.ERROR(f'✗ Failed: {cv.file_name} - {str(e)}'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Processing complete:'))
        self.stdout.write(f'  - Successfully processed: {processed}')
        self.stdout.write(f'  - Failed: {failed}')
        self.stdout.write(f'  - Total: {total}')

