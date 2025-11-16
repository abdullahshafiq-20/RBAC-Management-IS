"""
GDPR-Compliant Hospital Management System
Streamlit Dashboard with CIA Triad Implementation
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta
import hashlib
from utils import (
    EncryptionManager, hash_password, verify_password,
    anonymize_name, mask_contact, mask_email, anonymize_address,
    validate_contact, validate_email, sanitize_input,
    calculate_retention_date, format_log_message, mask_sensitive_data
)
import os
import dotenv
dotenv.load_dotenv()

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# DATABASE CONNECTION
# =====================================================

@st.cache_resource
def get_db_connection():
    """Create database connection with connection pooling"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch=True):
    """Execute database query with error handling"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
                conn.commit()
                return result
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        st.error(f"Query error: {e}")
        return None


# =====================================================
# ENCRYPTION MANAGER (Initialize once)
# =====================================================

@st.cache_resource
def get_encryption_manager():
    """Initialize encryption manager with stored key"""
    # In production, load this key from environment variables or secure vault
    ENCRYPTION_KEY = b'your-encryption-key-here-32-bytes-base64encoded='
    return EncryptionManager(ENCRYPTION_KEY)


# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
    if 'gdpr_consent_given' not in st.session_state:
        st.session_state.gdpr_consent_given = False
    if 'consent_timestamp' not in st.session_state:
        st.session_state.consent_timestamp = None


# =====================================================
# GDPR CONSENT BANNER
# =====================================================

def show_gdpr_consent_banner():
    """Display GDPR consent banner for users"""
    if not st.session_state.gdpr_consent_given:
        # Create a container for the consent banner
        consent_container = st.container()
        
        with consent_container:
            st.markdown("""
                <style>
                .consent-banner {
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    background-color: #1e1e1e;
                    color: white;
                    padding: 20px;
                    z-index: 9999;
                    border-top: 3px solid #4CAF50;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Display banner
            st.info("🍪 **GDPR Compliance Notice**")
            
            with st.expander("📋 View Privacy Policy & Data Usage", expanded=True):
                st.markdown("""
                ### Hospital Management System - Privacy Notice
                
                **Data We Collect:**
                - User authentication information (username, role)
                - Patient medical records (with consent)
                - System activity logs for security and audit purposes
                
                **How We Use Your Data:**
                - To provide healthcare management services
                - To ensure data security and system integrity
                - To comply with legal and regulatory requirements
                
                **Your Rights (GDPR Articles 15-22):**
                - ✅ Right to Access (Article 15)
                - ✅ Right to Rectification (Article 16)
                - ✅ Right to Erasure (Article 17)
                - ✅ Right to Data Portability (Article 20)
                - ✅ Right to Object (Article 21)
                
                **Data Retention:**
                - Patient data is retained for 1 year by default
                - You can request data deletion at any time
                - Anonymization is available for privacy protection
                
                **Security Measures:**
                - 🔒 Bcrypt password hashing
                - 🔐 Fernet encryption for sensitive data
                - 📊 Complete audit trail logging
                - 🛡️ Role-based access control (RBAC)
                
                **Contact:**
                For data protection inquiries, contact: dpo@hospital.com
                """)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col2:
                if st.button("✅ Accept & Continue", use_container_width=True, type="primary"):
                    st.session_state.gdpr_consent_given = True
                    st.session_state.consent_timestamp = datetime.now()
                    log_action('consent', f"User accepted GDPR consent at {st.session_state.consent_timestamp}")
                    st.success("✅ Consent recorded. Thank you!")
                    st.rerun()
            
            with col3:
                if st.button("❌ Decline", use_container_width=True):
                    st.error("⚠️ You must accept the privacy policy to use this system.")
                    st.session_state.authenticated = False
                    st.stop()
            
            st.divider()
    else:
        # Show consent status in sidebar
        with st.sidebar:
            st.caption(f"✅ GDPR Consent: Accepted")
            if st.session_state.consent_timestamp:
                st.caption(f"📅 {st.session_state.consent_timestamp.strftime('%Y-%m-%d %H:%M')}")
            
            if st.button("🔄 Revoke Consent", key="revoke_consent"):
                st.session_state.gdpr_consent_given = False
                st.session_state.consent_timestamp = None
                log_action('consent', "User revoked GDPR consent")
                st.rerun()


# =====================================================
# LOGGING FUNCTIONS
# =====================================================

def log_action(action, details="", patient_id=None):
    """Log user action to database"""
    if not st.session_state.authenticated:
        return
    
    query = """
        INSERT INTO logs (user_id, role, action, details, patient_id, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (
        st.session_state.user_id,
        st.session_state.role,
        action,
        details,
        patient_id,
        datetime.now()
    )
    execute_query(query, params, fetch=False)


# =====================================================
# AUTHENTICATION
# =====================================================

def authenticate_user(username, password):
    """Authenticate user and return user data"""
    query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
    result = execute_query(query, (username,))
    
    if result and len(result) > 0:
        user = result[0]
        if verify_password(password, user['password_hash']):
            # Update last login
            update_query = "UPDATE users SET last_login = %s WHERE user_id = %s"
            execute_query(update_query, (datetime.now(), user['user_id']), fetch=False)
            return user
    return None


def login_page():
    """Display login page"""
    st.markdown("# 🏥 Hospital Management System")
    st.markdown("### Secure Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['user_id']
                        st.session_state.username = user['username']
                        st.session_state.role = user['role']
                        
                        # Log successful login
                        log_action('login', f"User {username} logged in successfully")
                        st.success(f"Welcome, {user['full_name']}!")
                        st.rerun()
                    else:
                        log_action('login', f"Failed login attempt for username: {username}")
                        st.error("Invalid username or password")
        
        st.info("**Demo Credentials:**\n\n"
                "- Admin: `admin` / `admin123`\n"
                "- Doctor: `dr_bob` / `admin123`\n"
                "- Receptionist: `alice_recep` / `admin123`")


def logout():
    """Logout user"""
    log_action('logout', f"User {st.session_state.username} logged out")
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()


# =====================================================
# PATIENT DATA FUNCTIONS
# =====================================================

def get_patients(role):
    """Fetch patients based on user role"""
    if role == 'admin':
        query = "SELECT * FROM patients ORDER BY patient_id DESC"
    elif role == 'doctor':
        # Doctors can ONLY see anonymized patients
        query = """
            SELECT patient_id, 
                   COALESCE(anonymized_name, name) as name,
                   COALESCE(anonymized_contact, contact) as contact,
                   diagnosis, blood_group, date_added, is_anonymized
            FROM patients 
            WHERE is_anonymized = TRUE
            ORDER BY patient_id DESC
        """
    else:  # receptionist
        query = """
            SELECT patient_id, name, contact, email, date_of_birth, date_added
            FROM patients 
            ORDER BY patient_id DESC
        """
    
    result = execute_query(query)
    return pd.DataFrame(result) if result else pd.DataFrame()


def add_patient(name, contact, email, dob, address, diagnosis, blood_group, consent):
    """Add new patient record"""
    query = """
        INSERT INTO patients 
        (name, contact, email, date_of_birth, address, diagnosis, blood_group, 
         consent_given, data_retention_date, added_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING patient_id
    """
    
    retention_date = calculate_retention_date(365)  # 1 year
    params = (
        name, contact, email, dob, address, diagnosis, blood_group,
        consent, retention_date, st.session_state.user_id
    )
    
    result = execute_query(query, params)
    if result:
        patient_id = result[0]['patient_id']
        log_action('add', f"Added new patient: {name}", patient_id)
        return patient_id
    return None


def update_patient(patient_id, name, contact, email, dob):
    """Update patient record (receptionist can only update basic info)"""
    query = """
        UPDATE patients 
        SET name = %s, contact = %s, email = %s, date_of_birth = %s
        WHERE patient_id = %s
    """
    params = (name, contact, email, dob, patient_id)
    
    success = execute_query(query, params, fetch=False)
    if success:
        log_action('update', f"Updated patient: {name}", patient_id)
        return True
    return False


def anonymize_patient(patient_id):
    """Anonymize patient data"""
    # First fetch the patient data
    query = "SELECT * FROM patients WHERE patient_id = %s"
    result = execute_query(query, (patient_id,))
    
    if not result:
        return False
    
    patient = result[0]
    
    # Generate anonymized data
    anon_name = anonymize_name(patient['name'], patient_id)
    anon_contact = mask_contact(patient['contact'])
    anon_email = mask_email(patient['email']) if patient['email'] else None
    
    # Update with anonymized data
    update_query = """
        UPDATE patients 
        SET anonymized_name = %s, 
            anonymized_contact = %s, 
            anonymized_email = %s,
            is_anonymized = TRUE
        WHERE patient_id = %s
    """
    
    success = execute_query(
        update_query, 
        (anon_name, anon_contact, anon_email, patient_id),
        fetch=False
    )
    
    if success:
        log_action('anonymize', f"Anonymized patient data", patient_id)
        return True
    return False


# =====================================================
# ADMIN DASHBOARD
# =====================================================

def admin_dashboard():
    """Admin dashboard with full access"""
    st.title("🔐 Admin Dashboard")
    
    # Statistics Row
    col1, col2, col3, col4 = st.columns(4)
    
    stats_query = "SELECT * FROM system_statistics"
    stats = execute_query(stats_query)
    
    if stats:
        stat = stats[0]
        with col1:
            st.metric("Total Patients", stat['total_patients'])
        with col2:
            st.metric("Anonymized", stat['anonymized_patients'])
        with col3:
            st.metric("Active Users", stat['active_users'])
        with col4:
            st.metric("Actions (24h)", stat['actions_last_24h'])
    
    st.divider()
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Patient Records", "🔒 Anonymization", "📊 Audit Logs", "📈 Analytics", "⚙️ System"])
    
    with tab1:
        st.subheader("All Patient Records")
        
        # Sub-tabs for original and anonymized data
        subtab1, subtab2 = st.tabs(["📄 Original Data", "🔐 Anonymized Data"])
        
        with subtab1:
            st.write("**Original Patient Records**")
            df = get_patients('admin')
            
            if not df.empty:
                # Display configuration
                display_cols = ['patient_id', 'name', 'contact', 'diagnosis', 'blood_group', 
                              'is_anonymized', 'date_added']
                st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
                
                # Export functionality
                if st.button("📥 Export to CSV", key="export_original"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        "patients_export.csv",
                        "text/csv",
                        key='download-csv'
                    )
                    log_action('export', "Exported patient data to CSV")
            else:
                st.info("No patient records found")
        
        with subtab2:
            st.write("**Anonymized Patient Records View**")
            # Query for anonymized data only
            query = """
                SELECT patient_id, 
                       COALESCE(anonymized_name, name) as name,
                       COALESCE(anonymized_contact, contact) as contact,
                       diagnosis, blood_group, is_anonymized, date_added
                FROM patients 
                WHERE is_anonymized = TRUE
                ORDER BY patient_id DESC
            """
            result = execute_query(query)
            
            if result:
                df_anon = pd.DataFrame(result)
                display_cols = ['patient_id', 'name', 'contact', 'diagnosis', 'blood_group', 'date_added']
                st.dataframe(df_anon[display_cols], use_container_width=True, hide_index=True)
                
                # Export functionality
                if st.button("📥 Export Anonymized CSV", key="export_anon"):
                    csv = df_anon.to_csv(index=False)
                    st.download_button(
                        "Download Anonymized CSV",
                        csv,
                        "patients_anonymized_export.csv",
                        "text/csv",
                        key='download-csv-anon'
                    )
                    log_action('export', "Exported anonymized patient data to CSV")
            else:
                st.info("No anonymized patient records found")
    
    with tab2:
        st.subheader("Data Anonymization")
        
        # Get non-anonymized patients
        query = "SELECT patient_id, name, contact, is_anonymized FROM patients WHERE is_anonymized = FALSE"
        patients = execute_query(query)
        
        if patients:
            st.info(f"**{len(patients)}** patients pending anonymization")
            
            for patient in patients:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**ID:** {patient['patient_id']}")
                with col2:
                    st.write(f"**Name:** {patient['name']}")
                with col3:
                    if st.button("Anonymize", key=f"anon_{patient['patient_id']}"):
                        if anonymize_patient(patient['patient_id']):
                            st.success("Patient anonymized!")
                            st.rerun()
        else:
            st.success("✅ All patients are anonymized!")
    
    with tab3:
        st.subheader("Integrity Audit Log")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            log_limit = st.selectbox("Show last", [50, 100, 200, 500], index=0)
        with col2:
            action_filter = st.selectbox("Filter by action", 
                                        ["All", "login", "add", "update", "view", "anonymize", "export"])
        
        # Build query
        if action_filter == "All":
            log_query = f"SELECT * FROM logs ORDER BY timestamp DESC LIMIT {log_limit}"
            logs = execute_query(log_query)
        else:
            log_query = f"SELECT * FROM logs WHERE action = %s ORDER BY timestamp DESC LIMIT {log_limit}"
            logs = execute_query(log_query, (action_filter,))
        
        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            # Export logs
            if st.button("📥 Export Logs"):
                csv = df_logs.to_csv(index=False)
                st.download_button(
                    "Download Audit Log",
                    csv,
                    f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        else:
            st.info("No logs found")
    
    with tab4:
        st.subheader("📈 Real-Time Analytics Dashboard")
        
        # Row 1: Patient Statistics Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Patient Distribution by Blood Group**")
            blood_query = """
                SELECT blood_group, COUNT(*) as count 
                FROM patients 
                WHERE blood_group IS NOT NULL
                GROUP BY blood_group 
                ORDER BY count DESC
            """
            blood_data = execute_query(blood_query)
            if blood_data:
                df_blood = pd.DataFrame(blood_data)
                st.bar_chart(df_blood.set_index('blood_group'))
            else:
                st.info("No data available")
        
        with col2:
            st.write("**Anonymization Status**")
            anon_query = """
                SELECT 
                    CASE WHEN is_anonymized THEN 'Anonymized' ELSE 'Not Anonymized' END as status,
                    COUNT(*) as count
                FROM patients
                GROUP BY is_anonymized
            """
            anon_data = execute_query(anon_query)
            if anon_data:
                df_anon = pd.DataFrame(anon_data)
                # Create pie chart data
                import altair as alt
                chart = alt.Chart(df_anon).mark_arc().encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="status", type="nominal", 
                                   scale=alt.Scale(domain=['Anonymized', 'Not Anonymized'],
                                                 range=['#28a745', '#ffc107'])),
                    tooltip=['status', 'count']
                ).properties(width=300, height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No data available")
        
        st.divider()
        
        # Row 2: User Activity and Audit Logs
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**User Actions (Last 7 Days)**")
            actions_query = """
                SELECT action, COUNT(*) as count
                FROM logs
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                GROUP BY action
                ORDER BY count DESC
            """
            actions_data = execute_query(actions_query)
            if actions_data:
                df_actions = pd.DataFrame(actions_data)
                st.bar_chart(df_actions.set_index('action'))
            else:
                st.info("No activity in the last 7 days")
        
        with col2:
            st.write("**Daily Activity Trend (Last 7 Days)**")
            daily_query = """
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM logs
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                GROUP BY DATE(timestamp)
                ORDER BY date
            """
            daily_data = execute_query(daily_query)
            if daily_data:
                df_daily = pd.DataFrame(daily_data)
                df_daily['date'] = pd.to_datetime(df_daily['date'])
                st.line_chart(df_daily.set_index('date'))
            else:
                st.info("No activity data available")
        
        st.divider()
        
        # Row 3: GDPR Compliance Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Retention Status**")
            retention_status_query = """
                SELECT 
                    CASE 
                        WHEN data_retention_date > CURRENT_DATE + INTERVAL '30 days' THEN 'Safe (>30 days)'
                        WHEN data_retention_date > CURRENT_DATE THEN 'Expiring Soon (<30 days)'
                        ELSE 'Expired'
                    END as status,
                    COUNT(*) as count
                FROM patients
                WHERE data_retention_date IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN data_retention_date > CURRENT_DATE + INTERVAL '30 days' THEN 'Safe (>30 days)'
                        WHEN data_retention_date > CURRENT_DATE THEN 'Expiring Soon (<30 days)'
                        ELSE 'Expired'
                    END
            """
            retention_data = execute_query(retention_status_query)
            if retention_data:
                df_retention = pd.DataFrame(retention_data)
                st.bar_chart(df_retention.set_index('status'))
            else:
                st.info("No retention data available")
        
        with col2:
            st.write("**Consent Status**")
            consent_query = """
                SELECT 
                    CASE WHEN consent_given THEN 'Consent Given' ELSE 'No Consent' END as status,
                    COUNT(*) as count
                FROM patients
                GROUP BY consent_given
            """
            consent_data = execute_query(consent_query)
            if consent_data:
                df_consent = pd.DataFrame(consent_data)
                import altair as alt
                chart = alt.Chart(df_consent).mark_arc().encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="status", type="nominal",
                                   scale=alt.Scale(domain=['Consent Given', 'No Consent'],
                                                 range=['#28a745', '#dc3545'])),
                    tooltip=['status', 'count']
                ).properties(width=300, height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No consent data available")
        
        st.divider()
        
        # Row 4: Recent Patients Timeline
        st.write("**Patient Registration Timeline (Last 30 Days)**")
        timeline_query = """
            SELECT DATE(date_added) as date, COUNT(*) as patients_added
            FROM patients
            WHERE date_added > CURRENT_TIMESTAMP - INTERVAL '30 days'
            GROUP BY DATE(date_added)
            ORDER BY date
        """
        timeline_data = execute_query(timeline_query)
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline['date'] = pd.to_datetime(df_timeline['date'])
            st.area_chart(df_timeline.set_index('date'))
        else:
            st.info("No recent patient registrations")
    
    with tab5:
        st.subheader("System Management & GDPR Compliance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**System Status**")
            st.success("✅ Database: Connected")
            st.success("✅ Encryption: Active")
            st.info(f"⏱️ Last Activity: {st.session_state.last_activity.strftime('%H:%M:%S')}")
        
        with col2:
            st.write("**GDPR Compliance Overview**")
            retention_query = "SELECT * FROM check_data_retention()"
            expired = execute_query(retention_query)
            
            if expired:
                st.warning(f"⚠️ {len(expired)} records need attention")
            else:
                st.success("✅ All records within retention period")
        
        st.divider()
        
        # GDPR Data Retention Timer Section
        st.subheader("⏰ Data Retention Timer & Management")
        
        # Get detailed retention information
        retention_details_query = """
            SELECT 
                patient_id,
                name,
                data_retention_date,
                CASE 
                    WHEN data_retention_date <= CURRENT_DATE THEN 'EXPIRED'
                    WHEN data_retention_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING SOON'
                    ELSE 'ACTIVE'
                END as status,
                data_retention_date - CURRENT_DATE as days_remaining
            FROM patients
            WHERE data_retention_date IS NOT NULL
            ORDER BY data_retention_date ASC
        """
        retention_details = execute_query(retention_details_query)
        
        if retention_details:
            df_retention = pd.DataFrame(retention_details)
            
            # Show summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                expired_count = len(df_retention[df_retention['status'] == 'EXPIRED'])
                st.metric("🔴 Expired Records", expired_count)
            with col2:
                expiring_count = len(df_retention[df_retention['status'] == 'EXPIRING SOON'])
                st.metric("🟡 Expiring Soon (<30 days)", expiring_count)
            with col3:
                active_count = len(df_retention[df_retention['status'] == 'ACTIVE'])
                st.metric("🟢 Active Records", active_count)
            
            st.divider()
            
            # Show expired records that need attention
            if expired_count > 0:
                st.error("**⚠️ URGENT: Records Past Retention Date**")
                expired_df = df_retention[df_retention['status'] == 'EXPIRED'][['patient_id', 'name', 'data_retention_date', 'days_remaining']]
                st.dataframe(expired_df, use_container_width=True, hide_index=True)
                
                st.warning("**Action Required:** These records should be reviewed and potentially deleted per GDPR Article 17 (Right to Erasure)")
            
            # Show expiring soon records
            if expiring_count > 0:
                st.warning("**⏰ Records Expiring Within 30 Days**")
                expiring_df = df_retention[df_retention['status'] == 'EXPIRING SOON'][['patient_id', 'name', 'data_retention_date', 'days_remaining']]
                st.dataframe(expiring_df, use_container_width=True, hide_index=True)
            
            # All records table
            st.write("**All Records with Retention Dates**")
            display_df = df_retention[['patient_id', 'name', 'data_retention_date', 'status', 'days_remaining']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        else:
            st.info("No retention data available")
        
        st.divider()
        
        # Auto-refresh option
        st.write("**Auto-Refresh Dashboard**")
        auto_refresh = st.checkbox("Enable auto-refresh (every 30 seconds)", value=False)
        if auto_refresh:
            import time
            time.sleep(30)
            st.rerun()


# =====================================================
# DOCTOR DASHBOARD
# =====================================================

def doctor_dashboard():
    """Doctor dashboard with anonymized data access"""
    st.title("👨‍⚕️ Doctor Dashboard")
    
    st.info("ℹ️ You are viewing anonymized patient data to protect privacy")
    
    tab1, tab2 = st.tabs(["📋 Patient Records", "🔍 Search Patient"])
    
    with tab1:
        st.subheader("Anonymized Patient Records")
        df = get_patients('doctor')
        
        if not df.empty:
            # Show only relevant columns for doctors
            display_cols = ['patient_id', 'name', 'contact', 'diagnosis', 'blood_group', 'date_added']
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
            
            log_action('view', "Viewed anonymized patient list")
        else:
            st.info("No patient records found")
    
    with tab2:
        st.subheader("Search Patient by ID")
        
        patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)
        
        if st.button("Search"):
            query = """
                SELECT patient_id, 
                       COALESCE(anonymized_name, name) as name,
                       COALESCE(anonymized_contact, contact) as contact,
                       diagnosis, blood_group, date_added, is_anonymized
                FROM patients 
                WHERE patient_id = %s AND is_anonymized = TRUE
            """
            result = execute_query(query, (patient_id,))
            
            if result:
                patient = result[0]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Patient ID:** {patient['patient_id']}")
                    st.write(f"**Name:** {patient['name']}")
                    st.write(f"**Contact:** {patient['contact']}")
                
                with col2:
                    st.write(f"**Diagnosis:** {patient['diagnosis']}")
                    st.write(f"**Blood Group:** {patient['blood_group']}")
                    st.write(f"**Added:** {patient['date_added']}")
                
                log_action('view', f"Viewed patient details", patient_id)
            else:
                st.error("Patient not found or not anonymized yet")


# =====================================================
# RECEPTIONIST DASHBOARD
# =====================================================

def receptionist_dashboard():
    """Receptionist dashboard for adding/editing records"""
    st.title("📝 Receptionist Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Patient", "📋 View Patients", "✏️ Edit Patient"])
    
    with tab1:
        st.subheader("Add New Patient")
        
        with st.form("add_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", placeholder="John Doe")
                contact = st.text_input("Contact*", placeholder="+923001234567")
                email = st.text_input("Email", placeholder="patient@email.com")
                dob = st.date_input("Date of Birth*")
            
            with col2:
                address = st.text_area("Address*", placeholder="123 Main St, Karachi")
                diagnosis = st.text_input("Diagnosis*", placeholder="Hypertension")
                blood_group = st.selectbox("Blood Group*", 
                                          ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                consent = st.checkbox("Patient Consent Given*", value=False)
            
            submit = st.form_submit_button("Add Patient", use_container_width=True)
            
            if submit:
                # Validation
                errors = []
                if not name:
                    errors.append("Name is required")
                if not contact:
                    errors.append("Contact is required")
                elif not validate_contact(contact):
                    errors.append("Invalid contact format")
                if email and not validate_email(email):
                    errors.append("Invalid email format")
                if not diagnosis:
                    errors.append("Diagnosis is required")
                if not blood_group:
                    errors.append("Blood group is required")
                if not consent:
                    errors.append("Patient consent is required")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Sanitize inputs
                    name = sanitize_input(name)
                    diagnosis = sanitize_input(diagnosis)
                    address = sanitize_input(address)
                    
                    patient_id = add_patient(name, contact, email, dob, address, 
                                           diagnosis, blood_group, consent)
                    if patient_id:
                        st.success(f"✅ Patient added successfully! ID: {patient_id}")
                        st.balloons()
                    else:
                        st.error("Failed to add patient")
    
    with tab2:
        st.subheader("Patient List")
        df = get_patients('receptionist')
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            log_action('view', "Viewed patient list")
        else:
            st.info("No patient records found")
    
    with tab3:
        st.subheader("Edit Patient Information")
        st.info("ℹ️ You can only edit: Name, Contact, Email, and Date of Birth")
        
        # Search for patient
        patient_id = st.number_input("Enter Patient ID to Edit", min_value=1, step=1, key="edit_patient_id")
        
        if st.button("Load Patient Data", key="load_patient"):
            query = """
                SELECT patient_id, name, contact, email, date_of_birth
                FROM patients 
                WHERE patient_id = %s
            """
            result = execute_query(query, (patient_id,))
            
            if result:
                st.session_state.edit_patient_data = result[0]
                st.success(f"✅ Loaded patient ID: {patient_id}")
            else:
                st.error("Patient not found")
                st.session_state.edit_patient_data = None
        
        # Edit form
        if 'edit_patient_data' in st.session_state and st.session_state.edit_patient_data:
            patient_data = st.session_state.edit_patient_data
            
            st.divider()
            st.write(f"**Editing Patient ID: {patient_data['patient_id']}**")
            
            with st.form("edit_patient_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Full Name*", value=patient_data['name'])
                    edit_contact = st.text_input("Contact*", value=patient_data['contact'])
                
                with col2:
                    edit_email = st.text_input("Email", value=patient_data['email'] or "")
                    edit_dob = st.date_input("Date of Birth*", value=patient_data['date_of_birth'])
                
                update_submit = st.form_submit_button("Update Patient", use_container_width=True)
                
                if update_submit:
                    # Validation
                    errors = []
                    if not edit_name:
                        errors.append("Name is required")
                    if not edit_contact:
                        errors.append("Contact is required")
                    elif not validate_contact(edit_contact):
                        errors.append("Invalid contact format")
                    if edit_email and not validate_email(edit_email):
                        errors.append("Invalid email format")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Sanitize inputs
                        edit_name = sanitize_input(edit_name)
                        
                        if update_patient(patient_data['patient_id'], edit_name, edit_contact, edit_email, edit_dob):
                            st.success(f"✅ Patient {patient_data['patient_id']} updated successfully!")
                            st.balloons()
                            # Clear the session state
                            del st.session_state.edit_patient_data
                            st.rerun()
                        else:
                            st.error("Failed to update patient")


# =====================================================
# MAIN APPLICATION
# =====================================================

def main():
    """Main application logic"""
    init_session_state()
    
    # Check if authenticated
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Show GDPR consent banner (must be shown after authentication)
    show_gdpr_consent_banner()
    
    # Only proceed if consent is given
    if not st.session_state.gdpr_consent_given:
        return
    
    # Update last activity
    st.session_state.last_activity = datetime.now()
    
    # Sidebar
    with st.sidebar:
        st.title("🏥 HMS")
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role.upper()}")
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        st.caption(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("System: Online ✅")
    
    # Route to appropriate dashboard
    if st.session_state.role == 'admin':
        admin_dashboard()
    elif st.session_state.role == 'doctor':
        doctor_dashboard()
    elif st.session_state.role == 'receptionist':
        receptionist_dashboard()


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    main()