#!/usr/bin/env python3
import subprocess
import sys
import os

# ANSI color definitions for terminal output
GREEN = '\033[1;32m'
CYAN = '\033[1;36m'
RED = '\033[1;31m'
RESET = '\033[0m'

def main():
    # 1. Read the content of key.hex
    try:
        with open('key.hex', 'r') as f:
            hex_key = f.read().strip()
    except FileNotFoundError:
        print(f"{RED}Error: 'key.hex' file not found.{RESET}")
        sys.exit(1)

    # 2. Execute oathtool
    try:
        # Note: Some versions of oathtool use -totp while others use --totp. 
        # If you get a syntax error, change '--totp' to '-totp'.
        oathtool_process = subprocess.run(
            ['oathtool', '--totp', hex_key],
            capture_output=True,
            text=True,
            check=True
        )
        oathtool_output = oathtool_process.stdout.strip()
    except FileNotFoundError:
        print(f"{RED}Error: 'oathtool' is not installed or not in your PATH.{RESET}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error running oathtool: {e.stderr.strip()}{RESET}")
        sys.exit(1)

    # 3. Execute your ft_otp script
    try:
        # We run ./ft_otp. Ensure it has execution permissions (chmod +x ft_otp)
        ft_otp_process = subprocess.run(
            ['./ft_otp', '-k', 'ft_otp.key'],
            capture_output=True,
            text=True,
            check=True
        )
        ft_otp_output = ft_otp_process.stdout.strip()
    except FileNotFoundError:
        print(f"{RED}Error: './ft_otp' not found.{RESET}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error running ft_otp: {e.stderr.strip()}{RESET}")
        sys.exit(1)

    # 4. Print the result side-by-side
    print(f"Oathtool: {GREEN}{oathtool_output}{RESET} | My ft_otp: {CYAN}{ft_otp_output}{RESET}")

    # 5. Automatic validation
    if oathtool_output == ft_otp_output:
        print(f"✅ {GREEN}Perfect. The codes match.{RESET}")
    else:
        print(f"❌ {RED}Discrepancy detected. Please check your algorithm.{RESET}")

if __name__ == '__main__':
    main()