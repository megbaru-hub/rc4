#!/usr/bin/env python3
# Key scheduling algorithm 
def ksa(key: bytes) -> list:

    kLength = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % kLength]) % 256
        S[i], S[j] = S[j], S[i]
    return S

# pseudo random generation algorithm
def prga(S: list, data: bytes) -> bytes:
    S = S.copy()
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream_byte = S[(S[i] + S[j]) % 256]
        out.append(byte ^ keystream_byte)
    return bytes(out)

"""File Handling  I put the file variable instead of the actual file path or actual file mean file.txt cause python case an error due to the pyhton def rule it only use letter underscore number  only""" 
def encrypt_file(file: str, key: bytes):
    try:
        #  Open the file in binary mode and read into memory buffer
        with open(file, 'rb') as f:
            plaintext = f.read()

        # Encrypt the bytes using RC4
        ciphertext = prga(ksa(key), plaintext)

        # Write the encrypted bytes back to the file
        with open(file, 'wb') as f:
            f.write(ciphertext)

        print(f"[+] Successfully encrypted {file}")
    except FileNotFoundError:
        print(f"[-] Error: {file} not found.")

if __name__ == "__main__":
    import os
    import sys
    # Define a secret key (must be in bytes)
    KEY = b"backtohomebutstillmissthesummercamp#INSA#AASTU2018E.C"
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file.txt")
    target = sys.argv[1] if len(sys.argv) > 1 else default_path
    key = sys.argv[2].encode() if len(sys.argv) > 2 else KEY
    encrypt_file(target, key)
