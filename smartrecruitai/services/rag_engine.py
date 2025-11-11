"""
RAG Engine Service
Level 3: Retrieval-Augmented Generation for Explainability
"""

from typing import Dict, Any, List, Optional
import json


class RAGEngine:
    """Retrieval-Augmented Generation engine for intelligent explanations"""
    
    def __init__(self):
        """Initialize the RAG engine"""
        self.temperature = 0.7
        self.max_tokens = 1000
    
    def explain_match(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], scores: Dict[str, float]) -> str:
        """
        Generate a detailed explanation of why a candidate matches a job
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            scores: Matching scores
            
        Returns:
            Human-readable explanation
        """
        # Build the explanation
        explanation_parts = []
        
        # Overall score (percent)
        overall_score = scores.get('overall_score', 0) * 100
        explanation_parts.append(f"Compatibility score: {overall_score:.0f}%\n")

        explanation_parts.append("Detailed analysis:\n\n")
        
        # Technical skills analysis
        explanation_parts.append("Technical skills:\n")
        candidate_skills = candidate_data.get('technical_skills', [])
        job_skills = job_data.get('required_skills', [])
        
        matched = set(candidate_skills) & set(job_skills)
        missing = set(job_skills) - set(candidate_skills)
        
        for skill in matched:
            explanation_parts.append("+ " + skill + "\n")
        
        for skill in missing:
            explanation_parts.append("- " + skill + " (missing skill)\n")
        
        explanation_parts.append("\n")
        
        # Experience analysis
        explanation_parts.append("Experience:\n")
        candidate_exp = candidate_data.get('experience_years', 0)
        job_exp_required = job_data.get('required_experience_years', 0)
        
        if candidate_exp >= job_exp_required:
            explanation_parts.append("+ " + str(candidate_exp) + " years experience (required: " + str(job_exp_required) + ")\n")
        else:
            explanation_parts.append("- " + str(candidate_exp) + " years (required: " + str(job_exp_required) + ")\n")
        
        explanation_parts.append("\n")
        
        # Recommendation
        explanation_parts.append("Recommendation:\n")
        
        # overall_score is in [0, 100]
        if overall_score >= 80:
            explanation_parts.append("Excellent candidate, highly recommended for this position.\n")
        elif overall_score >= 60:
            explanation_parts.append("Good candidate with potential; evaluate gaps and training possibilities.\n")
        else:
            explanation_parts.append("Consider if profile brings complementary value; otherwise explore other candidates.\n")
        
        return "".join(explanation_parts)
    
    def answer_question(self, question: str, candidate_data: Dict[str, Any], 
                       job_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Answer questions about a candidate using RAG
        
        Args:
            question: Natural language question
            candidate_data: Candidate information
            job_data: Optional job context
            
        Returns:
            Answer to the question
        """
        question_lower = question.lower()
        
        # Simple rule-based responses (in production, use LLM)
        responses = []
        
        # Questions about experience
        if "experience" in question_lower or "expérience" in question_lower:
            exp_years = candidate_data.get('experience_years', 0)
            responses.append(f"Le candidat a {exp_years} ans d'expérience.")
        
        # Questions about skills
        if "compétence" in question_lower or "skill" in question_lower:
            skills = candidate_data.get('technical_skills', [])
            if skills:
                responses.append(f"Ses compétences techniques incluent: {', '.join(skills[:5])}")
        
        # Questions about projects
        if "projet" in question_lower:
            responses.append("Les projets mentionnés dans le CV seront analysés en détail.")
        
        # Questions about availability
        if "disponibilité" in question_lower or "availability" in question_lower:
            availability = candidate_data.get('availability', 'unknown')
            responses.append(f"Disponibilité: {availability}")
        
        # Questions about education
        if "formation" in question_lower or "education" in question_lower:
            education = candidate_data.get('education_level', 'N/A')
            responses.append(f"Niveau de formation: {education}")
        
        if not responses:
            responses.append("Pour plus d'informations, consultez le CV complet du candidat.")
        
        return "\n".join(responses)
    
    def generate_candidate_summary(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary for a candidate tailored to a specific job
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            
        Returns:
            Executive summary text
        """
        summary_parts = []
        
        summary_parts.append(f"📋 Résumé Exécutif - {candidate_data.get('full_name', 'Candidat')}\n\n")
        summary_parts.append(f"Pour le poste: {job_data.get('title', 'N/A')}\n\n")
        
        summary_parts.append("Forces pour ce poste:\n")
        
        # Technical skills
        candidate_skills = set(candidate_data.get('technical_skills', []))
        job_skills = set(job_data.get('required_skills', []))
        matched = candidate_skills & job_skills
        
        for skill in list(matched)[:5]:
            summary_parts.append(f"✓ {skill}\n")
        
        summary_parts.append("\n")
        
        # Experience
        summary_parts.append(f"Expérience: {candidate_data.get('experience_years', 0)} ans\n")
        
        # Current position
        if candidate_data.get('current_position'):
            summary_parts.append(f"Poste actuel: {candidate_data.get('current_position')}\n")
        
        return "".join(summary_parts)
    
    def generate_email_content(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], 
                               match_score: float) -> str:
        """
        Generate a personalized contact email for a candidate
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            match_score: Matching score
            
        Returns:
            Email content
        """
        email_parts = []
        
        email_parts.append(f"Bonjour {candidate_data.get('full_name', 'Madame, Monsieur')},\n\n")
        
        email_parts.append(f"Nous avons examiné votre profil et nous pensons que vous pourriez être intéressé(e)")
        email_parts.append(f" par notre poste de {job_data.get('title', '')}.\n\n")
        
        email_parts.append("Votre profil présente une forte compatibilité pour ce rôle grâce à:\n")
        
        # List matched skills
        candidate_skills = set(candidate_data.get('technical_skills', []))
        job_skills = set(job_data.get('required_skills', []))
        matched = candidate_skills & job_skills
        
        for skill in list(matched)[:3]:
            email_parts.append(f"- {skill}\n")
        
        email_parts.append("\n")
        
        email_parts.append(f"Score de compatibilité: {match_score*100:.0f}%\n\n")
        
        email_parts.append("Nous serions ravis d'en discuter avec vous.\n\n")
        email_parts.append("Cordialement,\n")
        email_parts.append("L'équipe SmartRecruitAI\n")
        
        return "".join(email_parts)
    
    def suggest_interview_questions(self, candidate_data: Dict[str, Any], 
                                   job_data: Dict[str, Any]) -> List[str]:
        """
        Suggest interview questions based on candidate profile
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            
        Returns:
            List of suggested interview questions
        """
        questions = []
        
        # Questions about experience
        candidate_exp = candidate_data.get('experience_years', 0)
        if candidate_exp > 0:
            questions.append(f"Parlez-nous de vos {int(candidate_exp)} années d'expérience.")
        
        # Questions about specific skills
        candidate_skills = set(candidate_data.get('technical_skills', []))
        job_skills = set(job_data.get('required_skills', []))
        gaps = job_skills - candidate_skills
        
        for skill in list(gaps)[:2]:
            questions.append(f"Quelle est votre expérience avec {skill}?")
        
        # Questions about projects
        questions.append("Pouvez-vous nous parler d'un projet récent dont vous êtes fier(e)?")
        
        # Questions about motivation
        questions.append("Qu'est-ce qui vous intéresse dans ce poste?")
        
        return questions

