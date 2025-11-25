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
from pathlib import Path
import json
from django.conf import settings
import unicodedata


class VectorMatcher:
    """Match candidates and job offers using vector embeddings"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-mpnet-base-v2'):
        """
        Initialize the Vector Matcher
        
        Args:
            model_name: Name of the Sentence-BERT model to use
        """
        # Resolve model name in three steps:
        # 1. If a fine-tuned matcher path exists and is a directory, prefer it.
        # 2. Otherwise, use the SENTENCE_BERT_MODEL setting if defined.
        # 3. Finally, fall back to the provided default value.
        try:
            fine_tuned_path = getattr(settings, 'FINE_TUNED_MATCHER_PATH', None)
            if fine_tuned_path and Path(fine_tuned_path).exists():
                model_name = fine_tuned_path
            else:
                configured_name = getattr(settings, 'SENTENCE_BERT_MODEL', None)
                if configured_name:
                    model_name = configured_name
        except Exception:
            # If settings are not available (e.g. in isolated tests), keep the original value.
            pass

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
        
        # Technical skills score (enhanced matching with synonyms and variations)
        candidate_skills = set(skill.lower().strip() for skill in candidate_data.get('technical_skills', []) if skill)
        job_skills = set(skill.lower().strip() for skill in job_data.get('required_skills', []) if skill)
        
        if job_skills:
            # Enhanced skill matching with synonyms and variations
            skill_synonyms = {
                # Programming languages
                'javascript': ['js', 'ecmascript', 'es6', 'es2015'],
                'typescript': ['ts'],
                'python': ['py', 'python3'],
                'java': ['jvm', 'jdk'],
                'c#': ['csharp', 'c-sharp', '.net'],
                'c++': ['cpp', 'c-plus-plus'],
                'php': ['hypertext preprocessor'],
                'ruby': ['rails', 'ruby on rails'],
                'go': ['golang'],
                'swift': ['ios'],
                'kotlin': ['android'],
                'rust': ['rs'],
                
                # Web technologies
                'html': ['html5', 'markup'],
                'css': ['css3', 'sass', 'scss', 'less', 'stylus'],
                'react': ['reactjs', 'react.js', 'jsx'],
                'angular': ['angularjs', 'angular.js', 'ng'],
                'vue': ['vuejs', 'vue.js', 'vuejs'],
                'node.js': ['node', 'nodejs', 'backend javascript'],
                'express': ['expressjs', 'express.js'],
                'django': ['python django'],
                'flask': ['python flask'],
                'laravel': ['php laravel'],
                'spring': ['spring boot', 'spring framework'],
                'asp.net': ['.net core', 'aspnet'],
                
                # Databases
                'sql': ['mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'mssql'],
                'nosql': ['mongodb', 'cassandra', 'redis', 'elasticsearch', 'dynamodb'],
                'postgresql': ['postgres', 'psql'],
                'mysql': ['mariadb'],
                'mongodb': ['mongo', 'nosql mongodb'],
                'redis': ['cache', 'in-memory database'],
                
                # Cloud platforms
                'aws': ['amazon web services', 'ec2', 's3', 'lambda', 'rds'],
                'azure': ['microsoft azure', 'azure cloud'],
                'gcp': ['google cloud platform', 'google cloud'],
                'docker': ['containers', 'containerization'],
                'kubernetes': ['k8s', 'orchestration'],
                
                # DevOps tools
                'jenkins': ['ci/cd', 'continuous integration'],
                'git': ['version control', 'github', 'gitlab', 'bitbucket'],
                'terraform': ['infrastructure as code', 'iac'],
                'ansible': ['automation', 'configuration management'],
                
                # Frontend technologies
                'bootstrap': ['css framework', 'responsive design'],
                'tailwind': ['tailwind css', 'utility-first css'],
                'webpack': ['bundler', 'module bundler'],
                'babel': ['transpiler', 'javascript transpiler'],
                
                # Mobile development
                'ios': ['iphone', 'ipad', 'objective-c'],
                'android': ['android studio', 'mobile development'],
                'react native': ['cross-platform mobile'],
                'flutter': ['dart', 'cross-platform'],
                
                # Data science/AI
                'tensorflow': ['deep learning', 'neural networks'],
                'pytorch': ['machine learning', 'ai'],
                'scikit-learn': ['sklearn', 'machine learning library'],
                'pandas': ['data analysis', 'data manipulation'],
                'numpy': ['numerical computing', 'scientific computing'],
                
                # Testing
                'jest': ['javascript testing', 'unit testing'],
                'pytest': ['python testing'],
                'junit': ['java testing'],
                'selenium': ['automated testing', 'web testing'],
                
                # Other technologies
                'rest': ['rest api', 'restful', 'web api'],
                'graphql': ['gql', 'query language'],
                'microservices': ['microservice architecture'],
                'agile': ['scrum', 'kanban', 'iterative development'],
                'linux': ['unix', 'ubuntu', 'centos', 'debian'],
                'windows': ['microsoft windows', 'win32'],
                'macos': ['os x', 'mac', 'apple os']
            }
            
            # Expand job skills with synonyms
            expanded_job_skills = set(job_skills)
            for skill in job_skills:
                if skill in skill_synonyms:
                    expanded_job_skills.update(skill_synonyms[skill])
            
            # Expand candidate skills with synonyms
            expanded_candidate_skills = set(candidate_skills)
            for skill in candidate_skills:
                if skill in skill_synonyms:
                    expanded_candidate_skills.update(skill_synonyms[skill])
            
            # Calculate matches with expanded skill sets
            matched = expanded_candidate_skills & expanded_job_skills
            
            # Weight exact matches higher than synonym matches
            exact_matches = candidate_skills & job_skills
            synonym_matches = matched - exact_matches
            
            # Calculate score with weighting
            if expanded_job_skills:
                exact_score = len(exact_matches) / len(expanded_job_skills) * 1.0  # Full weight for exact matches
                synonym_score = len(synonym_matches) / len(expanded_job_skills) * 0.7  # 70% weight for synonym matches
                scores['technical_skills'] = min(1.0, exact_score + synonym_score)
            else:
                scores['technical_skills'] = 0.0
        else:
            # If job has no required skills, give partial credit based on candidate having skills
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
        
        scores['education'] = self._calculate_education_score(
            candidate_data.get('education_level'),
            job_data.get('required_education')
        )
        
        # Soft skills score (enhanced matching)
        candidate_soft = set(skill.lower().strip() for skill in candidate_data.get('soft_skills', []) if skill)
        job_soft = set(skill.lower().strip() for skill in job_data.get('required_soft_skills', []) if skill)
        
        if job_soft:
            # Calculate soft skills match ratio
            matched_soft = candidate_soft & job_soft
            soft_score = len(matched_soft) / len(job_soft) if job_soft else 0.0
            scores['soft_skills'] = soft_score
        else:
            # If job has no soft skills requirements, give partial credit for having soft skills
            if candidate_soft:
                scores['soft_skills'] = 0.3  # Partial credit for having soft skills
            else:
                scores['soft_skills'] = 0.0
        
        return scores

    def _normalize_education_text(self, education_data: Any) -> str:
        if not education_data:
            return ''
        if isinstance(education_data, list):
            return ' '.join(str(item) for item in education_data if item)
        if isinstance(education_data, str):
            text = education_data.strip()
            if text.startswith('[') and text.endswith(']'):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        return ' '.join(str(item) for item in parsed if item)
                except json.JSONDecodeError:
                    pass
            return text
        return str(education_data)

    def _infer_degree_level(self, education_data: Any) -> float:
        text = unicodedata.normalize('NFKD', self._normalize_education_text(education_data).lower())
        text = text.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        if not text:
            return 0.0

        degree_levels = [
            (4.0, ['doctor of philosophy', 'phd', 'doctorate', 'dr.', 'doctor of science']),
            (3.5, ['master', 'msc', 'm.s.', 'ma ', 'mba', 'ingenieur', 'ingénieur', 'engineering degree']),
            (2.5, ['bachelor', 'licence', 'license', 'licenciatura', 'bsc', 'ba', 'undergraduate degree']),
            (1.5, ['associate', 'dut', 'bts', 'deug']),
            (1.2, ['diploma', 'diplome', 'certificate', 'certificat']),
            (0.7, ['high school', 'secondary school', 'lycee', 'lycée', 'baccalaureat', 'bac'])
        ]

        for level, keywords in degree_levels:
            for keyword in keywords:
                if keyword in text:
                    return level
        return 0.0

    def _calculate_education_score(self, candidate_education: Any, required_education: Any) -> float:
        candidate_level = self._infer_degree_level(candidate_education)
        required_level = self._infer_degree_level(required_education)

        if required_level > 0:
            if candidate_level <= 0:
                score = 0.2
            elif candidate_level >= required_level:
                bonus = min(0.2, (candidate_level - required_level) * 0.1)
                score = min(1.0, 0.85 + bonus)
            else:
                ratio = candidate_level / required_level
                score = max(0.3, ratio)
        else:
            if candidate_level > 0:
                score = min(1.0, 0.6 + (candidate_level / 5))
            else:
                score = 0.4

        return float(round(max(0.0, min(score, 1.0)), 2))

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

