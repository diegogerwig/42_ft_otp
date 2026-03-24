# ft_otp

A time-based one-time password (TOTP) generator built for the 42 School curriculum. Encrypts and stores a secret key locally, then generates RFC 6238-compliant OTP codes compatible with tools like Google Authenticator.

---

## Setup

```bash
bash setup.sh
```

Detects your OS (Linux 42 Campus, WSL, or other), creates a virtual environment in the right place, and installs dependencies. To start fresh:

```bash
bash setup.sh clean
```

Manual setup if you prefer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

Generar clave con:
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


## ft_otp.py

Saves a hexadecimal secret key encrypted on disk, then uses it to generate TOTP codes on demand.


```
./ft_otp.py -g FILE
./ft_otp.py -k KEY_FILE
```

| Flag | Argument | Description |
|---|---|---|
| `-g` | `FILE` | Reads a hex key from `FILE`, encrypts it, and saves it to `ft_otp.key` |
| `-k` | `KEY_FILE` | Decrypts the key from `KEY_FILE` and prints the current 6-digit OTP |

```bash
./ft_otp.py -g key.hex
./ft_otp.py -k ft_otp.key
```

The key file must contain at least 64 hexadecimal characters. The encrypted key is stored in `ft_otp.key` using Fernet symmetric encryption.

The OTP is generated following the TOTP algorithm (RFC 6238):

1. Compute the time step — current Unix time divided by 30
2. Pack it as an 8-byte big-endian counter
3. Compute HMAC-SHA1 of the counter using the secret key
4. Apply dynamic truncation to extract a 4-byte value
5. Take the result modulo 1 000 000 for a 6-digit code

---

## tester.py

Runs a continuous side-by-side comparison between `ft_otp.py` and `oathtool` to verify correctness. Requires `oathtool` to be installed.

```bash
python3 tester.py
```

On each 30-second window it shows both codes, marks them as matching or not, and displays a live countdown until the next rotation. Press `Ctrl+C` to stop.

```bash
# Install oathtool (macOS)
brew install oath-toolkit

# Manually verify a single code against oathtool
oathtool --totp $(cat key.hex)
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `cryptography` | Fernet encryption for local key storage |