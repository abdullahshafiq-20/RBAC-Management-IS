import hashlib
import bcrypt
from cryptography.fernet import Fernet
import re
from datetime import datetime, timedelta
import secrets
import base64

# =====================================================
# ENCRYPTION KEY MANAGEMENT
# =====================================================

class EncryptionManager:
    """Manages Fernet encryption for reversible data protection"""
    
    def __init__(self, key=None):
        """
        Initialize encryption manager
        key: Optional encryption key (base64 encoded). If None, generates new key.
        """
        if key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = key if isinstance(key, bytes) else key.encode()
        self.cipher = Fernet(self.key)
    
    def get_key(self):
        """Return the encryption key (store this securely!)"""
        return self.key.decode()
    
    def encrypt(self, plaintext):
        """Encrypt plaintext string"""
        if plaintext is None or plaintext == "":
            return None
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext):
        """Decrypt ciphertext string"""
        if ciphertext is None or ciphertext == "":
            return None
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None


# =====================================================
# PASSWORD HASHING (One-way, for authentication)
# =====================================================

def hash_password(password):
    """
    Hash password using bcrypt (one-way encryption)
    Returns: Hashed password as string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """
    Verify password against hashed version
    Returns: Boolean (True if match)
    """
    try:
        # Ensure password is bytes
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        # Ensure hashed_password is bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        print(f"Password bytes: {password}")
        print(f"Hash bytes: {hashed_password}")
        
        result = bcrypt.checkpw(password, hashed_password)
        print(f"bcrypt.checkpw result: {result}")
        return result
        
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


# =====================================================
# DATA ANONYMIZATION / MASKING
# =====================================================

def anonymize_name(name, patient_id=None):
    """
    Anonymize patient name
    Example: "John Doe" -> "ANON_1021"
    """
    if not name:
        return None
    
    if patient_id:
        return f"ANON_{patient_id:04d}"
    else:
        # Use hash-based anonymization if no ID
        hash_val = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"ANON_{hash_val.upper()}"


def mask_contact(contact):
    """
    Mask phone number
    Example: "+923001234567" -> "XXX-XXX-4567"
    """
    if not contact:
        return None
    
    # Extract last 4 digits
    digits = re.sub(r'\D', '', contact)  # Remove non-digits
    if len(digits) >= 4:
        last_four = digits[-4:]
        return f"XXX-XXX-{last_four}"
    return "XXX-XXX-XXXX"


def mask_email(email):
    """
    Mask email address
    Example: "john.doe@email.com" -> "j***@email.com"
    """
    if not email or '@' not in email:
        return None
    
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]
    
    if len(username) <= 2:
        masked_username = username[0] + '*'
    else:
        masked_username = username[0] + '*' * (len(username) - 1)
    
    return f"{masked_username}@{domain}"


def anonymize_address(address):
    """
    Anonymize address (keep only city/general area)
    Example: "123 Main St, Karachi" -> "*****, Karachi"
    """
    if not address:
        return None
    
    # Try to extract city (last part after comma)
    parts = address.split(',')
    if len(parts) > 1:
        city = parts[-1].strip()
        return f"*****, {city}"
    return "*****"


# =====================================================
# DATA MASKING UTILITIES
# =====================================================

def mask_diagnosis(diagnosis, mask_level='partial'):
    """
    Mask diagnosis information
    mask_level: 'full' or 'partial'
    """
    if not diagnosis:
        return None
    
    if mask_level == 'full':
        return "***CONFIDENTIAL***"
    else:
        # Partial masking - show only first word
        words = diagnosis.split()
        if len(words) > 1:
            return f"{words[0]} ***"
        return diagnosis


def generate_anonymous_id(prefix="PATIENT"):
    """Generate random anonymous identifier"""
    random_suffix = secrets.token_hex(4).upper()
    return f"{prefix}_{random_suffix}"


# =====================================================
# DATA VALIDATION
# =====================================================

def validate_contact(contact):
    """Validate phone number format"""
    if not contact:
        return False
    # Pattern: +country_code followed by 10-15 digits
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, contact))


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text, max_length=500):
    """
    Sanitize user input to prevent injection attacks
    Removes special SQL characters
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\'"\\]', '', str(text))
    return sanitized[:max_length]


# =====================================================
# GDPR UTILITIES
# =====================================================

def calculate_retention_date(days=365):
    """
    Calculate data retention date (GDPR compliance)
    Default: 1 year from now
    """
    return datetime.now() + timedelta(days=days)


def check_retention_expired(retention_date):
    """Check if data retention period has expired"""
    if not retention_date:
        return False
    
    if isinstance(retention_date, str):
        retention_date = datetime.strptime(retention_date, '%Y-%m-%d')
    
    return datetime.now() > retention_date


def generate_consent_id():
    """Generate unique consent tracking ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(4).upper()
    return f"CONSENT_{timestamp}_{random_part}"


# =====================================================
# LOGGING UTILITIES
# =====================================================

def format_log_message(user, action, details, patient_id=None):
    """Format consistent log message"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[{timestamp}] User: {user} | Action: {action}"
    
    if patient_id:
        msg += f" | Patient: {patient_id}"
    
    if details:
        msg += f" | Details: {details}"
    
    return msg


def get_client_ip():
    """Get client IP address (for web apps)"""
    # This is a placeholder - actual implementation depends on deployment
    return "127.0.0.1"


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def generate_patient_report_filename(patient_id, anonymized=False):
    """Generate standardized filename for patient reports"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if anonymized:
        return f"patient_report_ANON_{patient_id}_{timestamp}.pdf"
    else:
        return f"patient_report_{patient_id}_{timestamp}.pdf"


def format_timestamp(dt=None):
    """Format timestamp for display"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def mask_sensitive_data(data_dict, role):
    """
    Mask sensitive data based on user role
    data_dict: Dictionary containing patient data
    role: User role ('admin', 'doctor', 'receptionist')
    """
    if role == 'admin':
        return data_dict  # Admin sees everything
    
    masked = data_dict.copy()
    
    if role == 'doctor':
        # Doctors see anonymized data
        if 'name' in masked:
            masked['name'] = masked.get('anonymized_name', anonymize_name(masked['name']))
        if 'contact' in masked:
            masked['contact'] = mask_contact(masked['contact'])
        if 'email' in masked:
            masked['email'] = mask_email(masked['email'])
    
    elif role == 'receptionist':
        # Receptionists cannot see diagnosis
        if 'diagnosis' in masked:
            masked['diagnosis'] = '***RESTRICTED***'
        if 'address' in masked:
            masked['address'] = anonymize_address(masked['address'])
    
    return masked


# =====================================================
# TESTING FUNCTIONS (for development)
# =====================================================

def test_encryption():
    """Test encryption/decryption"""
    print("=== Testing Encryption ===")
    em = EncryptionManager()
    print(f"Generated Key: {em.get_key()}")
    
    original = "Sensitive Patient Data"
    encrypted = em.encrypt(original)
    decrypted = em.decrypt(encrypted)
    
    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}\n")


def test_password_hashing():
    """Test password hashing"""
    print("=== Testing Password Hashing ===")
    password = "admin123"
    hashed = hash_password(password)
    
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification (correct): {verify_password(password, hashed)}")
    print(f"Verification (wrong): {verify_password('wrong', hashed)}\n")


def test_anonymization():
    """Test data anonymization"""
    print("=== Testing Anonymization ===")
    
    name = "John Doe"
    contact = "+923001234567"
    email = "john.doe@email.com"
    
    print(f"Original Name: {name}")
    print(f"Anonymized: {anonymize_name(name, 1021)}")
    
    print(f"\nOriginal Contact: {contact}")
    print(f"Masked: {mask_contact(contact)}")
    
    print(f"\nOriginal Email: {email}")
    print(f"Masked: {mask_email(email)}\n")


# Run tests if executed directly
if __name__ == "__main__":
    test_encryption()
    test_password_hashing()
    test_anonymization()
    
    print("=== All tests completed ===")
    print("\nIMPORTANT: Store the encryption key securely!")
    print("For production, use environment variables or secure key management.")