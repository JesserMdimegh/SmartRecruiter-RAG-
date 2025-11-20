"""
Views for SmartRecruitAI API
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q

from .models import (
    Recruiter, Candidate, CV, JobOffer, Match,
    Conversation, Message, GeneratedDocument, Analytics
)
from .serializers.serializers import (
    CandidateSerializer, CVSerializer, JobOfferSerializer,
    JobOfferCreateSerializer, MatchSerializer, ConversationSerializer,
    MessageSerializer, GeneratedDocumentSerializer
)
from .services import NLPExtractor, VectorMatcher, RAGEngine, CVParser
from django.conf import settings
from .mixins import CSRFExemptMixin


@ensure_csrf_cookie
def cv_upload_page(request):
    """Serve the CV upload test page"""
    return render(request, 'cv_upload_test.html')


@ensure_csrf_cookie
def create_job_offer_page(request):
    """Serve the create job offer page"""
    return render(request, 'create_job_offer_modern.html')


@ensure_csrf_cookie
def list_job_offers_page(request):
    """Serve the list job offers page"""
    return render(request, 'list_job_offers_modern.html')


@ensure_csrf_cookie
def match_cv_page(request):
    """Serve the match CV to job offer page"""
    return render(request, 'match_cv.html')


@ensure_csrf_cookie
def cv_ranking_page(request):
    """Serve the advanced CV ranking page"""
    return render(request, 'cv_ranking.html')


class CandidateViewSet(CSRFExemptMixin, viewsets.ModelViewSet):
    """API endpoint for candidates"""
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = []  # Allow anonymous access for testing
    
    @action(detail=False, methods=['post'])
    def upload_cv_direct(self, request):
        """Upload a CV and create candidate automatically"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        try:
            # Create a temporary candidate first
            candidate = Candidate.objects.create(
                full_name="Processing...",
                email="processing@temp.com"
            )
            
            # Save CV file
            cv = CV.objects.create(
                candidate=candidate,
                file_name=uploaded_file.name,
                file_type=uploaded_file.name.split('.')[-1].lower(),
                uploaded_by=request.user if request.user.is_authenticated else None,
                extraction_status='processing',
            )
            
            # Process CV (in production, this would be async via Celery)
            try:
                # Handle both in-memory and temporary file uploads
                if hasattr(uploaded_file, 'temporary_file_path'):
                    # File is saved to temporary location
                    cv_text = CVParser().extract_text(uploaded_file.temporary_file_path())
                else:
                    # File is in memory, save it temporarily
                    import tempfile
                    import os
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as temp_file:
                        # Write uploaded file content to temporary file
                        for chunk in uploaded_file.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name
                    
                    try:
                        # Extract text from temporary file
                        cv_text = CVParser().extract_text(temp_file_path)
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                
                # Extract structured data
                nlp_extractor = NLPExtractor()
                extracted_data = nlp_extractor.extract_cv_data(cv_text)
                
                # Extract professional links
                professional_links = extracted_data.get('professional_links', {})
                
                # Update candidate with extracted data
                candidate.cv_text = cv_text
                candidate.technical_skills = extracted_data.get('technical_skills', [])
                candidate.soft_skills = extracted_data.get('soft_skills', [])
                candidate.total_experience_years = extracted_data.get('experience_years', 0)
                candidate.education_level = str(extracted_data.get('education', []))
                candidate.languages = extracted_data.get('languages', [])
                candidate.certifications = extracted_data.get('certifications', [])
                
                # Save professional links
                candidate.professional_links = professional_links
                candidate.linkedin_url = professional_links.get('linkedin', [''])[0] if professional_links.get('linkedin') else ''
                candidate.github_url = professional_links.get('github', [''])[0] if professional_links.get('github') else ''
                candidate.gitlab_url = professional_links.get('gitlab', [''])[0] if professional_links.get('gitlab') else ''
                candidate.portfolio_urls = professional_links.get('portfolio', [])
                
                # Try to extract name and email from CV text
                candidate.full_name = self._extract_name_from_cv(cv_text)
                candidate.email = self._extract_email_from_cv(cv_text)
                
                candidate.save()
                
                # Generate embedding
                vector_matcher = VectorMatcher()
                candidate.embedding = vector_matcher.generate_embedding(cv_text)
                candidate.save()
                
                # Update CV record
                cv.extracted_data = extracted_data
                cv.extraction_status = 'completed'
                cv.save()
                
                return Response({
                    'message': 'CV processed successfully',
                    'candidate_id': candidate.id,
                    'cv_id': cv.id,
                    'extracted_data': extracted_data,
                    'candidate': CandidateSerializer(candidate).data
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                cv.extraction_status = 'failed'
                cv.extraction_error = str(e)
                cv.save()
                
                # Delete the candidate if processing failed
                candidate.delete()
                
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _extract_name_from_cv(self, cv_text: str) -> str:
        """Extract candidate name from CV text"""
        lines = cv_text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 2 and len(line) < 50:  # Reasonable name length
                # Simple heuristic: if line doesn't contain common CV keywords
                keywords = ['cv', 'resume', 'email', 'phone', 'address', 'experience', 'education']
                if not any(keyword in line.lower() for keyword in keywords):
                    return line
        return "Candidate"
    
    def _extract_email_from_cv(self, cv_text: str) -> str:
        """Extract email from CV text"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text)
        return emails[0] if emails else ""
    
    @action(detail=True, methods=['post'])
    def upload_cv(self, request, pk=None):
        """Upload and process a CV for a candidate"""
        candidate = self.get_object()
        
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # Save CV file
        cv = CV.objects.create(
            candidate=candidate,
            file_name=uploaded_file.name,
            file_type=uploaded_file.name.split('.')[-1].lower(),
            uploaded_by=request.user if request.user.is_authenticated else None,
            extraction_status='processing',
        )
        
        # Process CV (in production, this would be async via Celery)
        try:
            # Handle both in-memory and temporary file uploads
            if hasattr(uploaded_file, 'temporary_file_path'):
                # File is saved to temporary location
                cv_text = CVParser().extract_text(uploaded_file.temporary_file_path())
            else:
                # File is in memory, save it temporarily
                import tempfile
                import os
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as temp_file:
                    # Write uploaded file content to temporary file
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                try:
                    # Extract text from temporary file
                    cv_text = CVParser().extract_text(temp_file_path)
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            
            # Extract structured data
            nlp_extractor = NLPExtractor()
            extracted_data = nlp_extractor.extract_cv_data(cv_text)
            
            # Update candidate with extracted data
            candidate.cv_text = cv_text
            candidate.technical_skills = extracted_data.get('technical_skills', [])
            candidate.soft_skills = extracted_data.get('soft_skills', [])
            candidate.total_experience_years = extracted_data.get('experience_years', 0)
            candidate.education_level = str(extracted_data.get('education', []))
            candidate.save()
            
            # Generate embedding
            vector_matcher = VectorMatcher()
            candidate.embedding = vector_matcher.generate_embedding(cv_text)
            candidate.save()
            
            # Update CV record
            cv.extracted_data = extracted_data
            cv.extraction_status = 'completed'
            cv.save()
            
            return Response({
                'message': 'CV processed successfully',
                'cv_id': cv.id,
                'extracted_data': extracted_data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            cv.extraction_status = 'failed'
            cv.extraction_error = str(e)
            cv.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get all matches for a candidate"""
        candidate = self.get_object()
        matches = Match.objects.filter(candidate=candidate)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class JobOfferViewSet(CSRFExemptMixin, viewsets.ModelViewSet):
    """API endpoint for job offers"""
    queryset = JobOffer.objects.all()
    permission_classes = []  # Allow anonymous access for testing
    
    # Disable pagination for list view
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobOfferCreateSerializer
        return JobOfferSerializer
    
    def create(self, request, *args, **kwargs):
        """Create job offer and return full data including required_skills"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the created job offer and refresh from DB to get all updates
        job_offer = serializer.instance
        if job_offer and job_offer.pk:
            job_offer.refresh_from_db()
        
        # Return full job offer data with updated skills
        response_serializer = JobOfferSerializer(job_offer)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Create job offer with default recruiter if needed"""
        # Get or create a default recruiter for anonymous users
        if not self.request.user.is_authenticated:
            # Create or get default recruiter
            default_user, created = User.objects.get_or_create(
                username='default_recruiter',
                defaults={'email': 'recruiter@smartrecruitai.com'}
            )
            
            recruiter, created = Recruiter.objects.get_or_create(
                user=default_user,
                defaults={'company_name': 'SmartRecruitAI', 'phone_number': ''}
            )
        else:
            # Use authenticated user's recruiter profile
            recruiter, created = Recruiter.objects.get_or_create(
                user=self.request.user,
                defaults={'company_name': 'My Company', 'phone_number': ''}
            )
        
        # Save the job offer
        job_offer = serializer.save(recruiter=recruiter, status='open')
        
        # Ensure required_skills is saved properly (handle if it's None or empty list)
        if job_offer.required_skills is None:
            job_offer.required_skills = []
            job_offer.save()
        
        # Process requirements to extract additional data
        try:
            nlp_extractor = NLPExtractor()
            job_text = f"{job_offer.description} {job_offer.requirements}"
            extracted = nlp_extractor.extract_job_requirements(job_text)
            
            # Update job offer with extracted data if needed
            if extracted.get('required_skills'):
                # Merge with existing required_skills
                existing_skills = job_offer.required_skills or []
                new_skills = extracted.get('required_skills', [])
                # Combine and remove duplicates
                all_skills = list(set(existing_skills + new_skills))
                job_offer.required_skills = all_skills
                job_offer.required_experience_years = extracted.get('required_experience_years', job_offer.required_experience_years or 0)
                job_offer.save()
        except Exception as e:
            # If NLP extraction fails, continue with the job offer as is
            print(f"Warning: Could not extract requirements: {str(e)}")
            pass
    
    @action(detail=True, methods=['post'])
    def process_requirements(self, request, pk=None):
        """Extract and process requirements from job description"""
        job_offer = self.get_object()
        
        description = job_offer.description
        requirements = job_offer.requirements
        
        # Extract requirements using NLP
        nlp_extractor = NLPExtractor()
        extracted = nlp_extractor.extract_job_requirements(description + " " + requirements)
        
        # Update job offer
        job_offer.extracted_requirements = extracted
        job_offer.required_skills = extracted.get('required_skills', [])
        job_offer.required_experience_years = extracted.get('required_experience_years', 0)
        job_offer.save()
        
        # Generate embedding
        vector_matcher = VectorMatcher()
        job_text = f"{description} {requirements}"
        job_offer.embedding = vector_matcher.generate_embedding(job_text)
        job_offer.save()
        
        return Response({
            'message': 'Job requirements processed',
            'extracted_requirements': extracted
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def find_matches(self, request, pk=None):
        """Find and score matching candidates for a job offer"""
        try:
            job_offer = self.get_object()
            
            # Ensure job offer has an embedding
            if not job_offer.embedding:
                # Generate embedding if missing
                vector_matcher = VectorMatcher()
                job_text = f"{job_offer.description} {job_offer.requirements}"
                job_offer.embedding = vector_matcher.generate_embedding(job_text)
                job_offer.save()
            
            # Get all active candidates
            candidates = Candidate.objects.filter(status='active')
            
            if not candidates.exists():
                return Response({
                    'count': 0,
                    'matches': [],
                    'message': 'No active candidates found'
                }, status=status.HTTP_200_OK)
            
            # Match candidates
            vector_matcher = VectorMatcher()
            matches = []
            errors = []
            
            for candidate in candidates:
                try:
                    if not candidate.embedding:
                        # Generate embedding if missing
                        if candidate.cv_text:
                            candidate.embedding = vector_matcher.generate_embedding(candidate.cv_text)
                            candidate.save()
                        else:
                            continue
                    
                    # Calculate similarity
                    similarity = vector_matcher.calculate_similarity(
                        job_offer.embedding,
                        candidate.embedding
                    )
                    
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
                    
                    # Determine weights (from settings or defaults in VectorMatcher)
                    weights = getattr(settings, 'MATCHING_WEIGHTS', None)
                    overall_percent = vector_matcher.calculate_overall_score(similarity, detailed_scores, weights)
                    
                    # Add overall (0-1) to detailed_scores for RAG
                    detailed_scores['overall_score'] = overall_percent / 100.0
                    
                    # Create or update match
                    match, created = Match.objects.get_or_create(
                        candidate=candidate,
                        job_offer=job_offer,
                        defaults={
                            'match_explanation': '',
                            'overall_score': overall_percent,
                            'technical_skill_score': detailed_scores.get('technical_skills', 0) * 100,
                            'experience_score': detailed_scores.get('experience', 0) * 100,
                            'education_score': detailed_scores.get('education', 0) * 100,
                            'soft_skill_score': detailed_scores.get('soft_skills', 0) * 100,
                        }
                    )
                    
                    # Update match scores
                    match.overall_score = overall_percent
                    match.technical_skill_score = detailed_scores.get('technical_skills', 0) * 100
                    match.experience_score = detailed_scores.get('experience', 0) * 100
                    match.education_score = detailed_scores.get('education', 0) * 100
                    match.soft_skill_score = detailed_scores.get('soft_skills', 0) * 100
                    
                    # Generate explanation
                    try:
                        rag_engine = RAGEngine()
                        explanation = rag_engine.explain_match(candidate_data, job_data, detailed_scores)
                        match.match_explanation = explanation or 'Match analysis completed.'
                    except Exception as e:
                        match.match_explanation = f'Match analysis: {similarity*100:.1f}% compatibility.'
                    
                    # Extract strengths and gaps
                    try:
                        detailed_analysis = vector_matcher.generate_matching_explanation(
                            candidate_data, job_data, detailed_scores
                        )
                        match.strengths = detailed_analysis.get('strengths', [])
                        match.gaps = detailed_analysis.get('gaps', [])
                        match.recommendations = detailed_analysis.get('recommendations', [])
                    except Exception as e:
                        match.strengths = []
                        match.gaps = []
                        match.recommendations = []
                    
                    if request.user.is_authenticated:
                        match.matched_by = request.user
                    match.save()
                    
                    matches.append(MatchSerializer(match).data)
                    
                except Exception as e:
                    errors.append(f"Error matching candidate {candidate.id}: {str(e)}")
                    continue
            
            # Sort by score
            matches.sort(key=lambda x: x['overall_score'], reverse=True)
            
            return Response({
                'count': len(matches),
                'matches': matches,
                'errors': errors if errors else None
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'detail': 'Failed to generate matches'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def rank_candidates(self, request, pk=None):
        """Rank multiple candidates against this job offer with detailed scoring and descriptions"""
        try:
            job_offer = self.get_object()
            
            # Get candidate IDs from request
            candidate_ids = request.data.get('candidate_ids', [])
            if not candidate_ids:
                return Response({'error': 'No candidate IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get candidates
            candidates = Candidate.objects.filter(id__in=candidate_ids, status='active')
            if not candidates.exists():
                return Response({'error': 'No valid active candidates found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure job offer has an embedding
            if not job_offer.embedding:
                vector_matcher = VectorMatcher()
                job_text = f"{job_offer.description} {job_offer.requirements}"
                job_offer.embedding = vector_matcher.generate_embedding(job_text)
                job_offer.save()
            
            # Initialize services
            vector_matcher = VectorMatcher()
            rag_engine = RAGEngine()
            
            ranked_candidates = []
            errors = []
            
            for candidate in candidates:
                try:
                    # Generate embedding if missing
                    if not candidate.embedding and candidate.cv_text:
                        candidate.embedding = vector_matcher.generate_embedding(candidate.cv_text)
                        candidate.save()
                    elif not candidate.embedding:
                        continue
                    
                    # Calculate similarity
                    similarity = vector_matcher.calculate_similarity(
                        job_offer.embedding,
                        candidate.embedding
                    )
                    
                    # Prepare data for detailed scoring
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
                        'required_soft_skills': request.data.get('required_soft_skills', []),
                    }
                    
                    # Calculate detailed scores
                    detailed_scores = vector_matcher.calculate_detailed_scores(candidate_data, job_data)
                    
                    # Get weights from settings
                    weights = getattr(settings, 'MATCHING_WEIGHTS', None)
                    overall_percent = vector_matcher.calculate_overall_score(similarity, detailed_scores, weights)
                    
                    # Add overall score to detailed_scores for RAG
                    detailed_scores['overall_score'] = overall_percent / 100.0
                    
                    # Generate comprehensive explanation
                    try:
                        explanation = rag_engine.explain_match(candidate_data, job_data, detailed_scores)
                    except Exception as e:
                        explanation = f'Candidate analysis: {overall_percent:.1f}% compatibility.'
                    
                    # Generate strengths and gaps analysis
                    try:
                        analysis = vector_matcher.generate_matching_explanation(
                            candidate_data, job_data, detailed_scores
                        )
                        strengths = analysis.get('strengths', [])
                        gaps = analysis.get('gaps', [])
                        recommendations = analysis.get('recommendations', [])
                    except Exception as e:
                        strengths = []
                        gaps = []
                        recommendations = []
                    
                    # Create comprehensive candidate profile
                    candidate_profile = {
                        'candidate_id': candidate.id,
                        'full_name': candidate.full_name or 'Unnamed Candidate',
                        'email': candidate.email or 'No email',
                        'current_position': candidate.current_position or 'Not specified',
                        'total_experience_years': candidate.total_experience_years,
                        'technical_skills': candidate.technical_skills or [],
                        'soft_skills': candidate.soft_skills or [],
                        'education_level': candidate.education_level or 'Not specified',
                        
                        # Scoring details
                        'overall_score': round(overall_percent, 2),
                        'similarity_score': round(similarity * 100, 2),
                        'technical_skill_score': round(detailed_scores.get('technical_skills', 0) * 100, 2),
                        'experience_score': round(detailed_scores.get('experience', 0) * 100, 2),
                        'education_score': round(detailed_scores.get('education', 0) * 100, 2),
                        'soft_skill_score': round(detailed_scores.get('soft_skills', 0) * 100, 2),
                        
                        # Analysis and explanations
                        'detailed_explanation': explanation,
                        'strengths': strengths,
                        'gaps': gaps,
                        'recommendations': recommendations,
                        
                        # Match breakdown
                        'skills_matched': len(set(candidate_data['technical_skills']) & set(job_data['required_skills'])),
                        'skills_total': len(job_data['required_skills']),
                        'soft_skills_matched': len(set(candidate_data['soft_skills']) & set(job_data.get('required_soft_skills', []))),
                        'soft_skills_total': len(job_data.get('required_soft_skills', [])),
                        
                        # Experience analysis
                        'experience_meets_requirement': candidate_data['experience_years'] >= job_data['required_experience_years'],
                        'experience_gap': max(0, job_data['required_experience_years'] - candidate_data['experience_years']),
                    }
                    
                    ranked_candidates.append(candidate_profile)
                    
                except Exception as e:
                    errors.append(f"Error processing candidate {candidate.id}: {str(e)}")
                    continue
            
            # Sort candidates by overall score (descending)
            ranked_candidates.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Add ranking positions
            for i, candidate in enumerate(ranked_candidates, 1):
                candidate['rank'] = i
                candidate['percentile'] = round((i / len(ranked_candidates)) * 100, 1)
            
            # Generate summary statistics
            if ranked_candidates:
                scores = [c['overall_score'] for c in ranked_candidates]
                summary_stats = {
                    'total_candidates': len(ranked_candidates),
                    'average_score': round(sum(scores) / len(scores), 2),
                    'highest_score': ranked_candidates[0]['overall_score'],
                    'lowest_score': ranked_candidates[-1]['overall_score'],
                    'median_score': round(sorted(scores)[len(scores) // 2], 2),
                    'candidates_above_80': len([c for c in ranked_candidates if c['overall_score'] >= 80]),
                    'candidates_above_60': len([c for c in ranked_candidates if c['overall_score'] >= 60]),
                }
            else:
                summary_stats = {}
            
            return Response({
                'job_offer': {
                    'id': job_offer.id,
                    'title': job_offer.title,
                    'location': job_offer.location,
                    'required_skills': job_offer.required_skills or [],
                    'required_experience_years': job_offer.required_experience_years,
                },
                'ranking_summary': summary_stats,
                'ranked_candidates': ranked_candidates,
                'errors': errors if errors else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'detail': 'Failed to rank candidates'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MatchViewSet(viewsets.ModelViewSet):
    """API endpoint for matches"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def explanation(self, request, pk=None):
        """Get detailed explanation of a match"""
        match = self.get_object()
        
        return Response({
            'overall_score': match.overall_score,
            'explanation': match.match_explanation,
            'strengths': match.strengths,
            'gaps': match.gaps,
            'recommendations': match.recommendations,
        })
    
    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """Generate executive summary for a match"""
        match = self.get_object()
        
        candidate_data = {
            'full_name': match.candidate.full_name,
            'technical_skills': match.candidate.technical_skills,
            'experience_years': match.candidate.total_experience_years,
            'current_position': match.candidate.current_position,
            'education_level': match.candidate.education_level,
            'soft_skills': match.candidate.soft_skills,
        }
        
        job_data = {
            'title': match.job_offer.title,
            'required_skills': match.job_offer.required_skills,
            'required_experience_years': match.job_offer.required_experience_years,
        }
        
        rag_engine = RAGEngine()
        summary = rag_engine.generate_candidate_summary(candidate_data, job_data)
        
        # Create generated document
        GeneratedDocument.objects.create(
            document_type='candidate_summary',
            candidate=match.candidate,
            job_offer=match.job_offer,
            match=match,
            content=summary,
            generated_by=request.user
        )
        
        return Response({'summary': summary}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def generate_email(self, request, pk=None):
        """Generate contact email for a candidate"""
        match = self.get_object()
        
        candidate_data = {
            'full_name': match.candidate.full_name,
            'technical_skills': match.candidate.technical_skills,
        }
        
        job_data = {
            'title': match.job_offer.title,
        }
        
        rag_engine = RAGEngine()
        email_content = rag_engine.generate_email_content(
            candidate_data,
            job_data,
            match.overall_score / 100
        )
        
        # Create generated document
        GeneratedDocument.objects.create(
            document_type='contact_email',
            candidate=match.candidate,
            job_offer=match.job_offer,
            match=match,
            content=email_content,
            generated_by=request.user
        )
        
        return Response({'email_content': email_content}, status=status.HTTP_200_OK)


class ConversationViewSet(viewsets.ModelViewSet):
    """API endpoint for conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def ask(self, request, pk=None):
        """Ask a question about a candidate in a conversation"""
        conversation = self.get_object()
        question = request.data.get('question', '')
        
        if not question:
            return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get candidate data
        candidate = conversation.candidate
        if not candidate:
            return Response({'error': 'No candidate in conversation'}, status=status.HTTP_400_BAD_REQUEST)
        
        candidate_data = {
            'technical_skills': candidate.technical_skills,
            'experience_years': candidate.total_experience_years,
            'education_level': candidate.education_level,
            'soft_skills': candidate.soft_skills,
            'availability': candidate.availability,
        }
        
        # Answer question using RAG
        rag_engine = RAGEngine()
        answer = rag_engine.answer_question(question, candidate_data)
        
        # Save messages
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=question
        )
        
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=answer
        )
        
        return Response({'answer': answer}, status=status.HTTP_200_OK)


class CVViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for CVs"""
    queryset = CV.objects.all()
    serializer_class = CVSerializer
    permission_classes = [IsAuthenticated]

