# Hospital Management System - Project Structure

## 📁 Complete Directory Structure

```
RBAC-Management-IS/
│
├── 📄 app.py                          # Main Streamlit application
├── 📄 utils.py                        # Utility functions (encryption, hashing, masking)
├── 📄 config.py                       # Configuration management
│
├── 📄 hospital_schema.sql             # PostgreSQL database schema
│
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env.example                    # Environment variables template
├── 📄 .env                            # Actual environment variables (DO NOT COMMIT!)
├── 📄 .gitignore                      # Git ignore file
│
├── 📄 README.md                       # Project documentation
├── 📄 SETUP_INSTRUCTIONS.md           # Detailed setup guide

```

---

## 📋 File Descriptions

### Core Application Files

#### `app.py`
**Purpose:** Main Streamlit application with UI and business logic

**Key Components:**
- Authentication system (login/logout)
- Session state management
- Role-based dashboards (Admin, Doctor, Receptionist)
- Database operations (CRUD)
- Audit logging
- Data anonymization interface

**Dependencies:** streamlit, psycopg2, pandas, utils, config

---

#### `utils.py`
**Purpose:** Utility functions for security and data processing

**Key Functions:**
- `EncryptionManager` - Fernet encryption/decryption
- `hash_password()` - Bcrypt password hashing
- `verify_password()` - Password verification
- `anonymize_name()` - Name anonymization
- `mask_contact()` - Phone number masking
- `mask_email()` - Email masking
- Data validation functions
- GDPR compliance utilities

**Dependencies:** hashlib, bcrypt, cryptography

---

#### `config.py`
**Purpose:** Centralized configuration management

**Configuration Classes:**
- `DatabaseConfig` - Database connection settings
- `SecurityConfig` - Encryption, session, password rules
- `AppConfig` - General application settings
- `GDPRConfig` - GDPR compliance settings
- `RBACConfig` - Role-based access control
- `LoggingConfig` - Audit log settings
- `ValidationConfig` - Data validation rules

**Dependencies:** os, dotenv, cryptography

---

#### `hospital_schema.sql`
**Purpose:** Complete PostgreSQL database schema

**Includes:**
- Table definitions (users, patients, logs)
- ENUM types (user_role, action_type)
- Indexes for performance
- Triggers for automatic timestamps
- Views for role-based access
- Functions for logging and data retention
- Sample data for testing

**Database Objects:**
- 3 tables
- 2 ENUM types
- 6 indexes
- 1 trigger
- 2 views
- 3 functions

---

### Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies

**Key Packages:**
```
streamlit==1.31.0          # Web framework
psycopg2-binary==2.9.9     # PostgreSQL driver
pandas==2.1.4              # Data processing
cryptography==42.0.0       # Encryption
bcrypt==4.1.2              # Password hashing
python-dotenv==1.0.0       # Environment variables
```

---

#### `.env.example`
**Purpose:** Template for environment variables

**Variables:**
- Database credentials
- Encryption keys
- Session timeouts
- Email configuration (optional)
- Feature flags

**Note:** Copy to `.env` and fill with actual values

---

#### `.gitignore`
**Purpose:** Exclude sensitive files from version control

**Should Include:**
```
.env
__pycache__/
*.pyc
*.pyo
*.log
.DS_Store
venv/
*.db
backups/
```

---

### Documentation Files

#### `README.md`
**Purpose:** Quick start guide and project overview

**Sections:**
- Project description
- Quick start instructions
- Features overview
- Technology stack
- Contributing guidelines

---

#### `SETUP_INSTRUCTIONS.md`
**Purpose:** Detailed step-by-step setup guide

**Sections:**
- Prerequisites
- PostgreSQL setup
- Python environment setup
- Configuration
- Running the application
- Testing checklist
- Troubleshooting
- Bonus features

---

#### `PROJECT_STRUCTURE.md`
**Purpose:** This file - complete project organization

---

### Assignment Deliverables

#### `docs/project_report.pdf`
**Purpose:** Main assignment submission document (3-5 pages)

**Required Sections:**
1. **System Overview**
   - Introduction
   - Technologies used
   - Architecture overview

2. **CIA Triad Implementation**
   - Confidentiality measures
   - Integrity controls
   - Availability mechanisms

3. **GDPR Compliance**
   - Data protection measures
   - User rights implementation
   - Consent management

4. **Screenshots**
   - Login page
   - Admin dashboard
   - Doctor dashboard
   - Receptionist dashboard
   - Anonymization process
   - Audit logs

5. **Implementation Details**
   - Database schema
   - Security measures
   - Role-based access control

6. **Testing & Results**
   - Test scenarios
   - Results
   - Observations

7. **Conclusion & Future Work**

---

#### `screenshots/`
**Purpose:** Visual documentation for report

**Required Screenshots:**
1. `login_page.png` - Login interface with credentials shown
2. `admin_dashboard.png` - Admin view with statistics
3. `doctor_dashboard.png` - Doctor view with anonymized data
4. `receptionist_dashboard.png` - Add patient form
5. `anonymization.png` - Before/after anonymization
6. `audit_logs.png` - Complete audit trail

**Tips for Screenshots:**
- Use full-screen mode
- Include browser tabs showing localhost:8501
- Highlight key features with arrows/annotations
- Ensure text is readable
- Show realistic test data

---

## 🚀 Quick Setup Commands

### 1. Clone/Create Project
```bash
mkdir hospital_management_system
cd hospital_management_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
```bash
# Create database
createdb hospital_db

# Load schema
psql -d hospital_db -f hospital_schema.sql
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 6. Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to .env as ENCRYPTION_KEY
```

### 7. Run Application
```bash
streamlit run app.py
```

### 8. Access Application
```
Open browser: http://localhost:8501
Login with: admin / admin123
```

---

## 📊 Database Schema Overview

### Tables

#### `users` (Authentication & RBAC)
- `user_id` (PK)
- `username` (unique)
- `password_hash`
- `role` (admin/doctor/receptionist)
- `full_name`
- `email`
- `is_active`
- `created_at`
- `last_login`

#### `patients` (Medical Records)
- `patient_id` (PK)
- `name`, `contact`, `email`
- `date_of_birth`, `address`
- `diagnosis`, `blood_group`
- `anonymized_name`, `anonymized_contact`, `anonymized_email`
- `is_anonymized`
- `date_added`, `last_modified`
- `added_by` (FK → users)
- `consent_given`
- `data_retention_date`

#### `logs` (Audit Trail)
- `log_id` (PK)
- `user_id` (FK → users)
- `role`
- `action` (login/view/add/update/delete/anonymize/export)
- `timestamp`
- `details`
- `ip_address`
- `patient_id` (FK → patients)

---

## 🔐 Security Features

### 1. Authentication
- Bcrypt password hashing (12 rounds)
- Session-based authentication
- Last login tracking
- Failed login attempts logging

### 2. Authorization (RBAC)
- **Admin:** Full access to all data and system functions
- **Doctor:** View-only access to anonymized patient data
- **Receptionist:** Add/edit patients, no access to sensitive diagnosis

### 3. Encryption
- Fernet symmetric encryption for sensitive data
- Base64 encoding for safe storage
- Reversible encryption for authorized access

### 4. Data Masking
- Name → ANON_XXXX
- Phone → XXX-XXX-1234
- Email → j***@domain.com

### 5. Audit Logging
- All user actions logged
- Timestamp tracking
- User identification
- Action details
- Patient references

---

## 🌍 GDPR Compliance Features

### 1. Lawful Basis
- Explicit consent required
- Consent tracking in database
- Clear purpose for data collection

### 2. Data Minimization
- Collect only necessary information
- Field-level access control
- Role-based data visibility

### 3. Right to Access
- Patients can view their data (future feature)
- Export functionality for data portability

### 4. Right to Erasure
- Data retention policies
- Automatic expiration tracking
- Secure deletion capability

### 5. Transparency
- Clear privacy notices
- Audit trail for all access
- Consent management

---

## 🧪 Testing Checklist

### Functional Testing
- [ ] Login with all three roles
- [ ] Add new patient (receptionist)
- [ ] View patient list (all roles)
- [ ] Anonymize patient data (admin)
- [ ] View audit logs (admin)
- [ ] Export data to CSV (admin)
- [ ] Logout functionality
- [ ] Session persistence

### Security Testing
- [ ] Password hashing works
- [ ] Role permissions enforced
- [ ] Audit logs capture all actions
- [ ] Data anonymization irreversible
- [ ] Invalid login blocked
- [ ] SQL injection prevention
- [ ] XSS prevention

### Data Validation
- [ ] Phone number format validation
- [ ] Email format validation
- [ ] Required field enforcement
- [ ] Data type validation
- [ ] Input sanitization

### GDPR Compliance
- [ ] Consent checkbox required
- [ ] Data retention date set
- [ ] Anonymization available
- [ ] Audit trail maintained
- [ ] Export functionality works

---

## 📝 Assignment Submission Format

### Folder Structure for Submission
```
Assignment4_YourName_YourRollNo/
│
├── Source_Code/
│   ├── app.py
│   ├── utils.py
│   ├── config.py
│   ├── requirements.txt
│   └── hospital_schema.sql
│
├── Database/
│   └── hospital_db_backup.sql
│
├── Documentation/
│   ├── Project_Report.pdf (3-5 pages)
│   └── Screenshots/
│       ├── login.png
│       ├── admin_dashboard.png
│       ├── doctor_view.png
│       ├── receptionist_view.png
│       ├── anonymization.png
│       └── audit_logs.png
│
├── Demo_Video/
│   └── demo_video_link.txt (Google Drive link)
│
└── README.txt (Brief instructions to run)
```

---

## 🎯 Grading Criteria Mapping

### Privacy & GDPR Compliance (20 marks)
- ✅ Consent management
- ✅ Data retention policies
- ✅ Right to be forgotten (anonymization)
- ✅ Transparency in data handling

### Confidentiality Implementation (20 marks)
- ✅ Password hashing (bcrypt)
- ✅ Data encryption (Fernet)
- ✅ Data masking/anonymization
- ✅ Role-based access control

### Integrity (20 marks)
- ✅ Comprehensive audit logging
- ✅ Data validation
- ✅ Timestamp tracking
- ✅ Action attribution

### Availability & Reliability (15 marks)
- ✅ Error handling (try-except)
- ✅ Data backup/export
- ✅ System status monitoring
- ✅ Session management

### Dashboard Functionality (10 marks)
- ✅ Intuitive UI
- ✅ Role-based views
- ✅ Real-time updates
- ✅ Data visualization

### Documentation (10 marks)
- ✅ System diagrams
- ✅ Screenshots
- ✅ Implementation explanation
- ✅ Code comments

### Presentation/Demo (5 marks)
- ✅ Clear demonstration
- ✅ Feature showcase
- ✅ Professional delivery

---

## 🎁 Bonus Features (+2 marks each)

### 1. Fernet Encryption ✅
Already implemented in `utils.py`

### 2. Real-time Activity Graphs
Add to admin dashboard using plotly

### 3. GDPR Features
- Data retention timer ✅
- User consent banner
- Cookie notice

---

## 📞 Support & Resources

### Getting Help
1. Check `SETUP_INSTRUCTIONS.md`
2. Review error messages in terminal
3. Check PostgreSQL logs
4. Verify `.env` configuration
5. Test database connection

### Useful Commands
```bash
# Check Python version
python --version

# Check PostgreSQL status
sudo systemctl status postgresql

# View Streamlit logs
streamlit run app.py --logger.level=debug

# Database backup
pg_dump -U postgres hospital_db > backup.sql

# Restore database
psql -U postgres hospital_db < backup.sql
```

---

## ✅ Pre-Submission Checklist

- [ ] All files in correct structure
- [ ] Database schema loads without errors
- [ ] Application runs successfully
- [ ] All three roles tested
- [ ] Screenshots captured
- [ ] Report completed (3-5 pages)
- [ ] Demo video uploaded (optional)
- [ ] Code has comments
- [ ] README includes setup instructions
- [ ] No hardcoded passwords
- [ ] .env file excluded from submission

---

**Good luck with your assignment! 🎉**