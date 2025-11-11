"""
Create a sample CV text file for testing
"""

sample_cv_text = """
ALEXANDER JOHNSON
Senior Data Scientist
alexander.johnson@email.com
+1 (555) 987-6543
New York, NY

PROFESSIONAL SUMMARY
Experienced Senior Data Scientist with 7+ years of experience in machine learning, deep learning, and data analysis.
Specialized in Python, TensorFlow, PyTorch, and natural language processing. Proven track record of delivering
data-driven solutions that drive business growth.

TECHNICAL SKILLS
- Programming Languages: Python, R, SQL, JavaScript, Java
- Machine Learning: TensorFlow, PyTorch, Scikit-learn, Keras, XGBoost
- Data Analysis: Pandas, NumPy, Matplotlib, Seaborn, Plotly
- Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
- Cloud Platforms: AWS, Google Cloud Platform, Azure
- Tools: Git, Docker, Kubernetes, Jupyter Notebooks, Apache Spark
- Frameworks: Django, Flask, FastAPI, React

EXPERIENCE
Senior Data Scientist | TechCorp Inc. | 2021 - Present
- Led development of ML models for recommendation systems serving 10M+ users
- Implemented deep learning solutions using TensorFlow and PyTorch
- Collaborated with engineering teams to deploy models in production
- Mentored team of 5 junior data scientists
- Improved model accuracy by 25% through advanced feature engineering

Data Scientist | StartupXYZ | 2019 - 2021
- Built predictive models for customer churn analysis reducing churn by 30%
- Developed NLP pipelines for text classification and sentiment analysis
- Created interactive data visualization dashboards using Python and React
- Implemented A/B testing framework for model evaluation

Data Analyst | AnalyticsCorp | 2017 - 2019
- Analyzed large datasets to identify business opportunities
- Created automated reporting systems using Python and SQL
- Collaborated with stakeholders to define KPIs and success metrics

EDUCATION
Master of Science in Data Science | Stanford University | 2017
Bachelor of Science in Computer Science | UC Berkeley | 2015

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Google Cloud Professional Data Engineer
- Certified Analytics Professional (CAP)
- Microsoft Azure Data Scientist Associate

PROJECTS
1. Real-time Recommendation Engine
   - Built collaborative filtering algorithm using TensorFlow
   - Implemented real-time scoring system with Redis and Kafka
   - Achieved 40% improvement in click-through rates
   - Technologies: Python, TensorFlow, Redis, Docker, Kubernetes

2. Customer Sentiment Analysis Platform
   - Developed NLP model using BERT for sentiment classification
   - Achieved 94% accuracy on customer feedback data
   - Built REST API for real-time sentiment analysis
   - Technologies: Python, TensorFlow, BERT, Flask, PostgreSQL

3. Fraud Detection System
   - Created anomaly detection model using unsupervised learning
   - Reduced false positives by 60% while maintaining detection accuracy
   - Implemented real-time monitoring dashboard
   - Technologies: Python, Scikit-learn, Apache Spark, React

LANGUAGES
- English (Native)
- Spanish (Conversational)
- French (Basic)

SOFT SKILLS
- Leadership and Team Management
- Communication and Presentation
- Problem Solving and Critical Thinking
- Project Management
- Cross-functional Collaboration
- Mentoring and Training

PUBLICATIONS
- "Advanced Feature Engineering for Recommendation Systems" - ICML 2022
- "Deep Learning Approaches to NLP" - NeurIPS 2021
- "Scalable Machine Learning Pipelines" - KDD 2020

AWARDS
- Data Science Excellence Award - TechCorp Inc. 2022
- Best Paper Award - ICML 2022
- Innovation Award - StartupXYZ 2020
"""

# Save to file
with open("sample_cv_alexander.txt", "w", encoding="utf-8") as f:
    f.write(sample_cv_text)

print("Sample CV created: sample_cv_alexander.txt")
print("This CV contains:")
print("- Name: Alexander Johnson")
print("- Email: alexander.johnson@email.com")
print("- Experience: 7+ years")
print("- Skills: Python, TensorFlow, PyTorch, Machine Learning, etc.")
print("- Education: MS Data Science from Stanford")
print("- Projects: Recommendation Engine, Sentiment Analysis, Fraud Detection")
print("- Soft Skills: Leadership, Communication, Problem Solving")
print("\nYou can now test the CV upload with this file!")

