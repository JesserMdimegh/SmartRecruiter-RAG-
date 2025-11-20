"""
NLP Extraction Service
Level 1: Extraction & Understanding with BERT/JobBERT
"""

import re
from typing import Dict, Any, List

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
        
        # Extract professional links
        professional_links = self._extract_professional_links(cv_text, doc)
        
        return {
            'technical_skills': technical_skills,
            'soft_skills': soft_skills,
            'experience_years': experience_years,
            'education': education,
            'certifications': certifications,
            'languages': languages,
            'professional_links': professional_links,
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
            # Leadership & Management
            'leadership', 'management', 'team leadership', 'project management', 'people management',
            'delegation', 'mentoring', 'coaching', 'supervision', 'strategic planning',
            
            # Communication
            'communication', 'public speaking', 'presentation skills', 'negotiation', 'persuasion',
            'active listening', 'written communication', 'verbal communication', 'interpersonal skills',
            
            # Teamwork & Collaboration
            'teamwork', 'collaboration', 'team player', 'cross-functional collaboration', 'partnership',
            'relationship building', 'networking', 'conflict resolution', 'consensus building',
            
            # Problem-Solving & Critical Thinking
            'problem-solving', 'critical thinking', 'analytical thinking', 'logical reasoning',
            'troubleshooting', 'decision making', 'risk assessment', 'root cause analysis',
            
            # Creativity & Innovation
            'creativity', 'innovation', 'creative thinking', 'out of the box thinking', 'ideation',
            'design thinking', 'adaptability', 'flexibility', 'resourcefulness',
            
            # Time Management & Organization
            'time management', 'organization', 'planning', 'prioritization', 'multitasking',
            'deadline management', 'project coordination', 'workflow optimization', 'scheduling',
            
            # Personal Attributes
            'motivation', 'self-motivated', 'initiative', 'proactive', 'entrepreneurial mindset',
            'resilience', 'stress management', 'emotional intelligence', 'self-awareness',
            
            # Work Ethic & Professionalism
            'attention to detail', 'detail-oriented', 'quality focused', 'results oriented',
            'accountability', 'responsibility', 'professionalism', 'work ethic', 'reliability',
            
            # Customer & Client Focus
            'customer service', 'client relationship', 'customer focused', 'stakeholder management',
            'customer satisfaction', 'user experience', 'empathy', 'patience', 'understanding needs',
            
            # Learning & Development
            'continuous learning', 'fast learner', 'quick study', 'knowledge sharing', 'training',
            'development', 'coaching', 'mentorship', 'skill development', 'growth mindset',
            
            # Cultural & Social Skills
            'cultural awareness', 'diversity and inclusion', 'social skills', 'etiquette',
            'diplomacy', 'tact', 'discretion', 'confidentiality', 'professional conduct'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        # Check for each soft skill
        for skill in soft_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Also check for common variations and synonyms
        skill_variations = {
            'problem solving': 'problem-solving',
            'critical thinking': 'critical thinking',
            'time management': 'time management',
            'attention to detail': 'attention to detail',
            'detail oriented': 'attention to detail',
            'customer focused': 'customer service',
            'self motivated': 'self-motivated',
            'quick learner': 'fast learner',
            'team player': 'teamwork',
            'hard working': 'work ethic',
            'professional attitude': 'professionalism'
        }
        
        for variation, standard in skill_variations.items():
            if variation in text_lower and standard.title() not in found_skills:
                found_skills.append(standard.title())
        
        # Remove duplicates while preserving order
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
        """Extract languages and proficiency levels with enhanced patterns"""
        # Comprehensive language patterns
        language_patterns = {
            # English variations
            'english': [
                r'\benglish\b', r'\benglis[h]\b', r'\beng\b', r'\ben\b',
                r'\benglish\s+(?:language|lang)\b', r'\bnative\s+english\b',
                r'\bfluent\s+english\b', r'\benglish\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # French variations
            'french': [
                r'\bfrench\b', r'\bfran[çc]ais\b', r'\bfrançais\b', r'\bfr\b', r'\bfr\b',
                r'\bfrench\s+(?:language|lang)\b', r'\bnative\s+french\b',
                r'\bfluent\s+french\b', r'\bfrench\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Spanish variations
            'spanish': [
                r'\bspanish\b', r'\bespañol\b', r'\bespanol\b', r'\bes\b', r'\bsp\b',
                r'\bspanish\s+(?:language|lang)\b', r'\bnative\s+spanish\b',
                r'\bfluent\s+spanish\b', r'\bspanish\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # German variations
            'german': [
                r'\bgerman\b', r'\bdeutsch\b', r'\bde\b', r'\bge\b',
                r'\bgerman\s+(?:language|lang)\b', r'\bnative\s+german\b',
                r'\bfluent\s+german\b', r'\bgerman\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Italian variations
            'italian': [
                r'\bitalian\b', r'\bitaliano\b', r'\bit\b', r'\bitalia\b',
                r'\bitalian\s+(?:language|lang)\b', r'\bnative\s+italian\b',
                r'\bfluent\s+italian\b', r'\bitalian\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Portuguese variations
            'portuguese': [
                r'\bportuguese\b', r'\bportugu[êe]s\b', r'\bpt\b', r'\bpor\b',
                r'\bportuguese\s+(?:language|lang)\b', r'\bnative\s+portuguese\b',
                r'\bfluent\s+portuguese\b', r'\bportuguese\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Dutch variations
            'dutch': [
                r'\bdutch\b', r'\bnederlands\b', r'\bnl\b', r'\bned\b',
                r'\bdutch\s+(?:language|lang)\b', r'\bnative\s+dutch\b',
                r'\bfluent\s+dutch\b', r'\bdutch\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Arabic variations
            'arabic': [
                r'\barabic\b', r'\bالعربية\b', r'\barabe\b', r'\bar\b',
                r'\barabic\s+(?:language|lang)\b', r'\bnative\s+arabic\b',
                r'\bfluent\s+arabic\b', r'\barabic\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Chinese variations
            'chinese': [
                r'\bchinese\b', r'\bmandarin\b', r'\bcantonese\b', r'\bzh\b', r'\b中文\b',
                r'\bchinese\s+(?:language|lang)\b', r'\bnative\s+chinese\b',
                r'\bfluent\s+chinese\b', r'\bchinese\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Japanese variations
            'japanese': [
                r'\bjapanese\b', r'\bnihongo\b', r'\bja\b', r'\b日本語\b',
                r'\bjapanese\s+(?:language|lang)\b', r'\bnative\s+japanese\b',
                r'\bfluent\s+japanese\b', r'\bjapanese\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Russian variations
            'russian': [
                r'\brussian\b', r'\brusskiy\b', r'\bru\b', r'\bрусский\b',
                r'\brussian\s+(?:language|lang)\b', r'\bnative\s+russian\b',
                r'\bfluent\s+russian\b', r'\brussian\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ],
            # Hindi variations
            'hindi': [
                r'\bhindi\b', r'\bhi\b', r'\bहिन्दी\b',
                r'\bhindi\s+(?:language|lang)\b', r'\bnative\s+hindi\b',
                r'\bfluent\s+hindi\b', r'\bhindi\s+(?:native|fluent|proficient|advanced|intermediate|basic)\b'
            ]
        }
        
        # Proficiency level patterns
        proficiency_patterns = {
            'native': [r'\bnative\b', r'\bnative\s+speaker\b', r'\bnative\s+level\b', r'\bmother\s+tongue\b'],
            'fluent': [r'\bfluent\b', r'\bfluent\s+speaker\b', r'\bfluent\s+level\b', r'\bfully\s+proficient\b'],
            'proficient': [r'\bproficient\b', r'\bprofessional\b', r'\bworking\s+proficiency\b'],
            'advanced': [r'\badvanced\b', r'\badvanced\s+level\b', r'\bexpert\b'],
            'intermediate': [r'\bintermediate\b', r'\bintermediate\s+level\b', r'\bconversational\b'],
            'basic': [r'\bbasic\b', r'\bbasic\s+level\b', r'\bbeginner\b', r'\belementary\b']
        }
        
        text_lower = text.lower()
        found_languages = []
        
        # Extract languages with proficiency
        for language, patterns in language_patterns.items():
            language_found = False
            proficiency = None
            
            # Check if language is mentioned
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    language_found = True
                    break
            
            if language_found:
                # Find proficiency level for this language
                for prof_level, prof_patterns in proficiency_patterns.items():
                    # Look for proficiency patterns near the language name
                    language_context = re.findall(rf'[^.]*{language}[^.]*', text_lower, re.IGNORECASE)
                    for context in language_context:
                        for prof_pattern in prof_patterns:
                            if re.search(prof_pattern, context):
                                proficiency = prof_level
                                break
                        if proficiency:
                            break
                
                # Format language with proficiency
                if proficiency:
                    found_languages.append(f"{language.title()} ({proficiency.title()})")
                else:
                    found_languages.append(language.title())
        
        # Also extract standalone proficiency indicators (for languages section headers)
        standalone_proficiencies = []
        for prof_level, patterns in proficiency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    standalone_proficiencies.append(prof_level.title())
                    break
        
        # Combine and remove duplicates
        all_languages = found_languages + standalone_proficiencies
        return list(dict.fromkeys(all_languages))
    
    def _extract_professional_links(self, text: str, doc=None) -> Dict[str, List[str]]:
        """Extract GitHub, GitLab, LinkedIn, and portfolio links from CV text"""
        links = {
            'github': [],
            'gitlab': [],
            'linkedin': [],
            'portfolio': []
        }
        
        # Convert to lowercase for pattern matching
        text_lower = text.lower()
        
        # GitHub patterns
        github_patterns = [
            r'https?://(?:www\.)?github\.com/[\w\-\.]+/?(?:[\w\-\/]*)?',
            r'github\.com/[\w\-\.]+/?(?:[\w\-\/]*)?',
            r'@[\w\-\.]+(?:\s+|\n)*(?:github|gh)',
            r'github:\s*[\w\-\.]+',
            r'github\s*[:\/]\s*[\w\-\.\.]+',
            r'github\s+user(?:name)?[:\s]+[\w\-\.]+'
        ]
        
        # LinkedIn patterns
        linkedin_patterns = [
            r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+',
            r'https?://(?:www\.)?linkedin\.com/profile/view\?id=\d+',
            r'linkedin\.com/in/[\w\-\.]+',
            r'linkedin:\s*[\w\-\.]+',
            r'linkedin\s*[:\/]\s*[\w\-\.\.]+',
            r'linkedin\s+profile[:\s]+[\w\-\.]+'
        ]
        
        # GitLab patterns
        gitlab_patterns = [
            r'https?://(?:www\.)?gitlab\.com/[\w\-\.]+/?(?:[\w\-\/]*)?',
            r'gitlab\.com/[\w\-\.]+/?(?:[\w\-\/]*)?',
            r'@[\w\-\.]+(?:\s+|\n)*gitlab',
            r'gitlab:\s*[\w\-\.]+',
            r'gitlab\s*[:\/]\s*[\w\-\.\.]+',
            r'gitlab\s+user(?:name)?[:\s]+[\w\-\.]+'
        ]
        
        # Portfolio patterns (broader catch for personal/professional sites)
        portfolio_patterns = [
            r'https?://[\w\-\.]+\.(?:com|io|dev|me|co|net|org|site|app|tech|blog|portfolio)/?(?:[\w\-\/]*)?',
            r'portfolio:\s*https?://[\w\-\.]+\.[\w\.]+',
            r'website:\s*https?://[\w\-\.]+\.[\w\.]+',
            r'personal\s+site:\s*https?://[\w\-\.]+\.[\w\.]+',
            r'blog:\s*https?://[\w\-\.]+\.[\w\.]+',
            r'demo:\s*https?://[\w\-\.]+\.[\w\.]+',
            r'project:\s*https?://[\w\-\.]+\.[\w\.]+'
        ]
        
        # Extract GitHub links
        for pattern in github_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean up and normalize the URL
                if not match.startswith('http'):
                    if match.startswith('github.com'):
                        match = 'https://' + match
                    elif '@' in match:
                        # Handle @username format
                        username = re.search(r'@([\w\-\.]+)', match)
                        if username:
                            match = f'https://github.com/{username.group(1)}'
                    else:
                        # Handle other formats
                        username = re.search(r'github[:\s\/]*([\w\-\.]+)', match)
                        if username:
                            match = f'https://github.com/{username.group(1)}'
                
                # Validate and add
                if self._is_valid_url(match) and match not in links['github']:
                    links['github'].append(match)
        
        # Extract LinkedIn links
        for pattern in linkedin_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean up and normalize the URL
                if not match.startswith('http'):
                    if match.startswith('linkedin.com'):
                        match = 'https://' + match
                    else:
                        # Handle linkedin:username format
                        username = re.search(r'linkedin[:\s\/]*([\w\-\.]+)', match)
                        if username:
                            match = f'https://linkedin.com/in/{username.group(1)}'
                
                # Validate and add
                if self._is_valid_url(match) and match not in links['linkedin']:
                    links['linkedin'].append(match)
        
        # Extract GitLab links
        for pattern in gitlab_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean up and normalize the URL
                if not match.startswith('http'):
                    if match.startswith('gitlab.com'):
                        match = 'https://' + match
                    elif '@' in match:
                        # Handle @username format
                        username = re.search(r'@([\w\-\.]+)', match)
                        if username:
                            match = f'https://gitlab.com/{username.group(1)}'
                    else:
                        # Handle other formats
                        username = re.search(r'gitlab[:\s\/]*([\w\-\.]+)', match)
                        if username:
                            match = f'https://gitlab.com/{username.group(1)}'
                
                # Validate and add
                if self._is_valid_url(match) and match not in links['gitlab']:
                    links['gitlab'].append(match)
        
        # Extract portfolio links
        for pattern in portfolio_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean up the URL
                if not match.startswith('http'):
                    # Extract URL from patterns like "portfolio: https://example.com"
                    url_match = re.search(r'https?://[\w\-\.]+\.[\w\.]+(?:/[\w\-\/]*)?', match)
                    if url_match:
                        match = url_match.group(0)
                
                # Validate and add (exclude known platforms)
                if (self._is_valid_url(match) and 
                    match not in links['portfolio'] and
                    not any(platform in match for platform in ['github.com', 'linkedin.com', 'gitlab.com'])):
                    links['portfolio'].append(match)
        
        # Also look for URLs in the general text that might be portfolio links
        general_url_pattern = r'https?://[\w\-\.]+\.(?:com|io|dev|me|co|net|org|site|app|tech|blog|portfolio)/?(?:[\w\-\/]*)?'
        general_matches = re.findall(general_url_pattern, text_lower)
        
        for match in general_matches:
            # Add to portfolio if it's not already in other categories
            if (match not in links['github'] and 
                match not in links['linkedin'] and 
                match not in links['gitlab'] and
                not any(platform in match for platform in ['github.com', 'linkedin.com', 'gitlab.com'])):
                if match not in links['portfolio']:
                    links['portfolio'].append(match)
        
        # Limit each category to top 3 most relevant links
        for category in links:
            links[category] = links[category][:3]
        
        return links
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if a URL looks legitimate"""
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL validation
        url_pattern = r'^https?://[\w\-\.]+\.[\w\.]+(?:/[\w\-\/]*)?$'
        if not re.match(url_pattern, url):
            return False
        
        # Exclude common non-portfolio domains
        excluded_domains = [
            'mail.google.com', 'gmail.com', 'outlook.com', 'yahoo.com',
            'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com',
            'stackoverflow.com', 'medium.com', 'reddit.com',
            'google.com', 'microsoft.com', 'apple.com'
        ]
        
        for domain in excluded_domains:
            if domain in url:
                return False
        
        return True
    
    def _extract_simple(self, text: str) -> Dict[str, Any]:
        """Simple extraction fallback when spaCy is not available"""
        return {
            'technical_skills': self._extract_technical_skills(text),
            'soft_skills': self._extract_soft_skills(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text),
            'certifications': self._extract_certifications(text),
            'languages': self._extract_languages(text),
            'professional_links': self._extract_professional_links(text),
            'entities': [],
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name"""
        skill_upper = skill.upper()
        return self.skill_normalization.get(skill_upper, skill.title())

