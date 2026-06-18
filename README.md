# Mentor Recruitment Form

**Mentor Recruitment Form** is a Streamlit-based web application for recruiting mentors for the She for STEM program. It serves as a reliable alternative to Google Forms and integrates directly with the organization's RDS database and Amazon S3.

The application is hosted on an **AWS EC2 instance** (production environment), connected to an **RDS database** for storing form submissions, while uploaded documents (resumes, bios, headshots) are stored in **Amazon S3**.

---

## Features

- **Mentor Registration Form** — Clean, multi-step interface for mentor sign-up
- **Direct Database Integration** — Submissions are stored in the `Mentor` table
- **Dynamic Dropdowns** — Degree, country, language, and join-options are fetched from mapping tables (with fallbacks)
- **File Uploads** — Resume and bio/headshot uploads to S3 on submit
- **Validation** — Email and WhatsApp number validation
- **Thank You Page** — Confirmation screen after successful registration
- **Modular Design** — Structured, maintainable codebase aligned with [student_registration_ui](https://github.com/VigyanShaala-Tech/student_registration_ui)

---

## Project Structure

```
Mentor-Recruitment-Form/
├── image/
│   └── VS-logo.png
├── scripts/
│   ├── app.py                  # Main Streamlit application
│   ├── config.env              # Environment variables template
│   ├── requirements.txt        # Python dependencies
│   ├── run.sh                  # Linux startup script
│   ├── GUI_1.bat               # Windows startup script
│   ├── .streamlit/
│   │   └── config.toml
│   └── modules/
│       ├── about_us.py         # About She for STEM section
│       ├── db_connection.py    # Database connection and query helpers
│       ├── db_operations.py    # Dropdown fetch + mentor insert
│       ├── page_config.py      # Page title, icon, and logo
│       ├── s3_upload.py        # S3 file upload helpers
│       ├── thankyou.py         # Thank-you page
│       └── validation.py       # Email and phone validation
├── .env                        # Local secrets (not in repo)
└── README.md
```

---

## Database Mapping Tables

Dropdown options are loaded from these tables when available (same pattern as student registration):

| Field | Mapping table | Fallback |
|-------|---------------|----------|
| Highest degree | `raw.course_mapping` (`course_duration != 1`) | Empty list if unavailable |
| Country | `raw.location_mapping` (`country`, `location_id`) | Empty list if unavailable |
| Languages | Fixed list in code | Same as original mentor form |
| Join movement options | Fixed list in code | Same as original mentor form |

Submissions are appended to the existing **`Mentor`** table with the same column names as before.

---

## Requirements

- Python 3.10+
- pandas==2.3.0
- python-dotenv==1.0.1
- SQLAlchemy==2.0.41
- streamlit==1.46.0
- boto3==1.28.18

---

## Setup

1. Copy `scripts/config.env` and fill in your database and AWS credentials.
2. Install dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

On Windows, double-click `GUI_1.bat` or run it from the `scripts` folder.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST` / `DB_ENDPOINT` | RDS host |
| `DB_NAME` | Database name |
| `DB_USER` / `DB_USERNAME` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_PORT` | Database port |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for S3 |
| `BUCKET_NAME` | S3 bucket for uploads |
| `CHECK_DUPLICATE_EMAIL` | `true` to block duplicate mentor emails |

Both `DB_USER`/`DB_HOST` (student registration style) and `DB_USERNAME`/`DB_ENDPOINT` (legacy mentor style) are supported.
