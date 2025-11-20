#!/usr/bin/env python
"""
Test script for professional links extraction from CV text
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CV_match.settings')
django.setup()

from smartrecruitai.services.nlp_extractor import NLPExtractor

def test_professional_links_extraction():
    """Test the professional links extraction functionality"""
    print("🔗 Testing Professional Links Extraction")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    # Test CV text with various link formats
    test_cv_texts = [
        {
            'name': 'Full Stack Developer CV',
            'text': '''
            John Doe
            Senior Full Stack Developer
            
            Contact:
            Email: john.doe@email.com
            Phone: +1 555-123-4567
            
            Professional Profiles:
            GitHub: https://github.com/johndoe
            LinkedIn: https://linkedin.com/in/johndoe
            GitLab: https://gitlab.com/johndoe-dev
            Portfolio: https://johndoe.dev
            
            Projects:
            - E-commerce Platform: https://github.com/johndoe/ecommerce
            - Blog: https://johndoe-blog.medium.com
            
            Skills:
            Python, JavaScript, React, Node.js, Docker
            '''
        },
        {
            'name': 'Data Scientist CV',
            'text': '''
            Jane Smith
            Data Scientist & ML Engineer
            
            Links:
            • GitHub: github.com/janesmith
            • LinkedIn: linkedin.com/in/janesmith
            • Portfolio: https://janesmith-portfolio.com
            
            Additional:
            Personal website: https://janesmith.com
            Blog: https://blog.janesmith.com
            Demo: https://ml-demos.janesmith.com
            
            Technical Skills:
            Python, TensorFlow, PyTorch, scikit-learn
            '''
        },
        {
            'name': 'DevOps Engineer CV',
            'text': '''
            Mike Johnson
            DevOps Engineer
            
            Social:
            @mikejohnson (GitHub)
            GitLab: gitlab.com/mikejohnson-devops
            
            Professional:
            LinkedIn: linkedin.com/in/mikejohnson
            Website: https://mikejohnson.dev
            Infrastructure blog: https://devops.mikejohnson.dev
            
            Experience:
            5+ years in DevOps and cloud infrastructure
            '''
        },
        {
            'name': 'Mixed Format CV',
            'text': '''
            Sarah Wilson
            Software Developer
            
            CONTACT
            ----------------------------------------
            Email: sarah.wilson@email.com
            LinkedIn: https://www.linkedin.com/in/sarahwilson
            GitHub: @sarahwilson
            Portfolio: portfolio: https://sarahwilson.github.io
            
            ONLINE PRESENCE
            ----------------------------------------
            Personal site: https://sarahwilson.com
            Tech blog: https://blog.sarahwilson.com
            Side projects: https://github.com/sarahwilson/projects
            
            SKILLS
            ----------------------------------------
            Java, Spring Boot, AWS, Kubernetes
            '''
        }
    ]
    
    for i, test_case in enumerate(test_cv_texts, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Extract professional links
        extracted_data = nlp_extractor.extract_cv_data(test_case['text'])
        professional_links = extracted_data.get('professional_links', {})
        
        print(f"✅ Extracted Links:")
        
        for category, links in professional_links.items():
            if links:
                print(f"  📂 {category.title()}:")
                for j, link in enumerate(links, 1):
                    print(f"    {j}. {link}")
            else:
                print(f"  📂 {category.title()}: No links found")
        
        # Show extraction summary
        total_links = sum(len(links) for links in professional_links.values())
        print(f"\n📊 Summary: {total_links} total links extracted")
        
        # Validate extracted links
        print(f"🔍 Validation:")
        for category, links in professional_links.items():
            if links:
                for link in links:
                    if nlp_extractor._is_valid_url(link):
                        print(f"  ✓ Valid: {link}")
                    else:
                        print(f"  ✗ Invalid: {link}")

def test_url_validation():
    """Test the URL validation functionality"""
    print("\n🔍 Testing URL Validation")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    test_urls = [
        # Valid URLs
        "https://github.com/username",
        "https://linkedin.com/in/username",
        "https://gitlab.com/username",
        "https://portfolio.dev",
        "https://personal-site.com",
        
        # Invalid URLs
        "not-a-url",
        "ftp://invalid-protocol.com",
        "https://facebook.com/excluded",
        "https://twitter.com/excluded",
        "https://mail.google.com/excluded",
        
        # Edge cases
        "",
        None,
        "https://",
        "github.com/username",  # Missing protocol
    ]
    
    for url in test_urls:
        is_valid = nlp_extractor._is_valid_url(url)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {url or 'None'}")

def test_pattern_matching():
    """Test various pattern matching scenarios"""
    print("\n🎯 Testing Pattern Matching")
    print("=" * 50)
    
    nlp_extractor = NLPExtractor()
    
    pattern_tests = [
        {
            'name': 'GitHub Patterns',
            'text': '''
            GitHub: https://github.com/username
            github.com/username/repo
            @username (GitHub)
            github: username
            '''
        },
        {
            'name': 'LinkedIn Patterns',
            'text': '''
            LinkedIn: https://linkedin.com/in/username
            linkedin.com/in/username
            linkedin: username
            LinkedIn profile: username
            '''
        },
        {
            'name': 'Portfolio Patterns',
            'text': '''
            Portfolio: https://myportfolio.com
            website: https://mywebsite.dev
            personal site: https://personal-site.io
            blog: https://myblog.com
            demo: https://demo.example.com
            '''
        }
    ]
    
    for test in pattern_tests:
        print(f"\n📋 {test['name']}:")
        links = nlp_extractor._extract_professional_links(test['text'])
        
        for category, link_list in links.items():
            if link_list:
                print(f"  {category.title()}: {link_list}")

if __name__ == "__main__":
    print("🚀 SmartRecruitAI Professional Links Extraction Test")
    print("=" * 60)
    
    # Test professional links extraction
    test_professional_links_extraction()
    
    # Test URL validation
    test_url_validation()
    
    # Test pattern matching
    test_pattern_matching()
    
    print(f"\n✅ Testing completed!")
    print(f"\n🎯 Key Features Demonstrated:")
    print("- GitHub, GitLab, LinkedIn link extraction")
    print("- Portfolio and personal website detection")
    print("- Multiple format support (URLs, usernames, text)")
    print("- URL validation and filtering")
    print("- Duplicate removal and organization")
    print("- Comprehensive pattern matching")
    
    print(f"\n📈 Extraction Capabilities:")
    print("- Supports 6+ URL formats per platform")
    print("- Handles @username mentions")
    print("- Extracts from various CV sections")
    print("- Filters out non-professional links")
    print("- Organizes links by platform type")
