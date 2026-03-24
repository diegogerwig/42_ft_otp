#!/usr/bin/env python3
import subprocess
import sys
import time
from datetime import datetime

GREEN = '\033[1;32m'
CYAN = '\033[1;36m'
RED = '\033[1;31m'
YELLOW = '\033[1;33m'
RESET = '\033[0m'

def main():
    # 1. Read the content of key.hex once at the start
    try:
        with open('key.hex', 'r') as f:
            hex_key = f.read().strip()
    except FileNotFoundError:
        print(f"{RED}Error: 'key.hex' file not found.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Starting continuous tester. A new block will appear every 30s.{RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop.{RESET}\n")

    try:
        while True:
            # Determine the current 30-second window
            current_time = int(time.time())
            current_window = current_time // 30
            
            # Get current timestamp for logging
            timestamp = datetime.now().strftime('%H:%M:%S')

            # 2. Execute oathtool
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

            # 3. Execute your ft_otp script using Python explicitly
            try:
                ft_otp_process = subprocess.run(
                    ['python3', 'ft_otp.py', '-k', 'ft_otp.key'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                ft_otp_output = ft_otp_process.stdout.strip()
            except FileNotFoundError:
                print(f"\n{RED}Error: 'ft_otp.py' not found.{RESET}")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"\n{RED}Error running ft_otp: {e.stderr.strip()}{RESET}")
                sys.exit(1)

            # 4. Print the output block for the history log
            print(f"{YELLOW}--- FT_OTP TESTER [{timestamp}] ---{RESET}")
            print(f"Oathtool:  {GREEN}{oathtool_output}{RESET}")
            print(f"My ft_otp: {CYAN}{ft_otp_output}{RESET}")

            # Automatic validation
            if oathtool_output == ft_otp_output:
                print(f"Status: ✅ {GREEN}Perfect. The codes match.{RESET}")
            else:
                print(f"Status: ❌ {RED}Discrepancy detected. Please check your algorithm.{RESET}")

            # 5. Live countdown loop on the same line
            while True:
                now = int(time.time())
                window = now // 30
                
                # If we entered a new 30-second window, break the loop to generate new codes
                if window != current_window:
                    break
                
                # Adjusted to countdown to 00s instead of 01s
                remaining_seconds = 29 - (now % 30)
                time_color = RED if remaining_seconds <= 5 else CYAN
                
                # \r moves cursor to start of line, \033[K clears the line from cursor to end
                print(f"\r\033[K⏳ This code is valid for: {time_color}{remaining_seconds:02d}s{RESET}", end="", flush=True)
                
                # Sleep briefly to keep the terminal responsive and accurate
                time.sleep(0.1)
            
            # Print a double newline before starting the next block in history
            print("\n\n", end="")

    except KeyboardInterrupt:
        # Gracefully handle the user pressing Ctrl+C
        print(f"\n\n{YELLOW}Tester stopped by user. Goodbye!{RESET}")
        sys.exit(0)

if __name__ == '__main__':
    main()