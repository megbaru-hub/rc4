# RC4 Stream Cipher File Encryptor & Decryptor

In this project, I implemented the RC4 symmetric stream cipher in both Python and C. It allows encrypting and decrypting arbitrary files in binary mode with full data integrity.

## Project Structure

- `rc4Encrypt.py` / `rc4Encryptor.py`: Python implementation of the RC4 file encryptor.
- `rc4Decryptor.py`: Python implementation of the RC4 file decryptor.
- `rc4_encrypt.c`: Standalone C implementation of the RC4 encryptor.
- `rc4_decrypt.c`: Standalone C implementation of the RC4 decryptor.
- `rc4_gui.py`: Full graphical user interface suite for visual testing.
- `rc4_decrypt_prompt.py`: Quick password-prompt decrypter for opening locked media files (.png, .pdf, .mp4, etc.).
- `file.txt`: Sample test file.
- `Makefile`: Build and test automation.
- `verify.sh`: Comprehensive automated test suite.

## How It Works

RC4 uses a symmetric keystream generated through two main components:
1. **Key Scheduling Algorithm (KSA):** Initializes and permutes a 256-byte state array `S` based on the secret key.
2. **Pseudo-Random Generation Algorithm (PRGA):** Continuously generates a pseudo-random keystream XORed byte-by-byte with the plaintext.

Because XOR is self-inverting ($(\text{Plaintext} \oplus K) \oplus K = \text{Plaintext}$), encrypting the ciphertext with the identical key restores the original plaintext.

## How to Build and Run

### 1. Automated Verification Suite
I wrote an 8-stage automated test suite to verify the correctness of both my Python and C implementations:
```bash
make test
# or directly:
./verify.sh
```

Tests included in the suite:
- Python encryption & decryption roundtrip integrity
- Native C binary encryption & decryption roundtrip
- Cross-compatibility (encrypt with Python &harr; decrypt with C)
- Random binary file payload handling
- Key-specificity validation

### 2. Building Native Binaries
I created a `Makefile` to simplify compilation and testing:
```bash
make            # Compiles rc4Encryptor and rc4Decryptor
make test       # Runs the full verification suite
make gui        # Launches the graphical user interface
make clean      # Cleans compiled binaries
```

### 3. Manual Command-Line Usage
**Running the Python scripts:**
```bash
./rc4Encrypt.py     # Encrypt file.txt
./rc4Decryptor.py   # Decrypt file.txt
```

**Running the native C executables:**
```bash
./rc4Encryptor [file_path] [custom_key]
./rc4Decryptor [file_path] [custom_key]
```

### 4. Graphical Interface (GUI) & File Unlocker
**Main GUI Suite:**
```bash
python3 rc4_gui.py
# or
make gui
```

**Direct File Unlocker Prompt (Double-click or CLI):**
```bash
python3 rc4_decrypt_prompt.py <path_to_encrypted_file>
```
When encrypting photos, videos, or PDFs with the `.rc4` extension, opening the locked file prompts for the secret key, decrypts it, and automatically opens it in the default system viewer.

## Security Note
This project was developed for educational purposes to study stream cipher mechanics. RC4 contains known cryptographic weaknesses and should not be used in modern production systems.
