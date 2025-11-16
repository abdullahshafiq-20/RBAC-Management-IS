
CREATE TYPE user_role AS ENUM ('admin', 'doctor', 'receptionist');
CREATE TYPE action_type AS ENUM ('login', 'logout', 'view', 'add', 'update', 'delete', 'anonymize', 'export', 'decrypt', 'consent');

-- =====================================================
-- USERS TABLE - Authentication & RBAC
-- =====================================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Hashed password (never store plain text)
    role user_role NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3)
);

-- Create index for faster login queries
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- =====================================================
-- PATIENTS TABLE - Medical Records with Anonymization
-- =====================================================
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    
    -- Original Data (Encrypted/Sensitive)
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(20),
    email VARCHAR(100),
    date_of_birth DATE,
    address TEXT,
    diagnosis TEXT,
    blood_group VARCHAR(5),
    
    -- Anonymized Data
    anonymized_name VARCHAR(50),
    anonymized_contact VARCHAR(20),
    anonymized_email VARCHAR(100),
    
    -- Metadata
    is_anonymized BOOLEAN DEFAULT FALSE,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by INTEGER REFERENCES users(user_id),
    
    -- GDPR Compliance
    consent_given BOOLEAN DEFAULT FALSE,
    data_retention_date DATE,  -- When data should be deleted
    
    CONSTRAINT chk_contact_format CHECK (contact ~ '^\+?[0-9]{10,15}$' OR contact IS NULL)
);

-- Create indexes for performance
CREATE INDEX idx_patients_anonymized ON patients(is_anonymized);
CREATE INDEX idx_patients_added_by ON patients(added_by);
CREATE INDEX idx_patients_retention ON patients(data_retention_date);

-- Trigger to update last_modified timestamp
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patients_modified
BEFORE UPDATE ON patients
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- =====================================================
-- LOGS TABLE - Audit Trail for Integrity
-- =====================================================
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    role user_role NOT NULL,
    action action_type NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    ip_address VARCHAR(45),  -- Support IPv6
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE SET NULL,
    
    -- Index for faster audit queries
    CONSTRAINT chk_details_length CHECK (LENGTH(details) <= 1000)
);

-- Create indexes for audit log queries
CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX idx_logs_action ON logs(action);
CREATE INDEX idx_logs_patient ON logs(patient_id);

-- =====================================================
-- SEED DATA - Initial Users
-- =====================================================
-- Password: admin123 (hashed with bcrypt - you'll generate this in Python)
INSERT INTO users (username, password_hash, role, full_name, email) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC3prHxrTOHu', 'admin', 'System Administrator', 'admin@hospital.com'),
('dr_bob', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC3prHxrTOHu', 'doctor', 'Dr. Bob Smith', 'bob@hospital.com'),
('alice_recep', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5VC3prHxrTOHu', 'receptionist', 'Alice Johnson', 'alice@hospital.com');

-- Note: All passwords above are 'admin123' for demo purposes
-- In production, users should set unique strong passwords

-- =====================================================
-- SAMPLE PATIENT DATA (for testing)
-- =====================================================
INSERT INTO patients (name, contact, email, date_of_birth, address, diagnosis, blood_group, consent_given, data_retention_date, added_by) VALUES
('John Doe', '+923001234567', 'john.doe@email.com', '1985-03-15', '123 Main St, Karachi', 'Hypertension', 'O+', TRUE, '2026-11-16', 1),
('Jane Smith', '+923007654321', 'jane.smith@email.com', '1990-07-22', '456 Park Ave, Lahore', 'Diabetes Type 2', 'A+', TRUE, '2026-11-16', 1),
('Ahmed Khan', '+923009876543', 'ahmed.khan@email.com', '1978-11-30', '789 Garden Rd, Islamabad', 'Asthma', 'B+', TRUE, '2026-11-16', 3),
('Sara Ali', '+923005551234', 'sara.ali@email.com', '1995-05-10', '321 Beach Rd, Karachi', 'Migraine', 'AB+', TRUE, '2026-11-16', 3),
('Hassan Raza', '+923004443322', 'hassan.raza@email.com', '1982-09-18', '654 Hill View, Peshawar', 'Anxiety Disorder', 'O-', TRUE, '2026-11-16', 1);

-- =====================================================
-- RBAC VIEWS - Role-Based Access Control
-- =====================================================

-- View for Doctors (Anonymized Data Only)
CREATE OR REPLACE VIEW doctor_patient_view AS
SELECT 
    patient_id,
    COALESCE(anonymized_name, 'ANON_' || patient_id) AS name,
    COALESCE(anonymized_contact, 'XXX-XXX-' || RIGHT(contact, 4)) AS contact,
    diagnosis,
    blood_group,
    date_added
FROM patients
WHERE is_anonymized = TRUE;

-- View for Receptionists (Limited Access)
CREATE OR REPLACE VIEW receptionist_patient_view AS
SELECT 
    patient_id,
    name,
    contact,
    email,
    date_of_birth,
    date_added
FROM patients;

-- =====================================================
-- SECURITY FUNCTIONS
-- =====================================================

-- Function to log user actions
CREATE OR REPLACE FUNCTION log_user_action(
    p_user_id INTEGER,
    p_role user_role,
    p_action action_type,
    p_details TEXT,
    p_patient_id INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO logs (user_id, role, action, details, patient_id)
    VALUES (p_user_id, p_role, p_action, p_details, p_patient_id);
END;
$$ LANGUAGE plpgsql;

-- Function to check data retention and flag expired records
CREATE OR REPLACE FUNCTION check_data_retention()
RETURNS TABLE(patient_id INTEGER, name VARCHAR, retention_date DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT p.patient_id, p.name, p.data_retention_date
    FROM patients p
    WHERE p.data_retention_date <= CURRENT_DATE
    AND p.data_retention_date IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- STATISTICS VIEWS (for Admin Dashboard)
-- =====================================================

CREATE OR REPLACE VIEW system_statistics AS
SELECT 
    (SELECT COUNT(*) FROM patients) AS total_patients,
    (SELECT COUNT(*) FROM patients WHERE is_anonymized = TRUE) AS anonymized_patients,
    (SELECT COUNT(*) FROM users WHERE is_active = TRUE) AS active_users,
    (SELECT COUNT(*) FROM logs WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours') AS actions_last_24h,
    (SELECT COUNT(*) FROM patients WHERE data_retention_date <= CURRENT_DATE) AS expired_records;

-- =====================================================
-- GRANT PERMISSIONS (Optional - for production)
-- =====================================================
-- Grant appropriate permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON patients TO hospital_app_user;
-- GRANT SELECT ON users TO hospital_app_user;
-- GRANT INSERT ON logs TO hospital_app_user;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify your setup:

-- Check users
-- SELECT * FROM users;

-- Check patients
-- SELECT * FROM patients;

-- Check if triggers work
-- UPDATE patients SET diagnosis = 'Updated Diagnosis' WHERE patient_id = 1;
-- SELECT patient_id, diagnosis, last_modified FROM patients WHERE patient_id = 1;

-- Test logging function
-- SELECT log_user_action(1, 'admin', 'view', 'Testing log function', 1);
-- SELECT * FROM logs;

-- Check statistics
-- SELECT * FROM system_statistics;