import bcrypt

password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(f"Correct hash for 'admin123':")
print(hashed.decode('utf-8'))

# Verify it works
test = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"\nVerification test: {test}")