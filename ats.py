# AI-Powered ATS Tool - Phase 1
# Resume Parsing & Job Description Analysis with Gemini AI

import os
import json
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import asyncio

# PDF and text processing
import PyPDF2
import pdfplumber
from io import BytesIO

# NLP and similarity
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Gemini AI
import google.generativeai as genai

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonalInfo:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""

@dataclass
class Experience:
    title: str
    company: str
    duration: str
    description: str
    skills_used: List[str]

@dataclass
class Education:
    degree: str
    institution: str
    year: str
    gpa: str = ""
    relevant_courses: List[str] = None

@dataclass
class ResumeData:
    personal_info: PersonalInfo
    experiences: List[Experience]
    education: List[Education]
    skills: List[str]
    certifications: List[str]
    projects: List[str]
    raw_text: str
    keywords: List[str]

@dataclass
class JobRequirements:
    title: str
    company: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    education_requirements: str
    responsibilities: List[str]
    qualifications: List[str]
    raw_text: str
    keywords: List[str]

class GeminiAIAnalyzer:
    """Gemini AI integration for advanced text analysis"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract_resume_structured_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured data from resume using Gemini AI"""
        
        prompt = f"""
        Analyze the following resume text and extract structured information in JSON format.
        
        Resume Text:
        {resume_text}
        
        Please extract and return a JSON object with the following structure:
        {{
            "personal_info": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "phone number",
                "location": "city, state/country",
                "linkedin": "LinkedIn URL",
                "github": "GitHub URL"
            }},
            "experiences": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "duration": "Start Date - End Date",
                    "description": "Job description",
                    "skills_used": ["skill1", "skill2"]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree Name",
                    "institution": "Institution Name",
                    "year": "Graduation Year",
                    "gpa": "GPA if mentioned",
                    "relevant_courses": ["course1", "course2"]
                }}
            ],
            "skills": ["skill1", "skill2", "skill3"],
            "certifications": ["cert1", "cert2"],
            "projects": ["project1", "project2"],
            "keywords": ["keyword1", "keyword2"]
        }}
        
        If any information is not available, use empty strings or empty arrays.
        Return only valid JSON without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean the response to extract JSON
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Error extracting resume data with Gemini: {e}")
            return self._get_empty_resume_structure()
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """Extract structured job requirements using Gemini AI"""
        
        prompt = f"""
        Analyze the following job description and extract structured information in JSON format.
        
        Job Description:
        {job_description}
        
        Please extract and return a JSON object with the following structure:
        {{
            "title": "Job Title",
            "company": "Company Name",
            "required_skills": ["skill1", "skill2"],
            "preferred_skills": ["skill1", "skill2"],
            "experience_level": "Entry/Mid/Senior Level",
            "education_requirements": "Education requirements",
            "responsibilities": ["responsibility1", "responsibility2"],
            "qualifications": ["qualification1", "qualification2"],
            "keywords": ["keyword1", "keyword2"]
        }}
        
        Focus on extracting:
        - Technical skills (programming languages, tools, frameworks)
        - Soft skills (communication, leadership, etc.)
        - Years of experience required
        - Education requirements
        - Key responsibilities
        - Required qualifications
        
        Return only valid JSON without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Error extracting job requirements with Gemini: {e}")
            return self._get_empty_job_structure()
    
    def calculate_ats_score_with_reasoning(self, resume_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Calculate ATS score with detailed reasoning using Gemini AI"""
        
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyzer. 
        Analyze the resume against the job requirements and provide a comprehensive evaluation.
        
        RESUME DATA:
        {json.dumps(resume_data, indent=2)}
        
        JOB REQUIREMENTS:
        {json.dumps(job_data, indent=2)}
        
        Please analyze and return a JSON object with the following structure:
        {{
            "overall_score": 85,
            "category_scores": {{
                "skills_match": 90,
                "experience_match": 80,
                "education_match": 85,
                "keywords_match": 75
            }},
            "strengths": ["strength1", "strength2"],
            "gaps": ["gap1", "gap2"],
            "missing_skills": ["skill1", "skill2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"],
            "readiness_status": "READY/NEEDS_IMPROVEMENT",
            "detailed_analysis": {{
                "skills_analysis": "Detailed analysis of skills match",
                "experience_analysis": "Analysis of experience relevance",
                "education_analysis": "Analysis of education match",
                "overall_recommendation": "Overall recommendation"
            }}
        }}
        
        Scoring criteria:
        - Skills Match (40%): How well do the candidate's skills match required/preferred skills?
        - Experience Match (30%): Does the experience level and relevance match?
        - Education Match (20%): Does education meet requirements?
        - Keywords Match (10%): How many relevant keywords are present?
        
        Score ranges:
        - 90-100: Excellent match, highly likely to pass ATS
        - 80-89: Good match, likely to pass ATS
        - 70-79: Moderate match, may pass ATS
        - 60-69: Below average, needs improvement
        - Below 60: Poor match, significant improvements needed
        
        Set readiness_status to "READY" if overall_score >= 90, otherwise "NEEDS_IMPROVEMENT".
        
        Return only valid JSON without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Error calculating ATS score with Gemini: {e}")
            return self._get_default_score_structure()
    
    def generate_improvement_plan(self, ats_analysis: Dict, missing_skills: List[str]) -> Dict[str, Any]:
        """Generate detailed improvement plan using Gemini AI"""
        
        prompt = f"""
        Based on the ATS analysis results, create a comprehensive improvement plan for the candidate.
        
        ATS ANALYSIS:
        {json.dumps(ats_analysis, indent=2)}
        
        MISSING SKILLS:
        {missing_skills}
        
        Create a detailed improvement plan in JSON format:
        {{
            "priority_improvements": [
                {{
                    "category": "Technical Skills",
                    "skill": "Python",
                    "current_level": "Beginner",
                    "target_level": "Intermediate",
                    "time_estimate": "2-3 months",
                    "learning_path": ["Step 1", "Step 2"],
                    "resources": [
                        {{
                            "type": "course",
                            "title": "Resource Title",
                            "provider": "Platform",
                            "duration": "X hours",
                            "difficulty": "Beginner/Intermediate/Advanced"
                        }}
                    ],
                    "milestones": ["Milestone 1", "Milestone 2"]
                }}
            ],
            "quick_wins": [
                {{
                    "action": "Add specific keywords to resume",
                    "description": "Include these keywords in your resume",
                    "time_required": "30 minutes",
                    "impact": "High/Medium/Low"
                }}
            ],
            "resume_optimization": {{
                "keywords_to_add": ["keyword1", "keyword2"],
                "sections_to_improve": ["section1", "section2"],
                "formatting_suggestions": ["suggestion1", "suggestion2"]
            }},
            "timeline": {{
                "immediate": ["Action within 1 week"],
                "short_term": ["Action within 1 month"],
                "medium_term": ["Action within 3 months"],
                "long_term": ["Action within 6 months"]
            }}
        }}
        
        Focus on:
        - Most impactful improvements first
        - Realistic timelines
        - Specific, actionable steps
        - Resource recommendations
        - Progress tracking milestones
        
        Return only valid JSON without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            return json.loads(json_text)
        except Exception as e:
            logger.error(f"Error generating improvement plan with Gemini: {e}")
            return {"error": "Failed to generate improvement plan"}
    
    def _get_empty_resume_structure(self):
        return {
            "personal_info": {"name": "", "email": "", "phone": "", "location": "", "linkedin": "", "github": ""},
            "experiences": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "keywords": []
        }
    
    def _get_empty_job_structure(self):
        return {
            "title": "", "company": "", "required_skills": [], "preferred_skills": [],
            "experience_level": "", "education_requirements": "",
            "responsibilities": [], "qualifications": [], "keywords": []
        }
    
    def _get_default_score_structure(self):
        return {
            "overall_score": 0,
            "category_scores": {"skills_match": 0, "experience_match": 0, "education_match": 0, "keywords_match": 0},
            "strengths": [], "gaps": [], "missing_skills": [],
            "improvement_suggestions": [], "readiness_status": "NEEDS_IMPROVEMENT",
            "detailed_analysis": {"skills_analysis": "", "experience_analysis": "", "education_analysis": "", "overall_recommendation": ""}
        }

class ResumeParser:
    """Resume parsing and text extraction"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english')) if nltk else set()
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
        
        try:
            # Fallback to PyPDF2
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s@.+\-()&,]', '', text)
        return text
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex patterns"""
        contact_info = {"email": "", "phone": "", "linkedin": "", "github": ""}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]
        
        # Phone pattern
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact_info["linkedin"] = f"https://{linkedin_matches[0]}"
        
        # GitHub pattern
        github_pattern = r'github\.com/[\w\-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contact_info["github"] = f"https://{github_matches[0]}"
        
        return contact_info
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Clean text
        text = self.clean_text(text.lower())
        
        # Tokenize
        words = word_tokenize(text) if nltk else text.split()
        
        # Remove stopwords and short words
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2 and word.isalpha()
        ]
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]

class ATSMatcher:
    """ATS scoring and matching algorithms"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts using TF-IDF"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0
            
            # Vectorize texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def calculate_skills_match(self, resume_skills: List[str], required_skills: List[str], 
                             preferred_skills: List[str] = None) -> Dict[str, Any]:
        """Calculate skills matching score"""
        if not resume_skills:
            return {"score": 0, "matched_required": [], "matched_preferred": [], "missing_required": required_skills}
        
        # Normalize skills (lowercase and strip)
        resume_skills_norm = [skill.lower().strip() for skill in resume_skills]
        required_skills_norm = [skill.lower().strip() for skill in required_skills]
        preferred_skills_norm = [skill.lower().strip() for skill in (preferred_skills or [])]
        
        # Find matches
        matched_required = []
        matched_preferred = []
        
        for req_skill in required_skills_norm:
            for res_skill in resume_skills_norm:
                if req_skill in res_skill or res_skill in req_skill:
                    matched_required.append(req_skill)
                    break
        
        for pref_skill in preferred_skills_norm:
            for res_skill in resume_skills_norm:
                if pref_skill in res_skill or res_skill in pref_skill:
                    matched_preferred.append(pref_skill)
                    break
        
        # Calculate score
        required_score = len(matched_required) / len(required_skills_norm) if required_skills_norm else 1.0
        preferred_score = len(matched_preferred) / len(preferred_skills_norm) if preferred_skills_norm else 0.0
        
        # Weighted score (required skills are more important)
        overall_score = (required_score * 0.8) + (preferred_score * 0.2)
        
        missing_required = [skill for skill in required_skills_norm if skill not in matched_required]
        
        return {
            "score": overall_score * 100,
            "matched_required": matched_required,
            "matched_preferred": matched_preferred,
            "missing_required": missing_required,
            "required_match_rate": required_score * 100,
            "preferred_match_rate": preferred_score * 100
        }

class ATSAnalyzer:
    """Main ATS analysis coordinator"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_analyzer = GeminiAIAnalyzer(gemini_api_key)
        self.resume_parser = ResumeParser()
        self.ats_matcher = ATSMatcher()
    
    def process_resume_and_job(self, pdf_file, job_description: str) -> Dict[str, Any]:
        """Complete processing pipeline"""
        try:
            # Step 1: Extract text from PDF
            logger.info("Extracting text from PDF...")
            resume_text = self.resume_parser.extract_text_from_pdf(pdf_file)
            if not resume_text.strip():
                raise ValueError("Could not extract text from PDF")
            
            # Step 2: Parse resume with Gemini AI
            logger.info("Parsing resume with Gemini AI...")
            resume_data = self.gemini_analyzer.extract_resume_structured_data(resume_text)
            resume_data["raw_text"] = resume_text
            
            # Step 3: Parse job description with Gemini AI
            logger.info("Analyzing job description with Gemini AI...")
            job_data = self.gemini_analyzer.extract_job_requirements(job_description)
            job_data["raw_text"] = job_description
            
            # Step 4: Calculate ATS score with Gemini AI
            logger.info("Calculating ATS score...")
            ats_analysis = self.gemini_analyzer.calculate_ats_score_with_reasoning(resume_data, job_data)
            
            # Step 5: Generate improvement plan if needed
            improvement_plan = None
            if ats_analysis.get("overall_score", 0) < 90:
                logger.info("Generating improvement plan...")
                missing_skills = ats_analysis.get("missing_skills", [])
                improvement_plan = self.gemini_analyzer.generate_improvement_plan(ats_analysis, missing_skills)
            
            # Compile results
            results = {
                "resume_data": resume_data,
                "job_data": job_data,
                "ats_analysis": ats_analysis,
                "improvement_plan": improvement_plan,
                "processed_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "processed_at": datetime.now().isoformat()
            }

# Example usage and testing functions
def main():
    """Example usage of the ATS tool"""
    
    # Initialize with your Gemini API key
    GEMINI_API_KEY = ""  # Replace with your actual API key
    
    if GEMINI_API_KEY == "your-gemini-api-key-here":
        print("Please set your Gemini API key in the GEMINI_API_KEY variable")
        return
    
    # Initialize ATS analyzer
    ats_analyzer = ATSAnalyzer(GEMINI_API_KEY)
    
    # Example job description
    job_description = """
    Senior Software Developer - Python/AI
    Company: TechCorp Inc.
    
    We are seeking a Senior Software Developer with expertise in Python and AI/ML to join our team.
    
    Required Skills:
    - 5+ years of Python development experience
    - Experience with machine learning frameworks (TensorFlow, PyTorch)
    - Strong knowledge of data structures and algorithms
    - Experience with cloud platforms (AWS, GCP, Azure)
    - Proficiency in SQL and database design
    
    Preferred Skills:
    - Experience with NLP and computer vision
    - Knowledge of Docker and Kubernetes
    - Experience with CI/CD pipelines
    - Leadership and mentoring experience
    
    Responsibilities:
    - Develop and maintain AI/ML applications
    - Design scalable software architectures
    - Collaborate with cross-functional teams
    - Mentor junior developers
    
    Education: Bachelor's degree in Computer Science or related field
    """
    
    #For testing, you would load a PDF file like this:
    with open("Ganesh_Neelakanta.pdf", "rb") as pdf_file:
        results = ats_analyzer.process_resume_and_job(pdf_file, job_description)
        print(json.dumps(results, indent=2))
    
    print("ATS Tool initialized successfully!")
    print("To use:")
    print("1. Set your Gemini API key")
    print("2. Load a PDF resume file")
    print("3. Call ats_analyzer.process_resume_and_job(pdf_file, job_description)")

if __name__ == "__main__":
    main()

# Additional utility functions for future phases

def save_results_to_json(results: Dict[str, Any], filename: str):
    """Save analysis results to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def load_results_from_json(filename: str) -> Dict[str, Any]:
    """Load analysis results from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_ats_summary(results: Dict[str, Any]):
    """Print a formatted summary of ATS analysis"""
    if results.get("status") != "success":
        print(f"Error: {results.get('error_message', 'Unknown error')}")
        return
    
    ats_analysis = results.get("ats_analysis", {})
    
    print("\n" + "="*50)
    print("ATS ANALYSIS SUMMARY")
    print("="*50)
    
    print(f"Overall Score: {ats_analysis.get('overall_score', 0):.1f}/100")
    print(f"Status: {ats_analysis.get('readiness_status', 'Unknown')}")
    
    category_scores = ats_analysis.get('category_scores', {})
    print(f"\nCategory Scores:")
    for category, score in category_scores.items():
        print(f"  {category.replace('_', ' ').title()}: {score}/100")
    
    strengths = ats_analysis.get('strengths', [])
    if strengths:
        print(f"\nStrengths:")
        for strength in strengths:
            print(f"  ✓ {strength}")
    
    gaps = ats_analysis.get('gaps', [])
    if gaps:
        print(f"\nAreas for Improvement:")
        for gap in gaps:
            print(f"  ⚠ {gap}")
    
    print("\n" + "="*50)

# Requirements for installation:
"""
pip install PyPDF2 pdfplumber spacy nltk scikit-learn google-generativeai pandas numpy

# Download spaCy model
python -m spacy download en_core_web_sm

# For NLTK data (will be downloaded automatically)
"""