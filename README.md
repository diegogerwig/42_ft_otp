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

## Quickstart

Complete flow from scratch to your first OTP code:

**1. Configure your master password**

Create a `.env` file in the project root with your master password:

```bash
echo "MASTER_PASSWORD=your_password_here" > .env
```

This password is used to derive the encryption key that protects `ft_otp.key` at rest.

**2. Generate a hex secret key**

A valid `key.hex` must contain at least 64 hexadecimal characters. You can create one with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))" > key.hex
```

Or write your own directly into `key.hex`.

**3. Encrypt and save the key**

```bash
python3 ft_otp.py -g key.hex
# → Key was successfully saved in ft_otp.key.
```

This reads `key.hex`, encrypts its contents using XOR with a key derived from `MASTER_PASSWORD`, and writes the result to `ft_otp.key`.

**4. Generate a TOTP code**

```bash
python3 ft_otp.py -k ft_otp.key
# → 048271
```

**5. Verify against oathtool (optional)**

```bash
oathtool --totp $(cat key.hex)
```

Both outputs should match within the same 30-second window.

---

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

The key file must contain at least 64 hexadecimal characters. The encrypted key is stored in `ft_otp.key` using a XOR cipher with a SHA-256 derived key from `MASTER_PASSWORD`.

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
| `python-dotenv` | Loads `MASTER_PASSWORD` from the `.env` file |