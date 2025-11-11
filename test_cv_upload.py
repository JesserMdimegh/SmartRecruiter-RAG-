"""
Test script for CV upload functionality
"""

import requests
import os

def test_cv_upload():
    """Test CV upload with the actual PDF file"""
    
    # Check if cv.pdf exists
    cv_path = "cv.pdf"
    if not os.path.exists(cv_path):
        print("Error: cv.pdf not found in current directory")
        return
    
    print("Testing CV upload with cv.pdf...")
    
    # Prepare the file upload
    with open(cv_path, 'rb') as f:
        files = {'file': ('cv.pdf', f, 'application/pdf')}
        
        try:
            # Make the request
            response = requests.post(
                'http://localhost:8000/api/candidates/upload_cv_direct/',
                files=files,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                print("✅ CV uploaded successfully!")
                print(f"Candidate ID: {data['candidate_id']}")
                print(f"Name: {data['candidate']['full_name']}")
                print(f"Email: {data['candidate']['email']}")
                print(f"Experience: {data['candidate']['total_experience_years']} years")
                print(f"Technical Skills: {', '.join(data['candidate']['technical_skills'][:5])}")
                print(f"Soft Skills: {', '.join(data['candidate']['soft_skills'][:3])}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to server. Make sure Django server is running.")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_cv_upload()
