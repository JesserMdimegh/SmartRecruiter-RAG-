"""
Test PDF parsing directly to debug the "document closed" error
"""

import os
import tempfile

def test_pdf_parsing():
    """Test PDF parsing directly"""
    from smartrecruitai.services import CVParser
    
    print("Testing PDF parsing directly...")
    
    # Test with the actual PDF file
    cv_path = "cv.pdf"
    if os.path.exists(cv_path):
        print(f"Testing with {cv_path}")
        print(f"File size: {os.path.getsize(cv_path)} bytes")
        
        try:
            # Parse PDF
            cv_parser = CVParser()
            parsed_data = cv_parser.parse_file(cv_path)
            
            print("SUCCESS: PDF parsed successfully!")
            print(f"File type: {parsed_data['file_type']}")
            print(f"Page count: {parsed_data['page_count']}")
            print(f"Text length: {len(parsed_data['text'])} characters")
            print(f"First 500 chars: {parsed_data['text'][:500]}...")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ERROR: File {cv_path} not found")

if __name__ == "__main__":
    test_pdf_parsing()

