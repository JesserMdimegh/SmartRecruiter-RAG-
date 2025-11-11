"""
Test CV upload with the working text file
"""

import requests
import os

def test_text_cv_upload():
    """Test CV upload with the text file"""
    
    # Check if text CV exists
    cv_path = "sample_cv_alexander.txt"
    if not os.path.exists(cv_path):
        print("ERROR: sample_cv_alexander.txt not found")
        return
    
    print(f"Testing CV upload with {cv_path}...")
    print(f"File size: {os.path.getsize(cv_path)} bytes")
    
    try:
        # Prepare the file upload
        with open(cv_path, 'rb') as f:
            files = {'file': ('sample_cv_alexander.txt', f, 'text/plain')}
            
            print("Sending request to Django server...")
            
            # Make the request
            response = requests.post(
                'http://localhost:8000/api/candidates/upload_cv_direct/',
                files=files,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("SUCCESS: CV uploaded successfully!")
                print(f"Candidate ID: {data['candidate_id']}")
                print(f"Name: {data['candidate']['full_name']}")
                print(f"Email: {data['candidate']['email']}")
                print(f"Experience: {data['candidate']['total_experience_years']} years")
                print(f"Technical Skills: {', '.join(data['candidate']['technical_skills'][:10])}")
                print(f"Soft Skills: {', '.join(data['candidate']['soft_skills'][:5])}")
                print(f"Education: {data['candidate']['education_level']}")
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
    test_text_cv_upload()

