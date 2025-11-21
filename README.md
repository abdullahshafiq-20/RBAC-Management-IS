# Hospital Management System - Project Structure

## 🌐 Live Link
https://rbac-is.streamlit.app/

## 📁 Complete Directory Structure

```
RBAC-Management-IS/
│
├── 📄 app.py                          # Main Streamlit application
├── 📄 utils.py                        # Utility functions (encryption, hashing, masking)
├── 📄 database.sql                    # PostgreSQL database schema
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env.example                    # Environment variables template
├── 📄 .env                            # Actual environment variables (DO NOT COMMIT!)
├── 📄 .gitignore                      # Git ignore file
│
├── 📄 README.md                       # Project documentation


```

---

## 📋 File Descriptions

### Core Application Files

#### `streamlit_app.py`
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

#### `database.sql`
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

## 🚀 Quick Setup Commands

### 1. Clone/Create Project
```bash
mkdir RBAC-Management-IS
cd RBAC-Management-IS
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
streamlit run streamlit_app.py
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
