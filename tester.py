#!/usr/bin/env python3
import subprocess
import sys
import time
import os
from datetime import datetime

GREEN = '\033[1;32m'
CYAN = '\033[1;36m'
RED = '\033[1;31m'
YELLOW = '\033[1;33m'
MAGENTA = '\033[1;35m'
RESET = '\033[0m'

def main():
    try:
        with open('key.hex', 'r') as f:
            hex_key = f.read().strip()
    except FileNotFoundError:
        print(f"{RED}Error: 'key.hex' file not found. Oathtool needs this to generate the reference code.{RESET}")
        sys.exit(1)

    if not os.path.exists('ft_otp.key'):
        print(f"{RED}Error: 'ft_otp.key' not found. Please run 'python3 ft_otp.py -g key.hex' first.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Starting continuous tester. A new block will appear every 30s.{RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop.{RESET}\n")

    while int(time.time()) % 30 in [0, 29]:
        time.sleep(0.5)

    try:
        while True:
            current_time = int(time.time())
            current_window = current_time // 30
            
            timestamp = datetime.now().strftime('%H:%M:%S')

            # Execute oathtool
            try:
                oathtool_process = subprocess.run(
                    ['oathtool', '--totp', hex_key],
                    capture_output=True,
                    text=True,
                    check=True
                )
                oathtool_output = oathtool_process.stdout.strip()
            except FileNotFoundError:
                print(f"\n{RED}Error: 'oathtool' is not installed or not in your PATH.{RESET}")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"\n{RED}Error running oathtool: {e.stderr.strip()}{RESET}")
                sys.exit(1)

            # Execute your ft_otp script
            try:
                ft_otp_process = subprocess.run(
                    ['python3', 'ft_otp.py', '-k', 'ft_otp.key'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                ft_otp_output = ft_otp_process.stdout.strip()
            except FileNotFoundError:
                print(f"\n{RED}Error: 'ft_otp.py' not found or 'python3' is not in PATH.{RESET}")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() or e.stdout.strip()
                print(f"\n{RED}Error running ft_otp: {error_msg}{RESET}")
                sys.exit(1)

            print(f"{YELLOW}--- FT_OTP TESTER [{timestamp}] ---{RESET}")
            print(f"Oathtool:  {MAGENTA}{oathtool_output}{RESET}")
            print(f"My ft_otp: {CYAN}{ft_otp_output}{RESET}")

            if oathtool_output == ft_otp_output:
                print(f"Status: ✅ {GREEN}Perfect. The codes match.{RESET}")
            else:
                print(f"Status: ❌ {RED}Discrepancy detected. Please check your algorithm.{RESET}")

            # 5. Live countdown loop
            while True:
                now = int(time.time())
                window = now // 30
                
                if window != current_window:
                    # Force the display to hold at 00s when the window finishes
                    print(f"\r\033[K⏳ This code is valid for: {RED}00s{RESET}", end="", flush=True)
                    # Wait 0.5s to ensure we are safely inside the new window (prevents race conditions)
                    time.sleep(0.5)
                    break
                
                # Standard authenticator countdown (from 30 down to 1)
                remaining_seconds = 30 - (now % 30)
                time_color = RED if remaining_seconds <= 5 else CYAN
                
                print(f"\r\033[K⏳ This code is valid for: {time_color}{remaining_seconds:02d}s{RESET}", end="", flush=True)
                
                time.sleep(0.1)
            
            print("\n\n", end="")

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tester stopped by user.{RESET}")
        sys.exit(0)

if __name__ == '__main__':
    main()