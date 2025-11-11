"""
Simple test for CV upload without authentication
"""

import os
import tempfile

def test_cv_parsing():
    """Test CV parsing directly"""
    from smartrecruitai.services import CVParser, NLPExtractor, VectorMatcher
    
    print("Testing CV parsing...")
    
    # Test with text file
    cv_path = "sample_cv_french.txt"
    if os.path.exists(cv_path):
        print(f"Testing with {cv_path}")
        
        try:
            # Parse CV
            cv_parser = CVParser()
            parsed_data = cv_parser.parse_file(cv_path)
            
            print("SUCCESS: CV parsed successfully!")
            print(f"File type: {parsed_data['file_type']}")
            print(f"Text length: {len(parsed_data['text'])} characters")
            print(f"First 200 chars: {parsed_data['text'][:200]}...")
            
            # Extract structured data
            nlp_extractor = NLPExtractor()
            extracted_data = nlp_extractor.extract_cv_data(parsed_data['text'])
            
            print("\nSUCCESS: Data extracted successfully!")
            print(f"Technical skills: {extracted_data['technical_skills']}")
            print(f"Soft skills: {extracted_data['soft_skills']}")
            print(f"Experience years: {extracted_data['experience_years']}")
            print(f"Education: {extracted_data['education']}")
            
            # Generate embedding
            vector_matcher = VectorMatcher()
            embedding = vector_matcher.generate_embedding(parsed_data['text'])
            
            print(f"\nSUCCESS: Embedding generated!")
            print(f"Embedding dimension: {len(embedding)}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
    else:
        print(f"ERROR: File {cv_path} not found")

if __name__ == "__main__":
    test_cv_parsing()
