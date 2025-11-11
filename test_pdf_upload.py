"""
Test script to upload the actual PDF file and debug any issues
"""

import requests
import os

def test_pdf_upload():
    """Test PDF upload with the actual cv.pdf file"""
    
    # Check if cv.pdf exists
    cv_path = "cv.pdf"
    if not os.path.exists(cv_path):
        print("ERROR: cv.pdf not found in current directory")
        return
    
    print(f"Testing PDF upload with {cv_path}...")
    print(f"File size: {os.path.getsize(cv_path)} bytes")
    
    try:
        # Prepare the file upload
        with open(cv_path, 'rb') as f:
            files = {'file': ('cv.pdf', f, 'application/pdf')}
            
            print("Sending request to Django server...")
            
            # Make the request
            response = requests.post(
                'http://localhost:8000/api/candidates/upload_cv_direct/',
                files=files,
                timeout=60  # Increased timeout for large files
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("SUCCESS: CV uploaded successfully!")
                print(f"Candidate ID: {data['candidate_id']}")
                print(f"Name: {data['candidate']['full_name']}")
                print(f"Email: {data['candidate']['email']}")
                print(f"Experience: {data['candidate']['total_experience_years']} years")
                print(f"Technical Skills: {', '.join(data['candidate']['technical_skills'][:5])}")
                print(f"Soft Skills: {', '.join(data['candidate']['soft_skills'][:3])}")
            else:
                print(f"ERROR: {response.status_code}")
                print("Response content:")
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure Django server is running.")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_upload()

