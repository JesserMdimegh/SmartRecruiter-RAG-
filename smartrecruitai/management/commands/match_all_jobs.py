"""
Management command to match all candidates to all job offers
Usage: python manage.py match_all_jobs --job-id JOB_ID
"""

from django.core.management.base import BaseCommand
from smartrecruitai.models import JobOffer, Candidate, Match
from smartrecruitai.services import VectorMatcher, RAGEngine


class Command(BaseCommand):
    help = 'Match all candidates to job offers'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--job-id',
            type=int,
            help='Match candidates to a specific job offer',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting matching process...'))
        
        # Get job offers
        if options['job_id']:
            job_offers = JobOffer.objects.filter(pk=options['job_id'])
        else:
            job_offers = JobOffer.objects.filter(status='open')
        
        total_jobs = job_offers.count()
        self.stdout.write(f'Found {total_jobs} job offers to match')
        
        # Get all active candidates
        candidates = Candidate.objects.filter(status='active')
        total_candidates = candidates.count()
        self.stdout.write(f'Found {total_candidates} active candidates')
        
        # Initialize services
        vector_matcher = VectorMatcher()
        rag_engine = RAGEngine()
        
        matches_created = 0
        matches_updated = 0
        
        for job_offer in job_offers:
            if not job_offer.embedding:
                self.stdout.write(self.style.WARNING(f'Skipping job {job_offer.title} - no embedding'))
                continue
            
            job_data = {
                'required_skills': job_offer.required_skills,
                'required_experience_years': job_offer.required_experience_years,
                'required_education': job_offer.required_education,
            }
            
            for candidate in candidates:
                if not candidate.embedding:
                    continue
                
                try:
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
                    
                    detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
                    
                    # Create or update match
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
                    
                    if created:
                        matches_created += 1
                    else:
                        matches_updated += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error matching {candidate.full_name} to {job_offer.title}: {str(e)}'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Matching complete:'))
        self.stdout.write(f'  - New matches created: {matches_created}')
        self.stdout.write(f'  - Matches updated: {matches_updated}')
        self.stdout.write(f'  - Total matches: {matches_created + matches_updated}')

