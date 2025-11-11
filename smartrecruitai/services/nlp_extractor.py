"""
NLP Extraction Service
Level 1: Extraction & Understanding with BERT/JobBERT
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

from typing import Dict, List, Any
import json


class NLPExtractor:
    """Extract and understand semantic information from CVs and job descriptions"""
    
    def __init__(self):
        # Load spaCy model for basic NLP
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except OSError:
                print("French spaCy model not found. Install with: python -m spacy download fr_core_news_sm")
                self.nlp = None
        else:
            print("spaCy not installed. Using simple text processing.")
            self.nlp = None
        
        # Skill normalization dictionary
        self.skill_normalization = {
            "ML": "Machine Learning",
            "DL": "Deep Learning",
            "JS": "JavaScript",
            "TS": "TypeScript",
            "AI": "Artificial Intelligence",
            "NLP": "Natural Language Processing",
            "CV": "Computer Vision",
            "AWS": "Amazon Web Services",
            "AZ": "Azure",
            "DB": "Database",
        }
    
    def extract_cv_data(self, cv_text: str) -> Dict[str, Any]:
        """
        Extract structured data from CV text using NLP
        
        Args:
            cv_text: Raw text extracted from CV
            
        Returns:
            Dictionary with extracted information
        """
        if not self.nlp:
            return self._extract_simple(cv_text)
        
        doc = self.nlp(cv_text)
        
        # Extract named entities
        entities = [ent.text for ent in doc.ents]
        
        # Extract technical skills (using rules + patterns)
        technical_skills = self._extract_technical_skills(cv_text, doc)
        
        # Extract soft skills
        soft_skills = self._extract_soft_skills(cv_text, doc)
        
        # Extract experience
        experience_years = self._extract_experience_years(cv_text, doc)
        
        # Extract education
        education = self._extract_education(cv_text, doc)
        
        # Extract certifications
        certifications = self._extract_certifications(cv_text, doc)
        
        # Extract languages
        languages = self._extract_languages(cv_text, doc)
        
        return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'experience_years': experience_years,
            'education': education,
            'certifications': certifications,
            'languages': languages,
            'entities': entities,
        }
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Extract requirements from job description
        
        Args:
            job_description: Job description text
            
        Returns:
            Dictionary with extracted requirements
        """
        if not self.nlp:
            return self._extract_simple(job_description)
        
        doc = self.nlp(job_description)
        
        required_skills = self._extract_technical_skills(job_description, doc)
        required_experience = self._extract_experience_years(job_description, doc)
        required_education = self._extract_education(job_description, doc)
        
        return {
            'required_skills': required_skills,
            'required_experience_years': required_experience,
            'required_education': required_education,
            'soft_skills': self._extract_soft_skills(job_description, doc),
            'certifications': self._extract_certifications(job_description, doc),
        }
    
    def _extract_technical_skills(self, text: str, doc=None) -> List[str]:
        """Extract technical skills and technologies"""
        # Common technical keywords
        tech_keywords = [
            # Languages / runtimes
            'python', 'java', 'javascript', 'typescript', 'go', 'golang', 'rust', 'c#', 'c++', 'dotnet', '.net',
            # Frontend
            'react', 'vue', 'angular', 'next.js', 'nuxt', 'svelte', 'redux',
            # Backend / frameworks
            'node', 'express', 'nestjs', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'laravel',
            # ML / Data
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'xgboost',
            # Databases
            'postgresql', 'postgres', 'mysql', 'mssql', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'neo4j',
            # DevOps / Cloud
            'docker', 'docker-compose', 'kubernetes', 'helm', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            # Messaging / streaming
            'kafka', 'rabbitmq', 'sqs', 'sns',
            # APIs / protocols
            'rest', 'graphql', 'grpc', 'websocket',
            # Testing / quality
            'pytest', 'unittest', 'junit', 'tdd', 'bdd',
            # Observability
            'prometheus', 'grafana', 'elk', 'logstash', 'kibana',
            # CI/CD & tooling
            'git', 'github actions', 'gitlab ci', 'jenkins', 'ci/cd',
            # Methods
            'agile', 'scrum',
            # AI topics
            'machine learning', 'deep learning', 'nlp', 'cv', 'computer vision', 'data science',
            # Big data
            'big data', 'spark', 'hadoop',
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                # Normalize the skill
                normalized_key = keyword.upper().replace(' ', '')
                normalized = self.skill_normalization.get(normalized_key, keyword.title())
                found_skills.append(normalized)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_skills))
    
    def _extract_soft_skills(self, text: str, doc=None) -> List[str]:
        """Extract soft skills"""
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem-solving',
            'creativity', 'adaptability', 'time management', 'organization',
            'critical thinking', 'collaboration', 'empathy', 'motivation',
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(dict.fromkeys(found_skills))
    
    def _extract_experience_years(self, text: str, doc=None) -> float:
        """Extract years of experience"""
        import re
        
        t = text.lower()
        # Normalize separators
        t = t.replace('années', 'annee').replace('année', 'annee').replace('ans', 'annee').replace('years', 'year')
        
        # Prefer numbers near "experience" keywords (context window)
        context_matches = []
        for m in re.finditer(r'experienc|expérienc|experience', t):
            start = max(0, m.start() - 40)
            end = min(len(t), m.end() + 40)
            window = t[start:end]
            ctx_nums = re.findall(r'(\d{1,2})\s*(?:\+|plus)?\s*(?:year|annee)', window)
            context_matches += ctx_nums
        if context_matches:
            try:
                return float(max(int(n) for n in context_matches))
            except Exception:
                pass
        
        # Global patterns: "3+ years", "at least 2 years", "2-4 years", "minimum 5 years"
        patterns = [
            r'(\d{1,2})\s*(?:\+|plus)?\s*(?:year|annee)',
            r'(?:at\s+least|min(?:imum)?)\s*(\d{1,2})\s*(?:year|annee)',
            r'(\d{1,2})\s*[-to]{1,3}\s*(\d{1,2})\s*(?:year|annee)',
        ]
        values: List[float] = []
        for pattern in patterns:
            for m in re.findall(pattern, t):
                if isinstance(m, tuple):
                    try:
                        a, b = int(m[0]), int(m[1])
                        values.append(float(max(a, b)))
                    except Exception:
                        continue
                else:
                    try:
                        values.append(float(int(m)))
                    except Exception:
                        continue
        if values:
            return max(values)
         
        return 0.0
    
    def _extract_education(self, text: str, doc=None) -> List[str]:
        """Extract education information"""
        education_keywords = [
            'master', 'licence', 'bachelor', 'doctorate', 'phd',
            'bac', 'diploma', 'degree', 'graduated', 'university',
            'école', 'school', 'ingénieur', 'engineer', 'engineering',
        ]
        
        text_lower = text.lower()
        found = []
        
        # Extract education lines
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                found.append(line.strip())
        
        return found
    
    def _extract_certifications(self, text: str, doc=None) -> List[str]:
        """Extract certifications"""
        cert_keywords = [
            'certified', 'certification', 'certificat', 'certificat',
            'aws certified', 'azure', 'google cloud', 'cissp', 'pmp',
            'scrum master', 'agile', 'iso',
        ]
        
        text_lower = text.lower()
        found = []
        
        for line in text.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in cert_keywords):
                found.append(line.strip())
        
        return found
    
    def _extract_languages(self, text: str, doc=None) -> List[str]:
        """Extract languages and proficiency levels"""
        lang_keywords = [
            'english', 'french', 'spanish', 'german', 'italian',
            'native', 'fluent', 'intermediate', 'beginner',
            'bilingual', 'toefl', 'ielts',
        ]
        
        text_lower = text.lower()
        found = []
        
        for keyword in lang_keywords:
            if keyword in text_lower:
                found.append(keyword.title())
        
        return list(dict.fromkeys(found))
    
    def _extract_simple(self, text: str) -> Dict[str, Any]:
        """Simple extraction fallback when spaCy is not available"""
        return {
            'technical_skills': self._extract_technical_skills(text),
            'soft_skills': self._extract_soft_skills(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text),
            'certifications': self._extract_certifications(text),
            'languages': self._extract_languages(text),
            'entities': [],
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name"""
        skill_upper = skill.upper()
        return self.skill_normalization.get(skill_upper, skill.title())

