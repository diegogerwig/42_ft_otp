#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import argparse
import sys
import time
import struct
import hmac
import hashlib
import re
from cryptography.fernet import Fernet


load_dotenv()

env_key = os.getenv("OTP_SECRET_KEY")
if not env_key:
    print("❌ Error: OTP_SECRET_KEY is missing or empty in file .env")
    sys.exit(1)

LOCAL_ENCRYPTION_KEY = env_key.encode('utf-8')

def is_valid_hex(s):
    is_long_enough = len(s) >= 64
    is_hex = bool(re.fullmatch(r'[0-9a-fA-F]+', s))
    is_valid = is_long_enough and is_hex
    return is_valid

def save_key(filename):
    """Option -g: Saves the hexadecimal key securely encrypted."""
    try:
        with open(filename, 'r') as f:
            hex_key = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found.")
        sys.exit(1)

    if not is_valid_hex(hex_key):
        print("❌ Error: key must be 64 hexadecimal characters.")
        sys.exit(1)

    # Encrypt the key
    cipher_suite = Fernet(LOCAL_ENCRYPTION_KEY)
    encrypted_key = cipher_suite.encrypt(hex_key.encode('utf-8'))

    # Save it securely
    try:
        with open("ft_otp.key", "wb") as f:
            f.write(encrypted_key)
        print("Key was successfully saved in ft_otp.key.")
    except IOError:
        print("❌ Error: could not save ft_otp.key.")
        sys.exit(1)

def generate_totp(key_filename):
    """Option -k: Decrypts the key and generates the TOTP."""
    try:
        with open(key_filename, 'rb') as f:
            encrypted_key = f.read()
    except FileNotFoundError:
        print(f"❌ Error: {key_filename} not found.")
        sys.exit(1)

    try:
        cipher_suite = Fernet(LOCAL_ENCRYPTION_KEY)
        decrypted_hex_key = cipher_suite.decrypt(encrypted_key).decode('utf-8')
    except Exception:
        print("❌ Error: ft_otp.key file is corrupted or key is invalid.")
        sys.exit(1)

    try:
        key_bytes = bytes.fromhex(decrypted_hex_key)
    except ValueError:
        print("❌ Error: invalid hexadecimal format in decrypted file.")
        sys.exit(1)

    # TOTP Algorithm (RFC 6238 based on RFC 4226)
    # 1. Get the current time and calculate T0 (every 30 seconds)
    current_time = int(time.time())
    time_step = current_time // 30

    # 2. Pack the counter into 8 bytes (Big-Endian)
    msg = struct.pack('>Q', time_step)

    # 3. Calculate HMAC-SHA1
    hmac_hash = hmac.new(key_bytes, msg, hashlib.sha1).digest()

    # 4. Dynamic Truncation (RFC 4226)
    offset = hmac_hash[-1] & 0x0f
    # Unpack 4 bytes starting at the offset and apply mask to discard the sign bit
    binary_code = struct.unpack_from('>I', hmac_hash, offset)[0] & 0x7fffffff

    # 5. Get the 6 digits
    otp = binary_code % 1000000
    print(f"{otp:06d}")

def main():
    parser = argparse.ArgumentParser(description="Time-based One-Time Password generator", add_help=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', metavar='FILE', help="Securely saves the hexadecimal key.")
    group.add_argument('-k', metavar='KEY_FILE', help="Generates the temporary OTP from the saved file.")

    try:
        args = parser.parse_args()
    except SystemExit:
        # Silence long errors and output a generic one if invalid arguments are provided
        print("❌ Error: please check the provided arguments.")
        sys.exit(1)

    if args.g:
        save_key(args.g)
    elif args.k:
        generate_totp(args.k)

if __name__ == "__main__":
    main()