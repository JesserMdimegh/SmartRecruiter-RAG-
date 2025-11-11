"""
Vector Matching Service
Level 2: Vector Matching with Sentence-BERT and Elasticsearch
"""

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import numpy as np
    from scipy.spatial.distance import cosine
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    cosine = None

from typing import List, Dict, Any, Tuple


class VectorMatcher:
    """Match candidates and job offers using vector embeddings"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-mpnet-base-v2'):
        """
        Initialize the Vector Matcher
        
        Args:
            model_name: Name of the Sentence-BERT model to use
        """
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        else:
            print("sentence-transformers not installed. Using mock embeddings.")
            self.model = None
            self.model_name = model_name
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.model:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            # Mock embedding for testing
            return [0.1] * 768
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        if not NUMPY_AVAILABLE or not embedding1 or not embedding2:
            # Mock similarity for testing
            return 0.75
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        similarity = 1 - cosine(vec1, vec2)
        
        return float(similarity)
    
    def match_candidate_to_job(self, candidate_text: str, job_text: str) -> float:
        """
        Calculate matching score between a candidate and a job
        
        Args:
            candidate_text: Combined candidate information (CV, skills, experience)
            job_text: Job description and requirements
            
        Returns:
            Matching score between 0 and 1
        """
        # Generate embeddings
        candidate_embedding = self.model.encode(candidate_text)
        job_embedding = self.model.encode(job_text)
        
        # Calculate similarity
        similarity = 1 - cosine(candidate_embedding, job_embedding)
        
        return float(similarity)
    
    def batch_match(self, candidate_texts: List[str], job_text: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Match multiple candidates against a job offer
        
        Args:
            candidate_texts: List of candidate information texts
            job_text: Job description
            top_k: Number of top matches to return
            
        Returns:
            List of (candidate_index, score) tuples sorted by score
        """
        # Generate embeddings
        job_embedding = self.model.encode(job_text)
        candidate_embeddings = self.model.encode(candidate_texts)
        
        # Calculate similarities
        scores = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarity = 1 - cosine(job_embedding, candidate_emb)
            scores.append((i, float(similarity)))
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def calculate_detailed_scores(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate detailed matching scores for different aspects
        
        Args:
            candidate_data: Dictionary with candidate information
            job_data: Dictionary with job information
            
        Returns:
            Dictionary with various matching scores
        """
        scores = {}
        
        # Technical skills score
        candidate_skills = set(candidate_data.get('technical_skills', []))
        job_skills = set(job_data.get('required_skills', []))
        
        if job_skills:
            # Normalize skills for comparison (lowercase, remove spaces)
            candidate_skills_normalized = {s.lower().strip() for s in candidate_skills if s}
            job_skills_normalized = {s.lower().strip() for s in job_skills if s}
            
            # Calculate match
            matched_skills = candidate_skills_normalized & job_skills_normalized
            skills_match = len(matched_skills) / len(job_skills_normalized) if job_skills_normalized else 0.0
            scores['technical_skills'] = skills_match
        else:
            # If job has no required skills, give partial credit based on candidate having skills
            # This prevents 0% when job requirements weren't specified
            if candidate_skills:
                scores['technical_skills'] = 0.5  # Partial credit
            else:
                scores['technical_skills'] = 0.0
        
        # Experience score
        candidate_exp = candidate_data.get('experience_years', 0)
        job_exp_required = job_data.get('required_experience_years', 0)
        
        if job_exp_required > 0:
            exp_ratio = min(candidate_exp / job_exp_required, 1.0)
            scores['experience'] = exp_ratio
        else:
            scores['experience'] = 1.0
        
        # Education score (simple binary for now)
        candidate_education = candidate_data.get('education_level', '').lower()
        required_education = job_data.get('required_education', '').lower()
        
        if required_education:
            # Simple matching logic
            if required_education in candidate_education:
                scores['education'] = 1.0
            else:
                scores['education'] = 0.5
        else:
            scores['education'] = 1.0
        
        # Soft skills score (cosine similarity on text)
        candidate_soft = ' '.join(candidate_data.get('soft_skills', []))
        job_soft = job_data.get('required_soft_skills', '')
        
        if candidate_soft and job_soft:
            candidate_emb = self.model.encode(candidate_soft)
            job_emb = self.model.encode(job_soft)
            scores['soft_skills'] = float(1 - cosine(candidate_emb, job_emb))
        else:
            scores['soft_skills'] = 0.0
        
        return scores

    def calculate_overall_score(self, similarity: float, detailed_scores: Dict[str, float], weights: Dict[str, float] | None = None) -> float:
        """Combine similarity and detailed scores into a single 0-100 score.

        Args:
            similarity: cosine similarity in [0, 1]
            detailed_scores: dict containing 'technical_skills', 'experience', 'education', 'soft_skills' in [0, 1]
            weights: optional dict overriding default weights. Keys: 'similarity', 'technical', 'experience', 'education', 'soft_skills'.

        Returns:
            Overall score on a 0-100 scale.
        """
        # Defaults if settings not provided
        default_weights = {
            'similarity': 0.5,
            'technical': 0.3,
            'experience': 0.15,
            'education': 0.05,
            'soft_skills': 0.0,
        }
        w = {**default_weights, **(weights or {})}

        tech = detailed_scores.get('technical_skills', 0.0)
        exp = detailed_scores.get('experience', 0.0)
        edu = detailed_scores.get('education', 0.0)
        soft = detailed_scores.get('soft_skills', 0.0)

        # Weighted sum
        overall_0_1 = (
            w['similarity'] * max(0.0, min(1.0, similarity)) +
            w['technical'] * max(0.0, min(1.0, tech)) +
            w['experience'] * max(0.0, min(1.0, exp)) +
            w['education'] * max(0.0, min(1.0, edu)) +
            w['soft_skills'] * max(0.0, min(1.0, soft))
        )

        # Normalize if weights don't sum to 1
        total_w = sum(w.values()) or 1.0
        overall_0_1 /= total_w
        return float(round(overall_0_1 * 100, 2))
    
    def generate_matching_explanation(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate human-readable explanation of the match
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            scores: Detailed matching scores
            
        Returns:
            Dictionary with strengths, gaps, and recommendations
        """
        strengths = []
        gaps = []
        recommendations = []
        
        # Analyze technical skills
        candidate_skills = set(candidate_data.get('technical_skills', []))
        job_skills = set(job_data.get('required_skills', []))
        
        matched_skills = candidate_skills & job_skills
        missing_skills = job_skills - candidate_skills
        
        for skill in matched_skills:
            strengths.append("+ Has required skill: " + skill)
        
        for skill in missing_skills:
            gaps.append("- Missing skill: " + skill)
            recommendations.append("Consider candidates with " + skill + " or provide training")
        
        # Analyze experience
        candidate_exp = candidate_data.get('experience_years', 0)
        job_exp_required = job_data.get('required_experience_years', 0)
        
        if candidate_exp >= job_exp_required:
            strengths.append("+ Meets experience requirement: " + str(candidate_exp) + " years")
        else:
            gaps.append("- Experience gap: " + str(candidate_exp) + " years (required: " + str(job_exp_required) + ")")
            if candidate_exp >= job_exp_required * 0.7:
                recommendations.append("Candidate has sufficient related experience")
        
        # Overall recommendation
        overall_score = sum(scores.values()) / len(scores)
        
        if overall_score >= 0.8:
            recommendations.insert(0, "Highly recommended candidate")
        elif overall_score >= 0.6:
            recommendations.insert(0, "Good candidate with potential")
        else:
            recommendations.insert(0, "Consider alternative candidates")
        
        return {
            'strengths': strengths,
            'gaps': gaps,
            'recommendations': recommendations,
            'overall_score': overall_score,
        }

