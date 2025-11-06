# Mentor Recruitment Form

**Mentor Recruitment Form** is a web-based application designed to streamline the process of recruiting mentors for our program. Since some organizations restrict access to Google Forms, this application serves as a reliable and secure alternative.  

The platform is hosted on an **AWS EC2 instance** (production environment), connected to an **RDS database** for storing form submissions, while uploaded **PDF documents** (like resumes or certificates) are securely stored in **Amazon S3**.  

---
## Project Structure

```
Mentor-Recruitment-Form/
├── scripts/
│   ├── Mentor_Rec.py          # Main Streamlit application
│   ├── requirements.txt       # Python dependencies
│   ├── GUI_1.bat             # Windows batch file for easy execution
│   └── .streamlit/           # Streamlit configuration
├── image/
│   ├── VS-logo.png           # VigyanShaala logo
│   └── logo                  # Additional logo file
├── .env                      # Environment variables (not in repo)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```
