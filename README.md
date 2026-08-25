# RC4 Stream Cipher File Encryptor & Decryptor

This is an educational implementation of the RC4 symmetric stream cipher in Python, comprising two separate scripts which are intended to encrypt and decrypt the contents of a local file by carrying out the processing in binary mode.

## Project Structure

The program `rc4Encrypt.py` reads the file `file.txt`, encrypts the data in it using RC4, and then replaces the original file with the binary ciphertext.
The program `rc4Decryptor.py` decrypts the file named `file.txt` by inverting the RC4 keystream and thus retrieves the original plaintext.

## How It Works

RC4 uses a symmetric key stream generated via two main components:
1. **Key Scheduling Algorithm (KSA):** The algorithm sets up a 256-byte array of permuted states using the secret key.
2. **Pseudo-Random Generation Algorithm (PRGA):** It produces a stream of bytes one after another, which is then XORed with the data in the file.

Since the XOR operation is identical to its inverse, encrypting the data once with the same stream sequence will exactly recover the original text.

## Usage Instructions

### 1. Preparation
In the same directory as the scripts make a target file called file.txt and put some sample text into it.

### 2. Encryption
Run the encryptor script from your terminal:
```bash
python rc4Encrypt.py
```
*Verification:* When you use the command `cat file.txt` to view the contents of `file.txt`, it will now show unreadable binary characters.

### 3. Decryption
Run the decryptor script to reverse the process:
```bash
python rc4Decryptor.py
```
*Verification:* On rechecking file.txt your original plain text will be found perfectly restored.

## Security Disclaimer
The repository has been set up entirely for academic and educational use. RC4 is known to have cryptographic flaws and includes identified vulnerabilities in its keystream. It should not be used in production environments or in modern secure communication systems.
