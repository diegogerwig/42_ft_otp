#!/usr/bin/env python3
import argparse
import sys
import time
import struct
import hmac
import hashlib
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the master password from the environment
env_password = os.getenv("MASTER_PASSWORD")
if not env_password:
    print("❌ Error: MASTER_PASSWORD is missing or empty in the .env file.")
    sys.exit(1)

# Encode to bytes for the hashing function
MASTER_PASSWORD = env_password.encode('utf-8')

def custom_xor_cipher(data_bytes):
    """
    Encrypts or decrypts a byte stream using the XOR operation.
    Since XOR is reversible, the same function works for both processes.
    """
    # Step 1: Create a secure 32-byte base key using SHA-256
    base_key = hashlib.sha256(MASTER_PASSWORD).digest()
    key_length = len(base_key)
    
    # Step 2: Create an empty array to store the final encrypted/decrypted bytes
    result = bytearray()
    
    # Step 3: Loop through each byte of the data we want to encrypt/decrypt
    for i in range(len(data_bytes)):
        
        # Step 4: Get the current byte from the data
        current_data_byte = data_bytes[i]
        
        # Step 5: Get the corresponding byte from the key.
        # We use modulo (%) so if the data is longer than 32 bytes, 
        # the key simply starts over from the beginning (0, 1, 2... 31, 0, 1...)
        current_key_byte = base_key[i % key_length]
        
        # Step 6: Apply the XOR operation (^) between the data byte and the key byte
        xored_byte = current_data_byte ^ current_key_byte
        
        # Step 7: Add the result to our final array
        result.append(xored_byte)
        
    # Step 8: Return the final array as an immutable bytes object
    return bytes(result)

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

    encrypted_key = custom_xor_cipher(hex_key.encode('utf-8'))

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
        decrypted_hex_key = custom_xor_cipher(encrypted_key).decode('utf-8')
    except Exception:
        print("❌ Error: ft_otp.key file is corrupted or key is invalid.")
        sys.exit(1)

    try:
        key_bytes = bytes.fromhex(decrypted_hex_key)
    except ValueError:
        print("❌ Error: invalid hexadecimal format in decrypted file.")
        sys.exit(1)

    # TOTP Algorithm (based on RFC 4226)
    
    # --- 1. TIME FACTOR ---
    # Get the current time in seconds and calculate the 30-second time window.
    current_time = int(time.time())
    time_step = current_time // 30

    # --- 2. PACKING ---
    # Pack the time_step into an 8-byte format (Big-Endian) required by the hash algorithm.
    msg = struct.pack('>Q', time_step)

    # --- 3. HMAC-SHA1 GENERATION ---
    # Create the HMAC using the secret key, the time message, and the SHA1 algorithm.
    hmac_obj = hmac.new(key_bytes, msg, hashlib.sha1)
    hmac_hash = hmac_obj.digest()  # This returns exactly 20 bytes.

    # --- 4. DYNAMIC TRUNCATION ---
    # Step A: Get the very last byte of the 20-byte hash.
    last_byte = hmac_hash[-1]
    
    # Step B: Apply a mask (0x0f) to isolate the last 4 bits. 
    # This gives us an offset index ranging from 0 to 15.
    offset = last_byte & 0x0f

    # Step C: Use the offset to extract exactly 4 bytes from the hash. 
    # '>I' reads these bytes as an unsigned integer in Big-Endian format.
    extracted_bytes = struct.unpack_from('>I', hmac_hash, offset)
    raw_number = extracted_bytes[0]

    # Step D: Apply the 0x7fffffff mask to discard the sign bit.
    # This ensures the resulting number is always positive.
    positive_number = raw_number & 0x7fffffff

    # Step E: Use the modulo operator (%) to keep only the last 6 digits.
    otp_number = positive_number % 1000000

    # --- 5. FINAL OUTPUT ---
    # Print the OTP, padding with leading zeros if it is shorter than 6 digits (e.g., 004521).
    print(f"{otp_number:06d}")

def main():
    parser = argparse.ArgumentParser(description="Time-based One-Time Password generator", add_help=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', metavar='FILE', help="Securely saves the hexadecimal key.")
    group.add_argument('-k', metavar='KEY_FILE', help="Generates the temporary OTP from the saved file.")

    try:
        args = parser.parse_args()
    except SystemExit:
        print("❌ Error: please check the provided arguments.")
        sys.exit(1)

    if args.g:
        save_key(args.g)
    elif args.k:
        generate_totp(args.k)

if __name__ == "__main__":
    main()