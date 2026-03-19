import sys
import os

print("--- 1. Starting test ---")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("--- 2. Importing codex.protocol_keygen ---")
try:
    import codex.protocol_keygen
    print("--- 3. Import codex.protocol_keygen OK ---")
except Exception as e:
    print(f"--- 3. Import error: {e}")

print("--- 4. Getting function references ---")
create_temp_email = codex.protocol_keygen.create_temp_email
create_session = codex.protocol_keygen.create_session
register_one = codex.protocol_keygen.register_one

print("--- 5. Calling create_session ---")
session = create_session()

print("--- 6. Calling create_temp_email ---")
email, tk = create_temp_email(session)
print(f"Got email: {email}")

print("--- 7. Calling register_one(0, 0, 1) ---")
try:
    register_one(0, 0, 1)
except Exception as e:
    print(e)
print("--- 8. Done ---")
