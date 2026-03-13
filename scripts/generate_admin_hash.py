#!/usr/bin/env python3
"""
scripts/generate_admin_hash.py
─────────────────────────────
Utility for the DB Team to generate a bcrypt password hash
suitable for inserting into the admins table or V2 seed migration.

Usage:
    python3 scripts/generate_admin_hash.py
    python3 scripts/generate_admin_hash.py --password MySecurePass1
"""
import argparse
import getpass
import sys

try:
    from passlib.context import CryptContext
except ImportError:
    print("ERROR: passlib not installed. Run: pip install passlib[bcrypt]")
    sys.exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_hash(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def main():
    parser = argparse.ArgumentParser(description="Generate bcrypt password hash")
    parser.add_argument("--password", "-p", help="Password to hash (prompted if not given)")
    parser.add_argument("--verify",   "-v", help="Hash to verify against")
    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password to hash: ")
        confirm  = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("ERROR: Passwords do not match.")
            sys.exit(1)

    hashed = generate_hash(password)

    print("\n─────────────────────────────────────────────")
    print(f"  Password : {password}")
    print(f"  Hash     : {hashed}")
    print("─────────────────────────────────────────────")
    print("\nSQL snippet for V2 seed migration:")
    print(f"  UPDATE admins SET hashed_password = '{hashed}' WHERE email = 'admin@sapsecops.in';")
    print()

    if args.verify:
        ok = verify_hash(password, args.verify)
        print(f"  Verify against provided hash: {'✅ MATCH' if ok else '❌ NO MATCH'}")


if __name__ == "__main__":
    main()
